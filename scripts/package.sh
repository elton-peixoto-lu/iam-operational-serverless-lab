#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="${repo_root}/build"

mkdir -p "${build_dir}"
rm -f "${build_dir}"/*.zip

for fn in receiver processor worker; do
  zip -qj "${build_dir}/${fn}.zip" "${repo_root}/lambdas/${fn}/app.py"
done

echo "Lambdas empacotadas em ${build_dir}"

