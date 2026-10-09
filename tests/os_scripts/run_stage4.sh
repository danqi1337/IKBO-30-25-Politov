#!/bin/sh
# Запуск стартового скрипта этапа 4 (ls, cd, tail, tac) на глубокой VFS.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --vfs "$ROOT/tests/vfs/deep" \
    --script "$ROOT/tests/scripts/test_stage4.txt" </dev/null
echo "код возврата: $?"
