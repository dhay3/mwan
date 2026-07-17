#!/usr/bin/env bash

set -euo pipefail

APP_NAME=mwan
VERSION=${1:-1.0.0}
PROJECT_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
DIST_DIR=${PROJECT_ROOT}/dist
PACKAGE_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/mwan-deb.XXXXXXXX")
PACKAGE_WORK=$(mktemp -d "${TMPDIR:-/tmp}/mwan-deb-work.XXXXXXXX")

cleanup() {
  rm -rf -- "${PACKAGE_ROOT}" "${PACKAGE_WORK}"
}
trap cleanup EXIT

if command -v dpkg > /dev/null 2>&1; then
  ARCHITECTURE=$(dpkg --print-architecture)
else
  case $(uname -m) in
    x86_64) ARCHITECTURE=amd64 ;;
    aarch64) ARCHITECTURE=arm64 ;;
    armv7l) ARCHITECTURE=armhf ;;
    *)
      echo "Unsupported architecture: $(uname -m)" >&2
      exit 1
      ;;
  esac
fi

PACKAGE_FILE=${DIST_DIR}/${APP_NAME}_${VERSION}_${ARCHITECTURE}.deb

if [[ ! ${VERSION} =~ ^[0-9][0-9A-Za-z.+:~-]*$ ]]; then
  echo "Invalid Debian package version: ${VERSION}" >&2
  exit 1
fi

if [[ ! -x ${DIST_DIR}/${APP_NAME} ]]; then
  echo "Missing executable: ${DIST_DIR}/${APP_NAME}" >&2
  echo 'Run make package first.' >&2
  exit 1
fi

install -d \
  "${PACKAGE_ROOT}/DEBIAN" \
  "${PACKAGE_ROOT}/lib/systemd/system" \
  "${PACKAGE_ROOT}/opt/${APP_NAME}"

install -m 0755 \
  "${DIST_DIR}/${APP_NAME}" \
  "${PACKAGE_ROOT}/opt/${APP_NAME}/${APP_NAME}"
install -m 0644 \
  "${PROJECT_ROOT}/src/${APP_NAME}.toml" \
  "${PACKAGE_ROOT}/opt/${APP_NAME}/${APP_NAME}.toml"
install -m 0644 \
  "${PROJECT_ROOT}/src/${APP_NAME}.service" \
  "${PACKAGE_ROOT}/lib/systemd/system/${APP_NAME}.service"

sed \
  -e "s/@VERSION@/${VERSION}/g" \
  -e "s/@ARCHITECTURE@/${ARCHITECTURE}/g" \
  "${PROJECT_ROOT}/packaging/debian/control" \
  > "${PACKAGE_ROOT}/DEBIAN/control"

install -m 0644 \
  "${PROJECT_ROOT}/packaging/debian/conffiles" \
  "${PACKAGE_ROOT}/DEBIAN/conffiles"
install -m 0755 \
  "${PROJECT_ROOT}/packaging/debian/postinst" \
  "${PACKAGE_ROOT}/DEBIAN/postinst"
install -m 0755 \
  "${PROJECT_ROOT}/packaging/debian/postrm" \
  "${PACKAGE_ROOT}/DEBIAN/postrm"
install -m 0755 \
  "${PROJECT_ROOT}/packaging/debian/prerm" \
  "${PACKAGE_ROOT}/DEBIAN/prerm"

if command -v dpkg-deb > /dev/null 2>&1; then
  dpkg-deb --build --root-owner-group "${PACKAGE_ROOT}" "${PACKAGE_FILE}"
else
  printf '2.0\n' > "${PACKAGE_WORK}/debian-binary"
  tar \
    --create \
    --xz \
    --file "${PACKAGE_WORK}/control.tar.xz" \
    --directory "${PACKAGE_ROOT}/DEBIAN" \
    --owner 0 \
    --group 0 \
    --sort name \
    .
  tar \
    --create \
    --xz \
    --file "${PACKAGE_WORK}/data.tar.xz" \
    --directory "${PACKAGE_ROOT}" \
    --exclude './DEBIAN' \
    --owner 0 \
    --group 0 \
    --sort name \
    .
  ar rcs \
    "${PACKAGE_WORK}/${APP_NAME}.deb" \
    "${PACKAGE_WORK}/debian-binary" \
    "${PACKAGE_WORK}/control.tar.xz" \
    "${PACKAGE_WORK}/data.tar.xz"
  mv "${PACKAGE_WORK}/${APP_NAME}.deb" "${PACKAGE_FILE}"
fi
echo "Built ${PACKAGE_FILE}"
