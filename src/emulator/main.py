"""Запуск эмулятора."""

import sys

from emulator.config import describe, parse_args
from emulator.console import run_console
from emulator.logger import CsvLogger, LogError
from emulator.script import ScriptError, read_script
from emulator.shell import Shell

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


def load_script(config, problems):
    """Читает стартовый скрипт; ошибки добавляет в problems."""
    if not config.script_path:
        return []
    try:
        return read_script(config.script_path)
    except ScriptError as exc:
        problems.append(str(exc))
        return []


def open_logger(config, problems):
    """Открывает журнал; при ошибке работает без журнала."""
    try:
        return CsvLogger(config.log_path)
    except LogError as exc:
        problems.append(f"{exc} (журнал отключён)")
        return None


def main(argv=None):
    """Разбирает параметры и запускает эмулятор.

    Ошибки скрипта и журнала выводятся в окно (консоль) вместе с
    параметрами запуска, работа эмулятора при этом продолжается.
    """
    config = parse_args(argv)
    problems = []
    lines = load_script(config, problems)
    shell = Shell(logger=open_logger(config, problems))
    banner = "\n".join([describe(config)]
                       + [f"Ошибка: {text}" for text in problems])
    if config.headless:
        return run_console(shell, lines, banner)
    return run_gui(shell, lines, banner)
