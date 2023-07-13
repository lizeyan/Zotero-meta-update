#!/usr/bin/env bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd ${SCRIPT_DIR}/..
pwd
source ./.venv/bin/activate
PYTHONPATH=$(realpath .) python ./bin/update_zotero_meta --output-dir output -w --skip-confirmation
