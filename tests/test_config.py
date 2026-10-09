"""Тесты параметров командной строки."""

import unittest

from emulator.config import DEFAULT_LOG, describe, parse_args


class ConfigTest(unittest.TestCase):
    """Проверки parse_args и describe."""

    def test_defaults(self):
        """Без аргументов используются значения по умолчанию."""
        config = parse_args([])
        self.assertIsNone(config.vfs_path)
        self.assertIsNone(config.script_path)
        self.assertEqual(config.log_path, DEFAULT_LOG)
        self.assertFalse(config.headless)

    def test_all_parameters(self):
        """Все параметры попадают в Config."""
        config = parse_args(
            ["--vfs", "v", "--log", "l.csv", "--script", "s.esh",
             "--headless"]
        )
        self.assertEqual(config.vfs_path, "v")
        self.assertEqual(config.log_path, "l.csv")
        self.assertEqual(config.script_path, "s.esh")
        self.assertTrue(config.headless)

    def test_describe_lists_every_parameter(self):
        """Отладочный вывод содержит все параметры."""
        config = parse_args(["--vfs", "v", "--script", "s.esh"])
        text = describe(config)
        for expected in ("vfs", "v", "log", DEFAULT_LOG, "s.esh"):
            self.assertIn(expected, text)

    def test_unknown_option_exits(self):
        """Неизвестный параметр приводит к завершению с ошибкой."""
        with self.assertRaises(SystemExit):
            parse_args(["--bogus"])


if __name__ == "__main__":
    unittest.main()
