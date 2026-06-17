#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}/terraform"

receiver_function="$(terraform output -raw receiver_function_name)"
processor_function="$(terraform output -raw processor_function_name)"
worker_function="$(terraform output -raw worker_function_name)"

echo "== Receiver tentando listar buckets =="
aws lambda invoke \
  --function-name "${receiver_function}" \
  --cli-binary-format raw-in-base64-out \
  --payload '{"test":"s3-list"}' \
  /tmp/negative-receiver.json >/tmp/negative-receiver.meta 2>&1 || true
cat /tmp/negative-receiver.json 2>/dev/null || true
cat /tmp/negative-receiver.meta

echo "== Processor tentando enviar para fila nao autorizada =="
aws lambda invoke \
  --function-name "${processor_function}" \
  --cli-binary-format raw-in-base64-out \
  --payload '{"test":"unauthorized-queue"}' \
  /tmp/negative-processor.json >/tmp/negative-processor.meta 2>&1 || true
cat /tmp/negative-processor.json 2>/dev/null || true
cat /tmp/negative-processor.meta

echo "== Worker tentando ler S3 =="
aws lambda invoke \
  --function-name "${worker_function}" \
  --cli-binary-format raw-in-base64-out \
  --payload '{"test":"s3-read","s3Key":"DOC-001.txt"}' \
  /tmp/negative-worker.json >/tmp/negative-worker.meta 2>&1 || true
cat /tmp/negative-worker.json 2>/dev/null || true
cat /tmp/negative-worker.meta
