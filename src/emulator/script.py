"""Стартовые скрипты эмулятора."""

from emulator.parser import ParseError, parse


class ScriptError(Exception):
    """Ошибка чтения стартового скрипта."""


def read_script(path):
    """Читает скрипт и возвращает список его строк."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        reason = getattr(exc, "strerror", None) or "invalid encoding"
        message = f"не удалось прочитать скрипт '{path}': {reason}"
        raise ScriptError(message) from exc


def is_skippable(line):
    """Истинно для пустых строк и строк, состоящих из комментария."""
    try:
        return not parse(line)
    except ParseError:
        return False


def run_script(shell, lines, write):
    """Выполняет строки скрипта, показывая и ввод, и вывод.

    Строки с ошибками пропускаются с сообщением об их номере.
    """
    for number, line in enumerate(lines, start=1):
        if is_skippable(line):
            continue
        result = shell.interact(line.strip(), write)
        if result.is_error:
            write(f"[скрипт] ошибка в строке {number}, "
                  "строка пропущена")
        if not shell.running:
            break
