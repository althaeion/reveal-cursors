#!/usr/bin/env bash
# Builds dist/swarm-cursors.zip, the file to attach to a GitHub release
# and to upload in Claude (the zip's root folder is the skill folder).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
rm -f dist/swarm-cursors.zip
zip -r dist/swarm-cursors.zip swarm-cursors -x "*/__pycache__/*" "*.pyc" "*.DS_Store"
echo "built dist/swarm-cursors.zip"
