#!/bin/sh
# Проверка ошибок загрузки VFS.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
INFO="$ROOT/tests/scripts/vfs_info.txt"

echo "### --vfs: каталог не существует"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --vfs "$TMP/no_such_vfs" --script "$INFO" </dev/null

echo
echo "### --vfs: вместо каталога передан файл (неверный формат)"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --vfs "$ROOT/tests/vfs/minimal/readme.txt" --script "$INFO" </dev/null

echo
echo "### без --vfs: VFS по умолчанию"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" --script "$INFO" </dev/null
