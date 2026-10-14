#!/usr/bin/env bash
# Checks node, ffmpeg, python on PATH; installs any that are missing, then re-checks.
# Exit 0 only if all three are available.
have() { command -v "$1" >/dev/null 2>&1; }
py() { have python && echo python || { have python3 && echo python3; } ; }
missing=()
have node   || missing+=(node)
have ffmpeg || missing+=(ffmpeg)
[ -n "$(py)" ] || missing+=(python)
if [ ${#missing[@]} -eq 0 ]; then echo "OK: node $(node -v), $(ffmpeg -version | head -1 | cut -d' ' -f1-3), $($(py) --version)"; exit 0; fi
echo "MISSING: ${missing[*]} -- installing"
os="$(uname -s)"
for m in "${missing[@]}"; do
  case "$os" in
    MINGW*|MSYS*|CYGWIN*)
      case $m in node) id=OpenJS.NodeJS.LTS;; ffmpeg) id=Gyan.FFmpeg;; python) id=Python.Python.3.12;; esac
      winget install -e --id "$id" --accept-source-agreements --accept-package-agreements ;;
    Darwin) case $m in node) brew install node;; ffmpeg) brew install ffmpeg;; python) brew install python;; esac ;;
    *) case $m in node) sudo apt-get install -y nodejs npm;; ffmpeg) sudo apt-get install -y ffmpeg;; python) sudo apt-get install -y python3 python3-pip;; esac ;;
  esac
done
echo "Installed. Open a NEW shell (PATH refresh) or add the install dirs to PATH, then re-run this script."
exit 1
