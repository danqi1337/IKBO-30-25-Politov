"""Тесты CSV-журнала."""

import csv
import os
import tempfile
import unittest

from emulator.logger import FIELDS, CsvLogger, LogError
from emulator.shell import Shell


def read_rows(path):
    """Читает все строки CSV-файла."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


class LoggerTest(unittest.TestCase):
    """Проверки журнала событий."""

    def setUp(self):
        """Создаёт временный каталог."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "log.csv")

    def test_header_written_once(self):
        """Заголовок пишется только в новый файл."""
        CsvLogger(self.path)
        CsvLogger(self.path)
        self.assertEqual(read_rows(self.path), [FIELDS])

    def test_shell_logs_commands(self):
        """Оболочка пишет в журнал и успешные, и ошибочные вызовы."""
        shell = Shell(logger=CsvLogger(self.path))
        shell.execute('ls "a b"')
        shell.execute("foo")
        rows = read_rows(self.path)[1:]
        self.assertEqual(rows[0][1:], [shell.user, "ls", '["a b"]', "ok"])
        self.assertEqual(rows[1][2], "foo")
        self.assertEqual(rows[1][4], "error")

    def test_timestamp_is_iso(self):
        """Время события записано в формате ISO 8601."""
        shell = Shell(logger=CsvLogger(self.path))
        shell.execute("ls")
        stamp = read_rows(self.path)[1][0]
        self.assertRegex(stamp, r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$")

    def test_bad_path_raises(self):
        """Недоступный путь — LogError."""
        bad = os.path.join(self.tmp.name, "no", "dir", "log.csv")
        with self.assertRaises(LogError):
            CsvLogger(bad)


if __name__ == "__main__":
    unittest.main()
