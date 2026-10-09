"""Основные команды эмулятора: ls, cd, exit, vfsinfo."""

from emulator.errors import CommandError
from emulator.options import split_options
from emulator.textcmds import TEXT_COMMANDS
from emulator.vfs import VfsError

HIDDEN_PREFIX = "."


def entries_of(node, path, show_hidden):
    """Возвращает пары (имя, узел) для вывода ls."""
    if not node.is_dir:
        return [(path, node)]
    names = sorted(node.children)
    return [(name, node.children[name]) for name in names
            if show_hidden or not name.startswith(HIDDEN_PREFIX)]


def long_lines(entries):
    """Формирует подробный список: тип, владелец, размер, имя."""
    owner_width = max(len(node.owner) for _, node in entries)
    size_width = max(len(str(node.size)) for _, node in entries)
    lines = []
    for name, node in entries:
        kind = "d" if node.is_dir else "-"
        lines.append(f"{kind} {node.owner:<{owner_width}} "
                     f"{node.size:>{size_width}} {name}")
    return "\n".join(lines)


def format_entries(entries, long_mode):
    """Форматирует список записей в одну строку или таблицу."""
    if not entries:
        return ""
    if long_mode:
        return long_lines(entries)
    return "  ".join(name for name, _ in entries)


def list_target(shell, path, flags):
    """Строит вывод ls для одного пути."""
    try:
        node = shell.vfs.lookup(path)
    except VfsError as exc:
        raise CommandError(f"cannot access '{path}': {exc}") from exc
    entries = entries_of(node, path, "a" in flags)
    return format_entries(entries, "l" in flags)


def cmd_ls(shell, args):
    """ls [-l] [-a] [ПУТЬ...] - содержимое каталогов или имена файлов."""
    flags, paths = split_options(args, "la")
    targets = paths or ["."]
    blocks = [list_target(shell, path, flags) for path in targets]
    if not paths[1:]:
        return blocks[0]
    return "\n\n".join(f"{path}:\n{block}"
                       for path, block in zip(targets, blocks))


def cmd_cd(shell, args):
    """cd [ПУТЬ] - меняет текущий каталог (без аргумента - корень)."""
    if args[1:]:
        raise CommandError("too many arguments")
    target = args[0] if args else "/"
    try:
        shell.vfs.chdir(target)
    except VfsError as exc:
        raise CommandError(f"{target}: {exc}") from exc
    return ""


def cmd_exit(shell, args):
    """Завершает работу эмулятора."""
    if args:
        raise CommandError("too many arguments")
    shell.running = False
    return ""


def cmd_vfsinfo(shell, args):
    """Служебная команда: сведения о загруженной VFS."""
    if args:
        raise CommandError("too many arguments")
    dirs, files, size = shell.vfs.stats()
    source = shell.vfs.source or "(только в памяти)"
    return (f"source: {source}\ndirectories: {dirs}\n"
            f"files: {files}\nbytes: {size}")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "vfsinfo": cmd_vfsinfo,
    "exit": cmd_exit,
    **TEXT_COMMANDS,
}
