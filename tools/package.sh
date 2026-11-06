#!/usr/bin/env bash
# Build dist/pitch-deck-builder.zip for apps that install a skill by upload
# (claude.ai Settings -> Capabilities -> Skills; ChatGPT Skills). The ZIP holds one
# top-level folder, pitch-deck-builder/, with SKILL.md inside it.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$root/dist"
out="$root/dist/pitch-deck-builder.zip"
rm -f "$out"
cd "$root"
zip -qr "$out" pitch-deck-builder -x '*/__pycache__/*' '*.pyc' '*/.DS_Store'
echo "built $out ($(du -h "$out" | cut -f1))"
zipinfo -1 "$out" | sed 's/^/  /'
