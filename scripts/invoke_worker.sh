#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}/terraform"
function_name="$(terraform output -raw worker_function_name)"
document_id="${1:-DOC-001}"
s3_key="${2:-DOC-001.txt}"

payload="{\"documentId\":\"${document_id}\",\"documentType\":\"INVOICE\",\"s3Key\":\"${s3_key}\"}"
aws lambda invoke \
  --function-name "${function_name}" \
  --cli-binary-format raw-in-base64-out \
  --payload "${payload}" \
  /tmp/worker-output.json >/dev/null
cat /tmp/worker-output.json
