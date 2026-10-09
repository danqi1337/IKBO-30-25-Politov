"""Запуск эмулятора."""

import sys

from emulator.config import describe, parse_args
from emulator.console import run_console
from emulator.logger import CsvLogger, LogError
from emulator.script import ScriptError, read_script
from emulator.shell import Shell
from emulator.sysinfo import get_username
from emulator.vfs import VfsError, Vfs, default_vfs, load_directory

EXIT_FAILURE = 1


def run_gui(shell, lines, banner):
    """Открывает графическое окно; возвращает код выхода."""
    try:
        from emulator.gui import EmulatorApp, GuiError
        app = EmulatorApp(shell)
    except (ImportError, GuiError) as exc:
        print(f"emulator: GUI unavailable ({exc}); try --headless",
              file=sys.stderr)
        return EXIT_FAILURE
    app.start(banner, lines)
    app.run()
    return 0


def load_script(config, notes):
    """Читает стартовый скрипт; ошибки добавляет в notes."""
    if not config.script_path:
        return []
    try:
        return read_script(config.script_path)
    except ScriptError as exc:
        notes.append(f"Ошибка: {exc}")
        return []


def open_logger(config, notes):
    """Открывает журнал; при ошибке работает без журнала."""
    try:
        return CsvLogger(config.log_path)
    except LogError as exc:
        notes.append(f"Ошибка: {exc} (журнал отключён)")
        return None


def load_vfs(config, notes):
    """Загружает VFS в память; при ошибке берёт пустую VFS."""
    owner = get_username()
    if not config.vfs_path:
        notes.append("VFS не указана, создана VFS по умолчанию")
        return default_vfs(owner)
    try:
        vfs = load_directory(config.vfs_path, owner)
    except VfsError as exc:
        notes.append(f"Ошибка загрузки VFS: {exc} (используется пустая VFS)")
        return Vfs.from_dict({}, owner)
    notes.append(f"VFS загружена из: {config.vfs_path}")
    return vfs


def main(argv=None):
    """Разбирает параметры и запускает эмулятор.

    Ошибки скрипта, журнала и VFS выводятся в окно (консоль) вместе с
    параметрами запуска, работа эмулятора при этом продолжается.
    """
    config = parse_args(argv)
    notes = []
    lines = load_script(config, notes)
    logger = open_logger(config, notes)
    shell = Shell(vfs=load_vfs(config, notes), logger=logger)
    banner = "\n".join([describe(config)] + notes)
    if config.headless:
        return run_console(shell, lines, banner)
    return run_gui(shell, lines, banner)
