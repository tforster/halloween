#!/usr/bin/env bash
####################################################################################################################################
# run.sh: Execute MicroPython files on Raspberry Pi Pico 2 via mpremote.
#
# Usage:    devops/run.sh [--file=main.py] [--folder=src]
#
# Options:
#   --file=main.py      Python file to execute (default: main.py)
#   --folder=src        Folder containing the file (default: src)
#   --repl              Drop into REPL after execution
#   --mount             Keep folder mounted after execution
#   --help              Show this help message
#
# Description:
#   Executes a MicroPython file on the Pico via mpremote. Can temporarily mount the folder,
#   run the file, and optionally enter REPL for debugging.
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

Usage: run.sh [--file=main.py] [--folder=src] [--repl] [--mount]

Options:
  --file=main.py        Python file to execute (default: main.py)
  --folder=src          Folder containing the file (default: src)
  --repl                Drop into REPL after execution
  --mount               Keep folder mounted after execution
  --help                Show this help message
"

# Parse the command line arguments
parseArgs "$USAGE" "$@"

# Set defaults if not provided
file="${file:-main.py}"
folder="${folder:-src}"

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

# Check if file exists
if [[ ! -f "$folder/$file" ]]; then
  echo "❌ File '$folder/$file' does not exist"
  exit 1
fi

echo "🚀 Executing $file on Raspberry Pi Pico 2..."
echo ""

# Build mpremote command
# Note: mpremote mount src -> files appear at /remote/ (not /remote/src/)
cmd="mpremote mount $folder exec \"import sys; sys.path.insert(0, '/remote')\" exec \"exec(open('/remote/$file').read())\""

if [[ "$repl" == "true" ]]; then
  echo "📝 Entering REPL after execution (Ctrl+X to exit, Ctrl+D to soft reboot)"
  cmd="$cmd repl"
elif [[ "$mount" == "true" ]]; then
  echo "📁 Keeping folder mounted (Ctrl+C to stop)"
  # Just mount without exec, keeps it alive
  mpremote mount "$folder"
  exit 0
fi

# Execute the command
eval "$cmd"

echo ""
echo "✅ Execution complete"
