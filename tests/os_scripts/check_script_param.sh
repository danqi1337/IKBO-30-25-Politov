#!/bin/sh
# Проверка параметра --script: успешный запуск и ошибка чтения.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "### --script: стартовый скрипт с комментариями"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --script "$ROOT/tests/scripts/test_stage2.txt" </dev/null
echo "код возврата: $?"

echo
echo "### --script: несуществующий файл (ошибка выводится, работа продолжается)"
"$ROOT/run.sh" --headless --log "$TMP/log.csv" \
    --script "$TMP/missing.esh" </dev/null
echo "код возврата: $?"
