#!/bin/sh
# Проверка загрузки VFS: VFS с тремя и более уровнями вложенности.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "### --vfs tests/vfs/deep: VFS с тремя и более уровнями вложенности"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --vfs "$ROOT/tests/vfs/deep" \
    --script "$ROOT/tests/scripts/vfs_info.txt" </dev/null
echo "код возврата: $?"

echo
echo "### тот же VFS + общий скрипт этапа 3"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --vfs "$ROOT/tests/vfs/deep" \
    --script "$ROOT/tests/scripts/test_stage3.txt" </dev/null
echo "код возврата: $?"
