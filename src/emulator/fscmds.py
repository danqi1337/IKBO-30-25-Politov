"""Команды, изменяющие VFS в памяти: chown и rmdir."""

import posixpath
import re

from emulator.errors import CommandError
from emulator.options import split_options
from emulator.vfs import VfsError

OWNER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
ROOT = "/"


def find_node(shell, path):
    """Находит узел VFS по пути или сообщает об ошибке."""
    try:
        return shell.vfs.lookup(path)
    except VfsError as exc:
        raise CommandError(f"cannot access '{path}': {exc}") from exc


def cmd_chown(shell, args):
    """chown [-R] ВЛАДЕЛЕЦ ПУТЬ... - меняет владельца файлов и каталогов.

    Сначала проверяются все пути, и только потом применяются изменения.
    """
    flags, operands = split_options(args, "R")
    if not operands:
        raise CommandError("missing operand")
    owner, paths = operands[0], operands[1:]
    if not paths:
        raise CommandError(f"missing operand after '{owner}'")
    if not OWNER_PATTERN.match(owner):
        raise CommandError(f"invalid user: '{owner}'")
    nodes = [find_node(shell, path) for path in paths]
    for node in nodes:
        shell.vfs.set_owner(node, owner, "R" in flags)
    return ""


def path_chain(path):
    """Возвращает path и его родителей: a/b/c -> [a/b/c, a/b, a]."""
    chain = []
    current = path.rstrip(ROOT) or path
    while current not in ("", ROOT):
        chain.append(current)
        current = posixpath.dirname(current)
    return chain or [path]


def remove_one(shell, path):
    """Удаляет один пустой каталог, ошибки приводит к CommandError."""
    try:
        shell.vfs.remove_dir(path)
    except VfsError as exc:
        raise CommandError(f"failed to remove '{path}': {exc}") from exc


def cmd_rmdir(shell, args):
    """rmdir [-p] КАТАЛОГ... - удаляет пустые каталоги в памяти.

    С -p после каталога удаляются и его пустые родители.
    """
    flags, paths = split_options(args, "p")
    if not paths:
        raise CommandError("missing operand")
    for path in paths:
        targets = path_chain(path) if "p" in flags else [path]
        for target in targets:
            remove_one(shell, target)
    return ""


FS_COMMANDS = {
    "chown": cmd_chown,
    "rmdir": cmd_rmdir,
}
