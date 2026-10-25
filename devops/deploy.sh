#!/usr/bin/env bash
####################################################################################################################################
# deploy.sh is a utility that copies MicroPython source files to a connected Raspberry Pi Pico 2 device.
####################################################################################################################################

# Exit immediately if a command exits with a non-zero status
set -o errexit
# Treat unset variables as an error when substituting
set -o nounset
# Fails entire pipeline if any command fails
set -euo pipefail

mpremote cp -r src/* :
