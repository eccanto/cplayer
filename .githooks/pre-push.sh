#!/usr/bin/env bash

set -euox pipefail

readonly PROJECT_DIRECTORY="./cplayer"

python -m brunette --check --diff --skip-string-normalization --config setup.cfg "."
python -m isort --check-only --diff --src "${PROJECT_DIRECTORY}" "."
python -m prospector "."
