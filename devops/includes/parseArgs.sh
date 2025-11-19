#!/usr/bin/env bash
####################################################################################################################################
# parseArgs.sh is a utility function to parse arguments passed to a script.
# - It determines the allowable arguments and their values from the usage string.
#
# usage: Include in another script via source ./devops/includes/parseArgs.sh and call parse_args "$usage" "$@"
####################################################################################################################################

# Exit immediately if a command exits with a non-zero status
set -o errexit
# Treat unset variables as an error when substituting
set -o nounset
# Fails entire pipeline if any command fails
set -euo pipefail

# This is early days. There are several more features to add
# --help should echo out the docstring
# --verbose should iterate all the values and echo those out, possibly with the same help docstring
# Shortcuts, eg. -v for --verbose, etc don't seem to be working properly yet. Use --long-form only for now.

parseArgs() {
  local usage="$1"
  shift

  # Parse the usage string for default values first
  while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*--([a-zA-Z0-9_-]+)=([^[:space:]]+) ]]; then
      local var_name="${BASH_REMATCH[1]}"
      # Replace hyphens with underscores for variable names if necessary (optional, depends on naming convention)
      var_name="${var_name//-/_}"
      local default_value="${BASH_REMATCH[2]}"
      # Set the default value using eval
      eval "${var_name}=\"${default_value}\""
    fi
  done <<<"$(echo "$usage" | grep -E '^[[:space:]]*--[a-zA-Z0-9_-]+=')"

  # Initialize boolean flags (arguments without defaults) to false
  while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*--([a-zA-Z0-9_-]+)[[:space:]]+[^=] ]]; then
      local var_name="${BASH_REMATCH[1]}"
      # Replace hyphens with underscores for variable names
      var_name="${var_name//-/_}"
      # Only set to false if the variable is not already set
      if [[ -z "${!var_name:-}" ]]; then
        eval "${var_name}=false"
      fi
    fi
  done <<<"$(echo "$usage" | grep -E '^[[:space:]]*--[a-zA-Z0-9_-]+[[:space:]]+' | grep -v '=')"

  # Now parse the actual arguments provided, potentially overwriting defaults
  while [[ "$#" -gt 0 ]]; do
    case $1 in
    --*=*)
      local var_name="${1%%=*}"
      var_name="${var_name#--}"
      # Replace hyphens with underscores if necessary
      var_name="${var_name//-/_}"
      local var_value="${1#*=}"
      eval "${var_name}=\"$var_value\""
      ;;
    --*)
      local var_name="${1#--}"
      # Replace hyphens with underscores if necessary
      var_name="${var_name//-/_}"
      if [[ "$#" -gt 1 && ! "$2" =~ ^-- ]]; then
        eval "${var_name}=\"$2\""
        shift
      else
        # Handle boolean flags (arguments without values)
        eval "${var_name}=true"
      fi
      ;;
    *)
      echo "Invalid option: $1" >&2
      echo "$usage" >&2
      exit 1
      ;;
    esac
    shift
  done

  if [[ "${help:-false}" == "true" ]]; then
    echo "$usage"
    exit 0
  fi

  ## Echo more information if the verbose flag is set
  if [[ "${verbose:-false}" == "true" ]]; then
    set -x # Enable debug mode to show commands
  fi
}
