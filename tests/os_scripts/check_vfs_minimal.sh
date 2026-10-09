#!/bin/sh
# Проверка загрузки VFS: минимальная VFS (один файл).
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "### --vfs tests/vfs/minimal: минимальная VFS (один файл)"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --vfs "$ROOT/tests/vfs/minimal" \
    --script "$ROOT/tests/scripts/vfs_info.txt" </dev/null
echo "код возврата: $?"

echo
echo "### тот же VFS + общий скрипт этапа 3"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --vfs "$ROOT/tests/vfs/minimal" \
    --script "$ROOT/tests/scripts/test_stage3.txt" </dev/null
echo "код возврата: $?"
