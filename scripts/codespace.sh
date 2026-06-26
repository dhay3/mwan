#!/usr/bin/env bash

set -eo pipefail

function init() {
  conda env create -f environment.yml --prefix "${PWD}/.conda"
  yarn install && npm list
}

function hook_commit-msg() {
  cat << EOF > .husky/commit-msg
#!/usr/bin/env bash

npx commitlint --edit $1
EOF
}

function hook_pre-commit() {
  cat << EOF > .husky/pre-commit
#!/usr/bin/env bash

gitleaks git . --verbose
npx lint-staged
EOF
}

function hook_pre-commit-msg() {
  cat << EOF > .husky/prepare-commit-msg
#!/usr/bin/env bash

if npx -v >&/dev/null
then
  exec < /dev/tty
  npx -c "gitmoji --hook ${1} ${2}"
else
  exec < /dev/tty
  gitmoji --hook "${1}" "${2}"
fi
EOF
}

function __main__() {
  case "${1}" in
    "init")
      init
      ;;
  esac

}

__main__ "${@}"
