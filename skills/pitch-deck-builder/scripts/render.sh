#!/usr/bin/env bash
# Render a .pptx to PDF + one PNG per slide (96 dpi) + a contact sheet, so you can LOOK
# at every slide before reporting a design (Stage 6).
#
# Usage: scripts/render.sh deck.pptx [out_dir]
#   out_dir defaults to <deck>_render/ next to the deck.
# Needs: LibreOffice, pdftoppm (poppler), python3 with Pillow (for the contact sheet).
# Override the LibreOffice binary with SOFFICE=/path/to/soffice.
set -euo pipefail

deck="${1:?usage: render.sh deck.pptx [out_dir]}"
[ -f "$deck" ] || { echo "error: no such file: $deck" >&2; exit 2; }
out="${2:-${deck%.*}_render}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$out"

# Find a LibreOffice binary that really runs. A Homebrew `soffice` wrapper can survive
# after the app bundle was deleted and then exit 127, so test each candidate.
find_soffice() {
  local c
  for c in "${SOFFICE:-}" \
           /Applications/LibreOffice.app/Contents/MacOS/soffice \
           "$(command -v soffice 2>/dev/null || true)" \
           "$(command -v libreoffice 2>/dev/null || true)" \
           "/c/Program Files/LibreOffice/program/soffice.exe" \
           /usr/bin/soffice /usr/lib/libreoffice/program/soffice; do
    [ -n "$c" ] && [ -x "$c" ] && "$c" --version >/dev/null 2>&1 && { echo "$c"; return 0; }
  done
  return 1
}

if ! so="$(find_soffice)"; then
  cat >&2 <<'EOF'
error: no working LibreOffice found.
  macOS:   brew install --cask libreoffice   (if already "installed" but broken:
           brew reinstall --cask libreoffice)
  Linux:   sudo apt install libreoffice-impress
  Windows: install from libreoffice.org, then set SOFFICE to soffice.exe
No LibreOffice at all? Open the .pptx in PowerPoint/Keynote, export PDF, then run:
  pdftoppm -r 96 -png deck.pdf out/slide
EOF
  exit 3
fi
command -v pdftoppm >/dev/null || { echo "error: pdftoppm missing (brew install poppler / apt install poppler-utils)" >&2; exit 3; }

# A private profile, so a LibreOffice window that is already open can't block the headless run.
profile="$(mktemp -d)"
trap 'rm -rf "$profile"' EXIT

# Headless LibreOffice does not always see the OS font folders (seen on macOS: Georgia and
# Tahoma silently became LinuxLibertine / NotoSans, and Thai text vanished). Copy the font
# files the deck names into the profile's own font folder, where it always looks.
mkdir -p "$profile/user/fonts"
font_dirs="${FONT_DIRS:-$HOME/Library/Fonts:/Library/Fonts:/System/Library/Fonts/Supplemental:/System/Library/Fonts:/usr/share/fonts:$HOME/.fonts:$HOME/.local/share/fonts}"
copied=0
while IFS= read -r face; do
  [ -n "$face" ] || continue
  case "$face" in +*) continue ;; esac   # theme placeholders like +mn-lt
  IFS=':'
  for dir in $font_dirs; do
    [ -d "$dir" ] || continue
    while IFS= read -r f; do
      cp "$f" "$profile/user/fonts/" 2>/dev/null && copied=$((copied + 1))
    done < <(find "$dir" -maxdepth 3 -type f \( -iname "$face.tt[fc]" -o -iname "$face *.tt[fc]" \
             -o -iname "$face.otf" -o -iname "$face *.otf" -o -iname "${face// /}*.tt[fc]" \) 2>/dev/null)
  done
  unset IFS
done < <(unzip -p "$deck" 'ppt/slides/*.xml' 2>/dev/null | grep -o 'typeface="[^"]*"' | sed 's/typeface="//;s/"$//' | sort -u)
[ "$copied" -gt 0 ] && echo "fonts: made $copied font file(s) visible to LibreOffice"
"$so" -env:UserInstallation="file://$profile" --headless --convert-to pdf --outdir "$out" "$deck" >/dev/null 2>&1
pdf="$out/$(basename "${deck%.*}").pdf"
[ -s "$pdf" ] || { echo "error: PDF conversion produced nothing ($so)" >&2; exit 4; }

# Report font substitutions, so a preview with the wrong font is never taken as final.
if command -v pdffonts >/dev/null; then
  used="$(pdffonts "$pdf" 2>/dev/null | awk 'NR>2{print $1}' | sed 's/^[A-Z]*+//;s/[-,].*//' | sort -u | tr '\n' ' ')"
  echo "fonts in preview: $used"
fi

rm -f "$out"/slide-*.png
# 96 dpi on purpose: odd DPIs can draw a fake 1px line at the slide edge.
pdftoppm -r 96 -png "$pdf" "$out/slide"
n=$(ls "$out"/slide-*.png | wc -l | tr -d ' ')

py="${PYTHON:-python3}"
if "$py" -c "import PIL" 2>/dev/null; then
  "$py" "$here/contact_sheet.py" "$out" "$out/contact-sheet.png"
else
  echo "note: Pillow not found for $py, skipped contact sheet (set PYTHON=...)" >&2
fi
echo "rendered $n slides -> $out"
