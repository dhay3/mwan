function lib::fmt::color() {
  declare -rg FMT_RED=$(printf '\033[31m')
  declare -rg FMT_GREEN=$(printf '\033[32m')
  declare -rg FMT_BLUE=$(printf '\033[34m')
  declare -rg FMT_YELLOW=$(printf '\033[33m')
  declare -rg FMT_BOLD=$(printf '\033[1m')
  declare -rg FMT_UNDERLINE=$(printf '\033[4m')
  declare -rg FMT_CODE=$(printf '\033[2m')
  declare -rg FMT_RESET=$(printf '\033[0m')
}

function lib::fmt::lowerCase() {
  local param="${*,,}"
  echo "${param}"
}

function lib::fmt::upperCase() {
  local param="${*^^}"
  echo "${param}"
}

function lib::fmt::boldMessage() {
  local msg="${*}"
  printf "%s%s%s" "${FMT_BOLD}" "${msg}" "${FMT_RESET}"
}

function lib::fmt::underlineMessage() {
  local msg="${*}"
  printf "%s%s%s" "${FMT_UNDERLINE}" "${msg}" "${FMT_RESET}"
}

function lib::fmt::codeMessage() {
  local msg="${*}"
  printf "\`%s%s%s\`" "${FMT_CODE}" "${msg}" "${FMT_RESET}"
}

function lib::fmt::errorMessage() {
  local msg="${*}"
  printf "%s%s[EROR] %s%s" "${FMT_RED}" "${FMT_BOLD}" "${FMT_RESET}" "${msg}" >&2 && exit 1
}

function lib::fmt::succeedMessage() {
  local msg="${*}"
  printf "%s%s[SUCC] %s%s" "${FMT_GREEN}" "${FMT_BOLD}" "${FMT_RESET}" "${msg}" >&2
}

function lib::fmt::warningMessage() {
  local msg="${*}"
  printf "%s%s[WARN] %s%s" "${FMT_YELLOW}" "${FMT_BOLD}" "${FMT_RESET}" "${msg}" >&2
}

function lib::fmt::infoMessage() {
  local msg="${*}"
  printf "%s%s[INFO] %s%s" "${FMT_BLUE}" "${FMT_BOLD}" "${FMT_RESET}" "${msg}" >&2
}
