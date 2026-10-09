"""Сквозные тесты запуска эмулятора в консольном режиме."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
SCRIPTS = os.path.join(ROOT, "tests", "scripts")


def run_emulator(*args, stdin=""):
    """Запускает эмулятор подпроцессом и возвращает результат."""
    env = dict(os.environ, PYTHONPATH=SRC)
    return subprocess.run(
        [sys.executable, "-m", "emulator", "--headless", *args],
        input=stdin, capture_output=True, text=True, env=env,
        check=False,
    )


class CliTest(unittest.TestCase):
    """Проверки параметров командной строки."""

    def setUp(self):
        """Создаёт временный каталог для журнала."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log = os.path.join(self.tmp.name, "log.csv")

    def test_parameters_are_printed(self):
        """При запуске выводятся все заданные параметры."""
        proc = run_emulator("--log", self.log, "--vfs", "somewhere",
                            stdin="exit\n")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("somewhere", proc.stdout)
        self.assertIn(self.log, proc.stdout)

    def test_script_output_shows_input_and_output(self):
        """Скрипт выполняется, диалог виден на экране."""
        script = os.path.join(SCRIPTS, "test_stage2.txt")
        proc = run_emulator("--log", self.log, "--script", script)
        self.assertIn("$ cd /usr/local", proc.stdout)
        self.assertIn("cd: /usr/local: No such file", proc.stdout)
        self.assertIn("foo: command not found", proc.stdout)
        self.assertTrue(os.path.exists(self.log))

    def test_missing_script_reported(self):
        """Несуществующий скрипт: ошибка на экране, работа продолжается."""
        proc = run_emulator("--log", self.log, "--script", "nope.esh",
                            stdin="exit\n")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("не удалось прочитать скрипт", proc.stdout)

    def test_bad_log_path_reported(self):
        """Недоступный журнал: ошибка на экране, журнал отключён."""
        bad = os.path.join(self.tmp.name, "no", "dir", "log.csv")
        proc = run_emulator("--log", bad, stdin="ls\nexit\n")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("журнал отключён", proc.stdout)


if __name__ == "__main__":
    unittest.main()
