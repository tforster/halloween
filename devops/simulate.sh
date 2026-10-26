#!/usr/bin/env bash
####################################################################################################################################
# simulate.sh: Run the firmware in a running Wokwi simulation and start the storm in test mode.
#
# Usage:    devops/simulate.sh [--port=4000] [--rigs=1]
#
# Options:
#   --port=4000         Wokwi RFC 2217 serial port, as set by rfc2217ServerPort in wokwi/wokwi.toml (default: 4000)
#   --rigs=1            Run the first N rigs from RIGS; the simulated board has one strip, on rig A's pin (default: 1)
#   --help              Show this help message
#
# Description:
#   Start the simulator first (VS Code: "Wokwi: Start Simulator" on wokwi/wokwi.toml). The simulated Pico 2's flash is not
#   writable (mkfs fails with ENOSPC), so src/ is not copied: mpremote mounts it from the host over the serial link and the firmware
#   imports from there. Test mode (1-3 s intervals) makes overlapping strikes common, and each rig drives 10 pixels to match
#   the simulated strip; both are switched on for this run only,
#   so src/main.py stays as deployed. Wokwi has no DFPlayer part and its Pico 2 hangs opening UART1, so SIMULATED skips the
#   UART and thunder frames print here instead ("DFPlayer < 7E FF ...").
#   Ctrl-C stops the storm.
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

Usage: simulate.sh [--port=4000] [--rigs=1]

Options:
  --port=4000           Wokwi RFC 2217 serial port (default: 4000)
  --rigs=1              Run the first N rigs (default: 1)
  --help                Show this help message
"

# Parse the command line arguments
parseArgs "$USAGE" "$@"

# mpremote comes from requirements.txt, so use the project venv's copy without needing it activated
if [[ -x venv/bin/mpremote ]]; then
  PATH="$PWD/venv/bin:$PATH"
fi

if ! command -v mpremote &>/dev/null; then
  echo "❌ mpremote is not installed."
  echo "Install with: pip install mpremote"
  exit 1
fi

# Wokwi simulates every WS2812 bit; two 300-pixel strips run at about 4% of real time, so the simulated strip (and each
# rig, for this run only) has 10 pixels
simulatedPixels=10

# resume skips mpremote's soft reset: each reset re-runs _boot.py, which tries to format the unwritable flash and takes
# longer than mpremote waits for the raw REPL. Importing main does not start it; start() runs after the overrides,
# which last for this session only
mpremote connect "port:rfc2217://localhost:${port}" resume mount src exec "import main
main.TEST_MODE = True
main.SIMULATED = True
main.RIGS = main.RIGS[:${rigs}]
for rig in main.RIGS:
    rig['pixels'] = ${simulatedPixels}
main.start()"
