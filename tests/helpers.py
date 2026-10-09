"""Вспомогательные функции для тестов."""

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
