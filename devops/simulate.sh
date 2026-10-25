#!/usr/bin/env bash
####################################################################################################################################
# simulate.sh: Copy the firmware into a running Wokwi simulation and start the storm in test mode.
#
# Usage:    devops/simulate.sh [--port=4000]
#
# Options:
#   --port=4000         Wokwi RFC 2217 serial port, as set by rfc2217ServerPort in wokwi/wokwi.toml (default: 4000)
#   --help              Show this help message
#
# Description:
#   Start the simulator first (VS Code: "Wokwi: Start Simulator" on wokwi/wokwi.toml). Its filesystem is empty on every start,
#   so run this each time. Test mode (5-10 s intervals) makes overlapping strikes common; it is switched on for this run only,
#   so src/main.py stays as deployed. Wokwi has no DFPlayer part, so thunder frames print here instead ("DFPlayer < 7E FF ...").
#   Ctrl-C stops the storm.
#
####################################################################################################################################

# Exit immediately if a command exits with a non-zero status
set -o errexit
# Treat unset variables as an error when substituting
set -o nounset
# Fails entire pipeline if any command fails
set -euo pipefail

# Include the parseArgs function
source ./devops/includes/parseArgs.sh

# Usage docstring that is parsed by the parseArgs function. Edit with care.
USAGE="

Usage: simulate.sh [--port=4000]

Options:
  --port=4000           Wokwi RFC 2217 serial port (default: 4000)
  --help                Show this help message
"

# Parse the command line arguments
parseArgs "$USAGE" "$@"

if ! command -v mpremote &>/dev/null; then
  echo "❌ mpremote is not installed."
  echo "Install with: pip install mpremote"
  exit 1
fi

# Importing main does not start it; start() runs after TEST_MODE is switched on for this session only
mpremote connect "port:rfc2217://localhost:${port}" cp src/*.py : + exec "import main; main.TEST_MODE = True; main.start()"
