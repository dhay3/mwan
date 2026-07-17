#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
readonly INSTALL_DIR="/opt/mwan"
readonly SYSTEMD_DIR="/etc/systemd/system"
readonly SERVICE_NAME="mwan.service"

readonly BINARY_SOURCE="${1:-${PROJECT_DIR}/dist/mwan}"
readonly CONFIG_SOURCE="${2:-${PROJECT_DIR}/src/mwan.toml}"
readonly SERVICE_SOURCE="${PROJECT_DIR}/src/${SERVICE_NAME}"

function info() {
  printf '[INFO] %s\n' "${*}"
}

function error() {
  printf '[ERROR] %s\n' "${*}" >&2
  exit 1
}

function require_root() {
  if ((EUID != 0)); then
    error "请使用 root 用户运行此脚本，例如：sudo ${0}"
  fi
}

function require_command() {
  command -v "${1}" > /dev/null 2>&1 || error "未找到所需命令：${1}"
}

function require_file() {
  [[ -f "${1}" ]] || error "文件不存在：${1}"
}

function install_files() {
  install -d -m 0755 "${INSTALL_DIR}"
  install -m 0755 "${BINARY_SOURCE}" "${INSTALL_DIR}/mwan"

  if [[ -e "${INSTALL_DIR}/mwan.toml" ]]; then
    info "保留已有配置：${INSTALL_DIR}/mwan.toml"
  else
    install -m 0644 "${CONFIG_SOURCE}" "${INSTALL_DIR}/mwan.toml"
  fi

  install -m 0644 "${SERVICE_SOURCE}" "${SYSTEMD_DIR}/${SERVICE_NAME}"
}

function start_service() {
  systemctl daemon-reload
  systemctl enable --now "${SERVICE_NAME}"
}

function main() {
  require_root
  require_command install
  require_command systemctl
  require_file "${BINARY_SOURCE}"
  require_file "${CONFIG_SOURCE}"
  require_file "${SERVICE_SOURCE}"

  info "安装 mwan 到 ${INSTALL_DIR}"
  install_files
  start_service
  info "mwan 安装完成，服务状态："
  systemctl --no-pager --full status "${SERVICE_NAME}"
}

main
