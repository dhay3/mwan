#!/usr/bin/env bash

set -euo pipefail

readonly BASE_URL=${MWAN_BASE_URL:-https://cpd-swy.oss-cn-hangzhou.aliyuncs.com/temp/hz.cheng/mwan}
readonly INSTALL_DIR=/opt/mwan
readonly SYSTEMD_DIR=/etc/systemd/system
readonly SERVICE_NAME=mwan.service
readonly TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/mwan-install.XXXXXXXX")

cleanup() {
  rm -rf -- "${TEMP_DIR}"
}
trap cleanup EXIT

info() {
  printf '[INFO] %s\n' "$*"
}

error() {
  printf '[ERROR] %s\n' "$*" >&2
  exit 1
}

require_root() {
  if ((EUID != 0)); then
    error "Run this script as root, for example: sudo $0"
  fi
}

require_command() {
  command -v "$1" > /dev/null 2>&1 || error "Required command not found: $1"
}

download() {
  local name=$1
  info "Downloading ${name}"
  curl \
    --fail \
    --location \
    --silent \
    --show-error \
    --output "${TEMP_DIR}/${name}" \
    "${BASE_URL}/${name}"
}

install_files() {
  install -d -m 0755 "${INSTALL_DIR}"
  install -m 0755 "${TEMP_DIR}/mwan" "${INSTALL_DIR}/mwan"

  if [[ -e ${INSTALL_DIR}/mwan.toml ]]; then
    info "Preserving existing configuration: ${INSTALL_DIR}/mwan.toml"
  else
    install -m 0644 "${TEMP_DIR}/mwan.toml" "${INSTALL_DIR}/mwan.toml"
  fi

  install -m 0644 \
    "${TEMP_DIR}/${SERVICE_NAME}" \
    "${SYSTEMD_DIR}/${SERVICE_NAME}"
}

main() {
  require_root
  require_command curl
  require_command install
  require_command sha1sum
  require_command systemctl

  download mwan
  download mwan.sha1
  download mwan.toml
  download "${SERVICE_NAME}"

  info 'Verifying mwan SHA-1 checksum'
  (cd "${TEMP_DIR}" && sha1sum --check mwan.sha1)

  systemctl stop "${SERVICE_NAME}" > /dev/null 2>&1 || true
  install_files
  systemctl daemon-reload
  systemctl enable --now "${SERVICE_NAME}"

  info 'mwan binary installation completed'
  systemctl --no-pager --full status "${SERVICE_NAME}"
}

main "$@"
