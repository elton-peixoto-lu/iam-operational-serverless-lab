#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}/terraform"
bucket_name="$(terraform output -raw document_bucket_name)"
document_id="${1:-DOC-001}"
document_type="${2:-INVOICE}"
file_path="/tmp/${document_id}.txt"
key="${document_id}.txt"

printf 'document %s\n' "${document_id}" > "${file_path}"

aws s3 cp "${file_path}" "s3://${bucket_name}/${key}" \
  --metadata "document-id=${document_id},document-type=${document_type}"

echo "Arquivo enviado para s3://${bucket_name}/${key}"

