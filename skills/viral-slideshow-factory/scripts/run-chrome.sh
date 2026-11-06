#!/bin/bash
# Runs one of this skill's browser scripts in real Google Chrome on a virtual screen.
# Cloud sessions need this: Social1 and ChatGPT turn away a hidden (headless) browser.
# Usage: run-chrome.sh <script.js> [args...]     e.g. run-chrome.sh social1_login.js --shot /tmp/s1.png
DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$1"; shift
HEADED=1 BROWSER_CHANNEL=chrome exec xvfb-run -a -s "-screen 0 1400x1000x24" node "$DIR/$SCRIPT" "$@"
