"""Параметры командной строки эмулятора."""

import argparse
from dataclasses import dataclass

DEFAULT_LOG = "emulator_log.csv"
NOT_SET = "(не задан)"


@dataclass
class Config:
    """Параметры запуска эмулятора."""

    vfs_path: str | None
    log_path: str
    script_path: str | None
    headless: bool


def build_parser():
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="путь к физическому расположению VFS (каталог на диске)",
    )
    parser.add_argument(
        "--log", metavar="PATH", default=DEFAULT_LOG,
        help="путь к CSV-файлу журнала (по умолчанию %(default)s)",
    )
    parser.add_argument(
        "--script", metavar="PATH",
        help="путь к стартовому скрипту эмулятора",
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="консольный режим без графического окна",
    )
    return parser


def parse_args(argv=None):
    """Разбирает аргументы командной строки в Config."""
    args = build_parser().parse_args(argv)
    return Config(args.vfs, args.log, args.script, args.headless)


def describe(config):
    """Формирует отладочный вывод всех заданных параметров."""
    rows = [
        ("vfs", config.vfs_path or NOT_SET),
        ("log", config.log_path),
        ("script", config.script_path or NOT_SET),
        ("headless", "да" if config.headless else "нет"),
    ]
    lines = ["Параметры запуска:"]
    lines += [f"  {key:<9}{value}" for key, value in rows]
    return "\n".join(lines)
