#!/usr/bin/env bash

set -euox pipefail

brunette --check --diff --skip-string-normalization --config setup.cfg "."
isort --check-only --diff "."
prospector "."
