"""Тесты разбора командной строки."""

import unittest

from emulator.parser import ParseError, parse


class ParserTest(unittest.TestCase):
    """Проверки функции parse."""

    def test_simple_words(self):
        """Слова разделяются пробелами."""
        self.assertEqual(parse("ls -l  /tmp"), ["ls", "-l", "/tmp"])

    def test_empty_line(self):
        """Пустая строка даёт пустой список."""
        self.assertEqual(parse("   "), [])

    def test_double_quotes(self):
        """Двойные кавычки сохраняют пробелы."""
        self.assertEqual(parse('cd "my dir"'), ["cd", "my dir"])

    def test_single_quotes(self):
        """Одинарные кавычки сохраняют пробелы и обратный слэш."""
        self.assertEqual(parse(r"ls 'a \n b'"), ["ls", r"a \n b"])

    def test_empty_quotes(self):
        """Пустые кавычки дают пустой аргумент."""
        self.assertEqual(parse('ls ""'), ["ls", ""])

    def test_adjacent_quotes(self):
        """Соседние фрагменты склеиваются в одно слово."""
        self.assertEqual(parse("ls a'b c'\"d\""), ["ls", "ab cd"])

    def test_escaped_quote(self):
        """Экранированная кавычка внутри двойных кавычек."""
        self.assertEqual(parse(r'ls "a\"b"'), ["ls", 'a"b'])

    def test_escaped_space(self):
        """Экранированный пробел не разделяет слова."""
        self.assertEqual(parse(r"ls a\ b"), ["ls", "a b"])

    def test_unterminated_quote(self):
        """Незакрытая кавычка — ошибка."""
        with self.assertRaises(ParseError):
            parse('ls "abc')

    def test_trailing_backslash(self):
        """Обратный слэш в конце строки — ошибка."""
        with self.assertRaises(ParseError):
            parse("ls abc\\")


if __name__ == "__main__":
    unittest.main()
