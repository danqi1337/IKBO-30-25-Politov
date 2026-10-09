"""Ядро эмулятора: выполнение введённых команд."""

from dataclasses import dataclass

from emulator.commands import COMMANDS
from emulator.errors import CommandError
from emulator.parser import ParseError, parse
from emulator.sysinfo import get_hostname, get_username


@dataclass
class Result:
    """Результат выполнения строки: вывод и признак ошибки."""

    output: str = ""
    is_error: bool = False


class Shell:
    """Состояние эмулятора и выполнение команд."""

    def __init__(self):
        """Создаёт оболочку для текущего пользователя ОС."""
        self.user = get_username()
        self.host = get_hostname()
        self.running = True

    def prompt(self):
        """Возвращает приглашение вида user@host:~$ ."""
        return f"{self.user}@{self.host}:~$ "

    def execute(self, line):
        """Разбирает и выполняет строку, возвращает Result."""
        try:
            tokens = parse(line)
        except ParseError as exc:
            return Result(f"parse error: {exc}", True)
        if not tokens:
            return Result()
        return self._dispatch(tokens[0], tokens[1:])

    def interact(self, line, write):
        """Показывает ввод, выполняет его и показывает вывод."""
        write(self.prompt() + line)
        result = self.execute(line)
        if result.output:
            write(result.output)
        return result

    def _dispatch(self, name, args):
        """Вызывает обработчик команды name с аргументами args."""
        handler = COMMANDS.get(name)
        if handler is None:
            return Result(f"{name}: command not found", True)
        try:
            return Result(handler(self, args))
        except CommandError as exc:
            return Result(f"{name}: {exc}", True)
