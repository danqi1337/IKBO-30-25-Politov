"""Консольный режим работы эмулятора (без окна)."""

from emulator.script import run_script


def run_console(shell, lines, banner, write=print, read=input):
    """Показывает баннер, выполняет скрипт, затем читает ввод."""
    write(banner)
    run_script(shell, lines, write)
    while shell.running:
        try:
            line = read(shell.prompt())
        except EOFError:
            write("")
            break
        result = shell.execute(line)
        if result.output:
            write(result.output)
    return 0
