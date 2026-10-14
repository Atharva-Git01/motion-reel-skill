#!/usr/bin/env bash
# One-time machine setup for the motion-reel skill (macOS, Linux, Git Bash on Windows).
# 1) node, ffmpeg, python on PATH (installs missing ones)  2) Python packages from requirements.txt
# Playwright + Chromium are installed per film project (SKILL.md step 0).
set -e
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/studio/check-prereqs.sh"
py=python; command -v python >/dev/null 2>&1 || py=python3
"$py" -m pip install -r "$here/requirements.txt"
echo "Setup done. Ask your agent for a motion reel; it follows SKILL.md."
