"""Текстовые команды эмулятора: tail и tac."""

from emulator.errors import CommandError
from emulator.options import SHORT_PREFIX, is_option
from emulator.vfs import VfsError

DEFAULT_LINES = 10
COUNT_OPTION = "-n"


def read_lines(shell, path):
    """Читает файл path из VFS и возвращает список его строк."""
    try:
        return shell.vfs.read_file(path).splitlines()
    except VfsError as exc:
        raise CommandError(f"cannot open '{path}' for reading: {exc}") \
            from exc


def parse_count(text):
    """Преобразует аргумент опции -n в число строк."""
    if text is None:
        raise CommandError("option requires an argument -- 'n'")
    if not text.isdigit():
        raise CommandError(f"invalid number of lines: '{text}'")
    return int(text)


def parse_tail_args(args):
    """Разбирает аргументы tail; возвращает (число строк, файлы)."""
    count = DEFAULT_LINES
    files = []
    rest = iter(args)
    for arg in rest:
        if arg == COUNT_OPTION:
            count = parse_count(next(rest, None))
        elif arg.startswith(COUNT_OPTION):
            count = parse_count(arg[len(COUNT_OPTION):])
        elif is_option(arg) and arg[1:].isdigit():
            count = parse_count(arg[1:])
        elif is_option(arg):
            raise CommandError(f"invalid option -- '{arg[1:]}'")
        else:
            files.append(arg)
    return count, files


def last_lines(lines, count):
    """Возвращает последние count строк списка lines."""
    return lines[-count:] if count else []


def cmd_tail(shell, args):
    """tail [-n N] ФАЙЛ... - выводит последние N (10) строк файлов."""
    count, files = parse_tail_args(args)
    if not files:
        raise CommandError("missing file operand")
    blocks = []
    for path in files:
        body = "\n".join(last_lines(read_lines(shell, path), count))
        blocks.append(f"==> {path} <==\n{body}" if files[1:] else body)
    return "\n\n".join(blocks)


def cmd_tac(shell, args):
    """tac ФАЙЛ... - выводит строки файлов в обратном порядке."""
    if not args:
        raise CommandError("missing file operand")
    if any(is_option(arg) and arg != SHORT_PREFIX for arg in args):
        raise CommandError("options are not supported")
    lines = []
    for path in args:
        lines.extend(reversed(read_lines(shell, path)))
    return "\n".join(lines)


TEXT_COMMANDS = {
    "tail": cmd_tail,
    "tac": cmd_tac,
}
