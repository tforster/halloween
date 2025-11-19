#!/usr/bin/env bash
####################################################################################################################################
# deploy-dev.sh: Copy source files to Pico's internal storage for faster execution.
#
# Usage:    devops/deploy-dev.sh [--folder=src] [--run]
#
# Options:
#   --folder=src        Local folder to copy (default: src)
#   --run               Execute main.py after copying
#   --help              Show this help message
#
# Description:
#   Copies all Python files from the source folder to the Pico's internal storage.
#   Useful for faster execution without mount overhead.
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

Usage: deploy-dev.sh [--folder=src] [--run]

Options:
  --folder=src          Local folder to copy (default: src)
  --run                 Execute main.py after copying
  --help                Show this help message
"

# Parse the command line arguments
parseArgs "$USAGE" "$@"

# Set default folder if not provided
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

echo "📦 Copying files from '$folder' to Pico internal storage..."
echo ""

# Copy all Python files to Pico root
for file in "$folder"/*.py; do
  if [[ -f "$file" ]]; then
    filename=$(basename "$file")
    echo "  📄 Copying $filename..."
    mpremote cp "$file" ":$filename"
  fi
done

echo ""
echo "✅ Files copied successfully"

# Run main.py if requested
if [[ "$run" == "true" ]]; then
  echo ""
  echo "🚀 Executing main.py..."
  echo ""
  mpremote exec "exec(open('main.py').read())"
  echo ""
  echo "✅ Execution complete"
fi
