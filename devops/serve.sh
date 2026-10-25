#!/usr/bin/env bash
####################################################################################################################################
# serve.sh: Mount local source folder on Raspberry Pi Pico 2 for live development.
#
# Usage:    devops/serve.sh [--folder=src]
#
# Options:
#   --folder=src        Local folder to mount on the Pico (default: src)
#   --stop              Stop any running mpremote mount sessions
#   --help              Show this help message
#
# Description:
#   Uses mpremote to mount a local folder on the Pico, allowing live editing in VS Code.
#   Files are immediately accessible on the device without uploading.
#
####################################################################################################################################

# Exit immediately if a command exits with a non-zero status
set -o errexit
# Treat unset variables as an error when substituting
set -o nounset
# Fails entire pipeline if any command fails
set -euo pipefail
trap 'echo "Exit status $? at line $LINENO from: $BASH_COMMAND"' ERR

# Include the parseArgs function
source ./devops/includes/parseArgs.sh

# Usage docstring that is parsed by the parseArgs function. Edit with care.
USAGE="

Usage: serve.sh [--folder=src] [--stop]

Options:
  --folder=src          Local folder to mount on the Pico (default: src)
  --stop                Stop any running mpremote mount sessions
  --help                Show this help message
"

# Parse the command line arguments
parseArgs "$USAGE" "$@"

# Set default folder if not provided
folder="${folder:-src}"

if [[ "$stop" == "true" ]]; then
  echo "🛑 Stopping mpremote mount sessions..."
  pkill -f "mpremote.*mount" || echo "No mpremote processes found"
  exit 0
fi

# Check if mpremote is installed
if ! command -v mpremote &>/dev/null; then
  echo "❌ mpremote is not installed."
  echo "Install with: pip install mpremote"
  exit 1
fi

# Check if folder exists
if [[ ! -d "$folder" ]]; then
  echo "❌ Folder '$folder' does not exist"
  exit 1
fi

echo "🚀 Mounting folder '$folder' on Raspberry Pi Pico 2 with REPL..."
echo "📁 Files from '$folder' will be available at /remote/ on the Pico"
echo "✏️  Changes in VS Code are immediately visible on the device"
echo ""
echo "💡 Interactive Development Mode:"
echo "   1. Edit files in VS Code"
echo "   2. In the REPL below, run:"
echo ""
echo "      exec(open('/remote/main.py').read())"
echo ""
echo "   3. Press Ctrl+D to soft reboot"
echo "   4. Press Ctrl+X to exit REPL and unmount"
echo ""
echo "⚙️  Setting up Python path..."
echo ""

# Mount the folder and enter REPL with path setup
# This keeps the mount active and gives an interactive Python prompt
# Note: mpremote mount src -> files appear at /remote/ (not /remote/src/)
mpremote mount "$folder" exec "import sys; sys.path.insert(0, '/remote')" repl
