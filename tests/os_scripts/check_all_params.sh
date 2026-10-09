#!/bin/sh
# Проверка всех параметров сразу и отладочного вывода параметров.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "### --vfs --log --script --headless одновременно"
"$ROOT/run.sh" --headless --vfs "$TMP/some-vfs" \
    --log "$TMP/log.csv" \
    --script "$ROOT/tests/scripts/test_stage2.txt" </dev/null
echo "код возврата: $?"

echo
echo "### без параметров (используются значения по умолчанию)"
cd "$TMP" && printf 'exit\n' | "$ROOT/run.sh" --headless
echo "код возврата: $?"
ls "$TMP"

echo
echo "### справка --help"
"$ROOT/run.sh" --help
