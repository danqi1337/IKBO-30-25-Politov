"""Вспомогательные функции и базовые классы для тестов."""

import tempfile
import unittest
from functools import cached_property

from emulator.shell import Shell
from emulator.vfs import Vfs

OWNER = "alice"

SAMPLE_TREE = {
    "readme.txt": "первая\nвторая\nтретья\n",
    "empty.txt": "",
    "numbers.txt": "".join(f"{i}\n" for i in range(1, 16)),
    "home": {
        "alex": {
            "notes.txt": "a\nb\n",
            "docs": {"plan.txt": "план\n", "old": {"x.txt": "x\n"}},
            "empty": {},
        },
    },
    "tmp": {},
}


def make_shell(tree=None):
    """Создаёт оболочку с VFS из словаря (по умолчанию SAMPLE_TREE)."""
    tree = SAMPLE_TREE if tree is None else tree
    shell = Shell(vfs=Vfs.from_dict(tree, OWNER))
    shell.user = OWNER
    return shell


class ShellCase(unittest.TestCase):
    """Базовый класс: свежая оболочка с тестовой VFS в каждом тесте."""

    @cached_property
    def shell(self):
        """Оболочка, создаваемая при первом обращении в тесте."""
        return make_shell()


class TempDirCase(unittest.TestCase):
    """Базовый класс: временный каталог, удаляемый после теста."""

    @cached_property
    def tmp(self):
        """Временный каталог, создаваемый при первом обращении."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return directory
