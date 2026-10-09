#!/bin/sh
# Запуск стартового скрипта этапа 5 (chown, rmdir) на глубокой VFS и
# проверка того, что каталог VFS на диске остался неизменным.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
VFS="$ROOT/tests/vfs/deep"

find "$VFS" | sort > "$TMP/before.txt"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" --vfs "$VFS" \
    --script "$ROOT/tests/scripts/test_stage5.txt" </dev/null
echo "код возврата: $?"
find "$VFS" | sort > "$TMP/after.txt"
if cmp -s "$TMP/before.txt" "$TMP/after.txt"; then
    echo "VFS на диске не изменилась: OK"
else
    echo "VFS на диске изменилась: ОШИБКА"
fi
