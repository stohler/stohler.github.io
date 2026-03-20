#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 não encontrado no ambiente do cloud agent." >&2
  exit 1
fi

python3 - <<'PY'
import sys

minimum = (3, 11)
if sys.version_info < minimum:
    found = ".".join(str(v) for v in sys.version_info[:3])
    required = ".".join(str(v) for v in minimum)
    raise SystemExit(
        f"Versão de Python incompatível: {found}. Necessário >= {required}."
    )
PY

# Garante pip mesmo em imagens mínimas.
if ! python3 -m pip --version >/dev/null 2>&1; then
  python3 -m ensurepip --upgrade
fi

python3 -m pip install --upgrade pip
python3 -m pip install ./stohler-news-agent

