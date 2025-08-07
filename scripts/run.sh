#!/usr/bin/env bash

set -e
set -x

uv run granian --interface asgi app:app \
  --host 0.0.0.0 --port 8000 \
  --reload --reload-paths ./app \
  --access-log --log-level debug
