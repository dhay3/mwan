#!/usr/bin/env bash

if [[ -x $(command -v act) ]]; then
  act -l
  act -n -e workflow_dispatch
  act --secret-file .env workflow_dispatch
fi
