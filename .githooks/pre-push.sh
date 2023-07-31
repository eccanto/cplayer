#!/usr/bin/env bash

set -euox pipefail

python -m brunette --check --diff --skip-string-normalization --config setup.cfg "."
python -m isort --check-only --diff "."
python -m prospector "."
