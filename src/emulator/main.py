"""Запуск эмулятора."""

from emulator.gui import EmulatorApp
from emulator.shell import Shell


def main(argv=None):
    """Запускает графический эмулятор; возвращает код выхода."""
    app = EmulatorApp(Shell())
    app.run()
    return 0
