"""Журнал вызовов команд в формате CSV."""

import csv
import json
import os
from datetime import datetime

FIELDS = ["timestamp", "user", "command", "arguments", "status"]
STATUS_OK = "ok"
STATUS_ERROR = "error"


class LogError(Exception):
    """Ошибка работы с файлом журнала."""


class CsvLogger:
    """Дописывает события вызова команд в CSV-файл."""

    def __init__(self, path):
        """Открывает журнал path, при необходимости пишет заголовок."""
        self.path = path
        try:
            is_new = (not os.path.exists(path)
                      or os.path.getsize(path) == 0)
        except OSError as exc:
            raise LogError(self._message(exc)) from exc
        if is_new:
            self._append(FIELDS)

    def log(self, user, command, args, status):
        """Записывает событие: время, пользователь, команда, итог."""
        stamp = datetime.now().isoformat(timespec="seconds")
        arguments = json.dumps(args, ensure_ascii=False)
        self._append([stamp, user, command, arguments, status])

    def _append(self, row):
        """Добавляет строку row в конец файла."""
        try:
            with open(self.path, "a", newline="",
                      encoding="utf-8") as handle:
                csv.writer(handle).writerow(row)
        except OSError as exc:
            raise LogError(self._message(exc)) from exc

    def _message(self, exc):
        """Формирует понятное сообщение об ошибке журнала."""
        return f"не удалось записать журнал '{self.path}': {exc.strerror}"
