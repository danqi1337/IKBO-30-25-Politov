"""Разбор коротких опций команд (-l, -la, --)."""

from emulator.errors import CommandError

LONG_PREFIX = "--"
SHORT_PREFIX = "-"


def is_option(arg):
    """Истинно для аргумента вида -x (но не для одиночного -)."""
    return arg.startswith(SHORT_PREFIX) and arg != SHORT_PREFIX


def check_flags(arg, allowed):
    """Проверяет склеенные флаги arg и возвращает их множество."""
    if arg.startswith(LONG_PREFIX):
        raise CommandError(f"unrecognized option '{arg}'")
    for char in arg[1:]:
        if char not in allowed:
            raise CommandError(f"invalid option -- '{char}'")
    return set(arg[1:])


def split_options(args, allowed):
    """Делит args на флаги и операнды.

    allowed - строка допустимых однобуквенных флагов. Аргумент -- завершает
    список опций. Возвращает (множество флагов, список операндов).
    """
    flags = set()
    operands = []
    for index, arg in enumerate(args):
        if arg == LONG_PREFIX:
            operands.extend(args[index + 1:])
            break
        if is_option(arg):
            flags |= check_flags(arg, allowed)
        else:
            operands.append(arg)
    return flags, operands
