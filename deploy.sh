#!/bin/sh
# Keys are read by Python and uploaded via stdin, never sourced as shell code.
set -eu
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: ./deploy.sh PROJECT_ID GOOGLE_ACCOUNT_EMAIL [REGION]" >&2
    exit 2
fi
cd "$(dirname "$0")"
.venv/bin/python scripts/prepare_cloud_run.py --project "$1" --account "$2" --region "${3:-us-west1}"
exec .venv/bin/python scripts/deploy_cloud_run.py --project "$1"
