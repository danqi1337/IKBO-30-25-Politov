"""Команды эмулятора (ls и cd пока заглушки)."""

from emulator.errors import CommandError


def stub_output(name, args):
    """Формирует вывод заглушки: имя команды и её аргументы."""
    return f"{name}: args={args}"


def cmd_ls(shell, args):
    """Заглушка ls: печатает своё имя и аргументы."""
    return stub_output("ls", args)


def cmd_cd(shell, args):
    """Заглушка cd: печатает своё имя и аргументы."""
    if args[1:]:
        raise CommandError("too many arguments")
    return stub_output("cd", args)


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
}
