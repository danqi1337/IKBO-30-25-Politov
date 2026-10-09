"""Ядро эмулятора: выполнение введённых команд."""

from dataclasses import dataclass

from emulator.commands import COMMANDS
from emulator.errors import CommandError
from emulator.logger import STATUS_ERROR, STATUS_OK
from emulator.parser import ParseError, parse
from emulator.sysinfo import get_hostname, get_username
from emulator.vfs import default_vfs


@dataclass
class Result:
    """Результат выполнения строки: вывод и признак ошибки."""

    output: str = ""
    is_error: bool = False


class Shell:
    """Состояние эмулятора и выполнение команд."""

    def __init__(self, vfs=None, logger=None):
        """Создаёт оболочку с файловой системой vfs и журналом logger."""
        self.logger = logger
        self.user = get_username()
        self.vfs = vfs if vfs is not None else default_vfs(self.user)
        self.host = get_hostname()
        self.running = True

    def prompt(self):
        """Возвращает приглашение вида user@host:/путь$ ."""
        return f"{self.user}@{self.host}:{self.vfs.pwd()}$ "

    def execute(self, line):
        """Разбирает и выполняет строку, возвращает Result."""
        try:
            tokens = parse(line)
        except ParseError as exc:
            result = Result(f"parse error: {exc}", True)
            self._log("", [line], result)
            return result
        if not tokens:
            return Result()
        result = self._dispatch(tokens[0], tokens[1:])
        self._log(tokens[0], tokens[1:], result)
        return result

    def interact(self, line, write):
        """Показывает ввод, выполняет его и показывает вывод."""
        write(self.prompt() + line)
        result = self.execute(line)
        if result.output:
            write(result.output)
        return result

    def _log(self, name, args, result):
        """Записывает вызов команды в журнал, если он включён."""
        if self.logger is None:
            return
        status = STATUS_ERROR if result.is_error else STATUS_OK
        self.logger.log(self.user, name, args, status)

    def _dispatch(self, name, args):
        """Вызывает обработчик команды name с аргументами args."""
        handler = COMMANDS.get(name)
        if handler is None:
            return Result(f"{name}: command not found", True)
        try:
            return Result(handler(self, args))
        except CommandError as exc:
            return Result(f"{name}: {exc}", True)
