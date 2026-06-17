#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}/terraform"
function_name="$(terraform output -raw receiver_function_name)"

payload='{"documentId":"DOC-001","documentType":"INVOICE"}'
aws lambda invoke \
  --function-name "${function_name}" \
  --cli-binary-format raw-in-base64-out \
  --payload "${payload}" \
  /tmp/receiver-output.json >/dev/null
cat /tmp/receiver-output.json
