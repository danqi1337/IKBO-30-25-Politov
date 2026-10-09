"""Тесты стартовых скриптов."""

import os
import tempfile
import unittest

from emulator.script import ScriptError, read_script, run_script
from emulator.shell import Shell


class ScriptTest(unittest.TestCase):
    """Проверки чтения и выполнения скриптов."""

    def test_comments_and_blank_lines_skipped(self):
        """Комментарии и пустые строки не выполняются и не печатаются."""
        shell = Shell()
        out = []
        run_script(shell, ["# note", "", "  ", "cd /x  # tail"], out.append)
        self.assertEqual(len(out), 2)
        self.assertTrue(out[0].endswith("cd /x  # tail"))
        self.assertEqual(out[1], "cd: args=['/x']")

    def test_input_and_output_are_shown(self):
        """Выводятся и ввод (с приглашением), и результат."""
        shell = Shell()
        out = []
        run_script(shell, ["ls a", "bogus"], out.append)
        self.assertEqual(out[0], shell.prompt() + "ls a")
        self.assertEqual(out[2], shell.prompt() + "bogus")
        self.assertEqual(out[3], "bogus: command not found")

    def test_errors_do_not_stop_script(self):
        """После ошибки скрипт продолжает работу."""
        shell = Shell()
        out = []
        run_script(shell, ["bogus", "cd q"], out.append)
        self.assertIn("cd: args=['q']", out)

    def test_error_line_number_reported(self):
        """Для ошибочной строки сообщается её номер."""
        shell = Shell()
        out = []
        run_script(shell, ["# c", "cd a", "bogus"], out.append)
        self.assertEqual(
            out[-1], "[скрипт] ошибка в строке 3, строка пропущена")

    def test_exit_stops_script(self):
        """exit прерывает выполнение скрипта."""
        shell = Shell()
        out = []
        run_script(shell, ["exit", "ls"], out.append)
        self.assertEqual(len(out), 1)
        self.assertFalse(shell.running)

    def test_read_missing_script(self):
        """Чтение несуществующего скрипта — ScriptError."""
        with self.assertRaises(ScriptError):
            read_script("/nonexistent/script.esh")

    def test_read_script_lines(self):
        """read_script возвращает строки файла."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.esh")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("ls\ncd /\n")
            self.assertEqual(read_script(path), ["ls", "cd /"])


if __name__ == "__main__":
    unittest.main()
