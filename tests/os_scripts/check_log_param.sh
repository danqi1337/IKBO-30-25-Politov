#!/bin/sh
# Проверка параметра --log: создание CSV, дозапись, ошибка пути.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
SCRIPT="$ROOT/tests/scripts/test_stage2.txt"

echo "### --log: первый запуск создаёт файл с заголовком"
"$ROOT/run.sh" --headless --log "$TMP/events.csv" \
    --script "$SCRIPT" </dev/null >/dev/null
cat "$TMP/events.csv"

echo
echo "### --log: второй запуск дописывает события"
"$ROOT/run.sh" --headless --log "$TMP/events.csv" \
    --script "$SCRIPT" </dev/null >/dev/null
echo "строк в журнале: $(wc -l < "$TMP/events.csv")"

echo
echo "### --log: недоступный путь (ошибка выводится, работа продолжается)"
"$ROOT/run.sh" --headless --log "$TMP/no/such/dir/log.csv" </dev/null
echo "код возврата: $?"
