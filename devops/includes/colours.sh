#!/usr/bin/env bash
####################################################################################################################################
# colours.sh is a utility module that provides consistent coloured output and logging functions for devops scripts.
# - It defines ANSI colour codes and provides logging functions with consistent formatting.
# - Functions are prefixed with 'log_' for clarity and consistency across scripts.
#
# usage: Include in another script via source ./devops/includes/colours.sh
# example: log_success "Operation completed successfully!"
#          log_error "Something went wrong"
#          log_info "Processing templates..."
####################################################################################################################################

# Exit immediately if a command exits with a non-zero status
set -o errexit
# Treat unset variables as an error when substituting
set -o nounset
# Fails entire pipeline if any command fails
set -euo pipefail

# ANSI Color Codes
# ================
# Basic colors
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[0;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_MAGENTA='\033[0;35m'
readonly COLOR_CYAN='\033[0;36m'
readonly COLOR_WHITE='\033[0;37m'
readonly COLOR_GRAY='\033[0;90m'

# Bright colors
readonly COLOR_BRIGHT_RED='\033[0;91m'
readonly COLOR_BRIGHT_GREEN='\033[0;92m'
readonly COLOR_BRIGHT_YELLOW='\033[0;93m'
readonly COLOR_BRIGHT_BLUE='\033[0;94m'
readonly COLOR_BRIGHT_MAGENTA='\033[0;95m'
readonly COLOR_BRIGHT_CYAN='\033[0;96m'
readonly COLOR_BRIGHT_WHITE='\033[0;97m'

# Bold colors
readonly COLOR_BOLD_RED='\033[1;31m'
readonly COLOR_BOLD_GREEN='\033[1;32m'
readonly COLOR_BOLD_YELLOW='\033[1;33m'
readonly COLOR_BOLD_BLUE='\033[1;34m'
readonly COLOR_BOLD_MAGENTA='\033[1;35m'
readonly COLOR_BOLD_CYAN='\033[1;36m'
readonly COLOR_BOLD_WHITE='\033[1;37m'

# Background colors
readonly COLOR_BG_RED='\033[41m'
readonly COLOR_BG_GREEN='\033[42m'
readonly COLOR_BG_YELLOW='\033[43m'
readonly COLOR_BG_BLUE='\033[44m'
readonly COLOR_BG_MAGENTA='\033[45m'
readonly COLOR_BG_CYAN='\033[46m'
readonly COLOR_BG_WHITE='\033[47m'

# Text formatting
readonly FORMAT_BOLD='\033[1m'
readonly FORMAT_DIM='\033[2m'
readonly FORMAT_ITALIC='\033[3m'
readonly FORMAT_UNDERLINE='\033[4m'
readonly FORMAT_BLINK='\033[5m'
readonly FORMAT_REVERSE='\033[7m'
readonly FORMAT_STRIKETHROUGH='\033[9m'

# Reset code
readonly COLOR_RESET='\033[0m'
readonly NC='\033[0m'  # No Color - for backward compatibility

# Function to check if terminal supports colors
# ===========================================
function colors_supported() {
    if [[ -t 1 ]] && [[ "${TERM:-}" != "dumb" ]] && command -v tput >/dev/null 2>&1; then
        if tput colors >/dev/null 2>&1 && [[ $(tput colors) -ge 8 ]]; then
            return 0
        fi
    fi
    return 1
}

# Function to colorize text if colors are supported
# ===============================================
function colorize() {
    local color="$1"
    local text="$2"
    
    if colors_supported; then
        echo -e "${color}${text}${COLOR_RESET}"
    else
        echo "$text"
    fi
    return 0  # Always return success
}

# Basic color functions
# ====================
function color_red() {
    colorize "$COLOR_RED" "$1"
}

function color_green() {
    colorize "$COLOR_GREEN" "$1"
}

function color_yellow() {
    colorize "$COLOR_YELLOW" "$1"
}

function color_blue() {
    colorize "$COLOR_BLUE" "$1"
}

function color_cyan() {
    colorize "$COLOR_CYAN" "$1"
}

function color_gray() {
    colorize "$COLOR_GRAY" "$1"
}

function color_bold() {
    colorize "$FORMAT_BOLD" "$1"
}

# Logging Functions with Emojis and Colors
# ========================================

# Success logging (green with checkmark)
function log_success() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_GREEN}✅ ${message}${COLOR_RESET}"
    else
        echo "[SUCCESS] $message"
    fi
}

# Error logging (red with X mark)
function log_error() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_RED}❌ ${message}${COLOR_RESET}" >&2
    else
        echo "[ERROR] $message" >&2
    fi
}

# Warning logging (yellow with warning sign)
function log_warning() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_YELLOW}⚠️  ${message}${COLOR_RESET}"
    else
        echo "[WARNING] $message"
    fi
}

# Info logging (blue with info icon)
function log_info() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_BLUE}ℹ️  ${message}${COLOR_RESET}"
    else
        echo "[INFO] $message"
    fi
}

# Debug logging (gray with debug icon)
function log_debug() {
    local message="$1"
    if [[ "${DEBUG:-false}" == "true" ]]; then
        if colors_supported; then
            echo -e "${COLOR_GRAY}🐛 [DEBUG] ${message}${COLOR_RESET}"
        else
            echo "[DEBUG] $message"
        fi
    fi
}

# Step logging (cyan with arrow)
function log_step() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_CYAN}➡️  ${message}${COLOR_RESET}"
    else
        echo "[STEP] $message"
    fi
}

# Progress logging (magenta with clock)
function log_progress() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_MAGENTA}⏳ ${message}${COLOR_RESET}"
    else
        echo "[PROGRESS] $message"
    fi
}

# Task completion logging (bright green with party emoji)
function log_complete() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_BRIGHT_GREEN}🎉 ${message}${COLOR_RESET}"
    else
        echo "[COMPLETE] $message"
    fi
}

# Configuration/setup logging (blue with gear)
function log_config() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_BLUE}⚙️  ${message}${COLOR_RESET}"
    else
        echo "[CONFIG] $message"
    fi
}

# File/template logging (yellow with document)
function log_file() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_YELLOW}📄 ${message}${COLOR_RESET}"
    else
        echo "[FILE] $message"
    fi
}

# Network/deployment logging (green with rocket)
function log_deploy() {
    local message="$1"
    if colors_supported; then
        echo -e "${COLOR_GREEN}🚀 ${message}${COLOR_RESET}"
    else
        echo "[DEPLOY] $message"
    fi
}

# Separator functions
# ==================

# Print a colored separator line
function log_separator() {
    local char="${1:-=}"
    local length="${2:-50}"
    local color="${3:-$COLOR_GRAY}"
    
    if colors_supported; then
        printf "${color}"
        printf "%*s\n" "$length" | tr ' ' "$char"
        printf "${COLOR_RESET}"
    else
        printf "%*s\n" "$length" | tr ' ' "$char"
    fi
}

# Print a section header with separator
function log_section() {
    local title="$1"
    local char="${2:-=}"
    local color="${3:-$COLOR_BOLD_BLUE}"
    
    echo ""
    if colors_supported; then
        echo -e "${color}${title}${COLOR_RESET}"
        log_separator "$char" "${#title}" "$color"
    else
        echo "$title"
        log_separator "$char" "${#title}"
    fi
    echo ""
}

# Utility functions
# ================

# Print text with timestamp
function log_timestamp() {
    local message="$1"
    local timestamp
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    if colors_supported; then
        echo -e "${COLOR_GRAY}[${timestamp}]${COLOR_RESET} $message"
    else
        echo "[$timestamp] $message"
    fi
}

# Print a key-value pair with formatting
function log_keyvalue() {
    local key="$1"
    local value="$2"
    local key_color="${3:-$COLOR_CYAN}"
    local value_color="${4:-$COLOR_WHITE}"
    
    if colors_supported; then
        echo -e "  ${key_color}${key}:${COLOR_RESET} ${value_color}${value}${COLOR_RESET}"
    else
        echo "  $key: $value"
    fi
}

# Print a banner with border
function log_banner() {
    local message="$1"
    local border_char="${2:-#}"
    local color="${3:-$COLOR_BOLD_GREEN}"
    local padding=4
    local border_length=$((${#message} + padding * 2))
    
    echo ""
    if colors_supported; then
        printf "${color}"
        printf "%*s\n" "$border_length" | tr ' ' "$border_char"
        printf "%*s%s%*s\n" $padding '' "$message" $padding ''
        printf "%*s\n" "$border_length" | tr ' ' "$border_char"
        printf "${COLOR_RESET}"
    else
        printf "%*s\n" "$border_length" | tr ' ' "$border_char"
        printf "%*s%s%*s\n" $padding '' "$message" $padding ''
        printf "%*s\n" "$border_length" | tr ' ' "$border_char"
    fi
    echo ""
}

# Export functions for use in other scripts
# =========================================
# Note: In bash, functions are automatically available to child processes
# when sourced, but we can explicitly export them if needed

# Backward compatibility aliases
# =============================
# These maintain compatibility with existing scripts while encouraging new naming

# Define as functions instead of aliases for better portability
function log_warn() {
    log_warning "$@"
}

function log_ok() {
    log_success "$@"
}

function log_fail() {
    log_error "$@"
}
