"""Тесты ядра оболочки (этап 1)."""

import unittest

from emulator.shell import Shell
from emulator.sysinfo import window_title


class ShellTest(unittest.TestCase):
    """Проверки выполнения команд-заглушек и ошибок."""

    def setUp(self):
        """Создаёт оболочку."""
        self.shell = Shell()

    def test_quoted_argument_is_one_path(self):
        """Аргумент в кавычках с пробелом — один путь."""
        result = self.shell.execute('ls "a b"')
        self.assertTrue(result.is_error)
        self.assertIn("'a b'", result.output)

    def test_ls_lists_root(self):
        """ls без аргументов показывает корень VFS."""
        result = self.shell.execute("ls")
        self.assertEqual(result.output, "home  readme.txt")

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        result = self.shell.execute("foo bar")
        self.assertTrue(result.is_error)
        self.assertEqual(result.output, "foo: command not found")

    def test_bad_arguments(self):
        """Лишние аргументы — ошибка."""
        result = self.shell.execute("cd a b")
        self.assertTrue(result.is_error)
        self.assertIn("too many arguments", result.output)

    def test_parse_error_reported(self):
        """Ошибка разбора выводится пользователю."""
        result = self.shell.execute('ls "oops')
        self.assertTrue(result.is_error)
        self.assertIn("unterminated quote", result.output)

    def test_empty_line_is_ignored(self):
        """Пустая строка ничего не делает."""
        result = self.shell.execute("   ")
        self.assertEqual(result.output, "")
        self.assertFalse(result.is_error)

    def test_exit_stops_shell(self):
        """exit останавливает оболочку."""
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)

    def test_exit_with_args_fails(self):
        """exit с аргументами не завершает работу."""
        result = self.shell.execute("exit now")
        self.assertTrue(result.is_error)
        self.assertTrue(self.shell.running)

    def test_interact_echoes_input(self):
        """interact показывает приглашение, ввод и вывод."""
        lines = []
        self.shell.interact("cd x", lines.append)
        self.assertEqual(lines[0], self.shell.prompt() + "cd x")
        self.assertEqual(len(lines), 2)

    def test_vfsinfo(self):
        """Служебная команда vfsinfo показывает сведения о VFS."""
        result = self.shell.execute("vfsinfo")
        self.assertIn("directories: 2", result.output)
        self.assertIn("files: 2", result.output)

    def test_prompt_shows_vfs_path(self):
        """Приглашение содержит текущий путь VFS."""
        self.assertTrue(self.shell.prompt().endswith(":/$ "))

    def test_window_title_has_user_and_host(self):
        """Заголовок содержит user@host."""
        title = window_title()
        self.assertIn(f"{self.shell.user}@{self.shell.host}", title)
        self.assertTrue(title.startswith("Эмулятор - ["))


if __name__ == "__main__":
    unittest.main()
