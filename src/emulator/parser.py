"""Разбор командной строки на слова с поддержкой кавычек."""

QUOTES = "'\""
ESCAPE = "\\"
COMMENT = "#"
DOUBLE_ESCAPABLE = '"\\'


class ParseError(ValueError):
    """Ошибка разбора строки (например, незакрытая кавычка)."""


class _Tokenizer:
    """Конечный автомат, разбивающий строку на слова."""

    def __init__(self, line):
        """Подготавливает разбор строки line."""
        self.line = line
        self.tokens = []
        self.buf = []
        self.in_token = False
        self.quote = None
        self.pos = 0

    def run(self):
        """Разбирает строку и возвращает список слов."""
        while self.pos < len(self.line):
            char = self.line[self.pos]
            self.pos += 1
            if self.quote:
                self._in_quote(char)
            else:
                self._plain(char)
        if self.quote:
            raise ParseError(f"unterminated quote {self.quote}")
        self._flush()
        return self.tokens

    def _plain(self, char):
        """Обрабатывает символ вне кавычек."""
        if char.isspace():
            self._flush()
        elif char == COMMENT and not self.in_token:
            self.pos = len(self.line)
        elif char in QUOTES:
            self.quote = char
            self.in_token = True
        elif char == ESCAPE:
            self._escape()
        else:
            self._add(char)

    def _in_quote(self, char):
        """Обрабатывает символ внутри кавычек."""
        if char == self.quote:
            self.quote = None
        elif char == ESCAPE and self.quote == '"':
            self._escape_in_double()
        else:
            self._add(char)

    def _escape(self):
        """Добавляет символ, экранированный обратной косой чертой."""
        if self.pos >= len(self.line):
            raise ParseError("trailing backslash")
        self._add(self.line[self.pos])
        self.pos += 1

    def _escape_in_double(self):
        """Обрабатывает обратную косую черту в двойных кавычках."""
        following = self.line[self.pos:self.pos + 1]
        if following and following in DOUBLE_ESCAPABLE:
            self._add(following)
            self.pos += 1
        else:
            self._add(ESCAPE)

    def _add(self, char):
        """Добавляет символ к текущему слову."""
        self.buf.append(char)
        self.in_token = True

    def _flush(self):
        """Завершает текущее слово, если оно начато."""
        if self.in_token:
            self.tokens.append("".join(self.buf))
        self.buf = []
        self.in_token = False


def parse(line):
    """Разбивает строку на слова: [команда, аргумент, ...].

    Аргументы в одинарных и двойных кавычках сохраняют пробелы,
    пустые кавычки дают пустой аргумент. Символ # в начале слова
    начинает комментарий до конца строки. При ошибке выбрасывается
    ParseError.
    """
    return _Tokenizer(line).run()
