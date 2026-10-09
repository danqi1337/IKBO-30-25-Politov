"""Сведения об ОС, в которой запущен эмулятор."""

import getpass
import socket

DEFAULT_USER = "user"
DEFAULT_HOST = "localhost"


def get_username():
    """Возвращает имя текущего пользователя ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return DEFAULT_USER


def get_hostname():
    """Возвращает сетевое имя компьютера."""
    return socket.gethostname() or DEFAULT_HOST


def window_title():
    """Формирует заголовок окна по реальным данным ОС."""
    return f"Эмулятор - [{get_username()}@{get_hostname()}]"
