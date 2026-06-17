#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"${repo_root}/scripts/package.sh"

cd "${repo_root}/terraform"
terraform init
terraform apply -auto-approve

