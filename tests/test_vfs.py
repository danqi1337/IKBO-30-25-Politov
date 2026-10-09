"""Тесты виртуальной файловой системы и её загрузки."""

import os
import tempfile
import unittest
from functools import cached_property

from helpers import make_shell
from emulator.vfs import (
    ERR_NOT_DIR, ERR_NOT_FOUND, Vfs, VfsError, default_vfs,
    load_directory,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VFS_DIR = os.path.join(ROOT, "tests", "vfs")


class VfsTest(unittest.TestCase):
    """Проверки навигации по VFS."""

    @cached_property
    def vfs(self):
        """VFS для проверок."""
        return make_shell().vfs

    def test_lookup_absolute_and_relative(self):
        """Абсолютные и относительные пути с . и .. ."""
        node = self.vfs.lookup("/home/alex/docs")
        self.assertTrue(node.is_dir)
        self.vfs.chdir("/home/alex")
        self.assertIs(self.vfs.lookup("docs/../docs/./old/.."), node)

    def test_dotdot_at_root_stays(self):
        """Выше корня подняться нельзя."""
        self.assertIs(self.vfs.lookup("/../.."), self.vfs.root)

    def test_missing_path(self):
        """Несуществующий путь — VfsError."""
        with self.assertRaises(VfsError) as ctx:
            self.vfs.lookup("/nope")
        self.assertEqual(str(ctx.exception), ERR_NOT_FOUND)

    def test_file_in_the_middle(self):
        """Путь через файл — это не каталог."""
        with self.assertRaises(VfsError) as ctx:
            self.vfs.lookup("readme.txt/x")
        self.assertEqual(str(ctx.exception), ERR_NOT_DIR)

    def test_pwd_and_chdir(self):
        """chdir меняет текущий каталог."""
        self.vfs.chdir("home/alex")
        self.assertEqual(self.vfs.pwd(), "/home/alex")
        self.vfs.chdir("/")
        self.assertEqual(self.vfs.pwd(), "/")

    def test_stats(self):
        """Подсчёт каталогов, файлов и байт."""
        vfs = Vfs.from_dict({"a": {"b.txt": "xyz"}, "c.txt": "12"}, "u")
        self.assertEqual(vfs.stats(), (1, 2, 5))


class LoadTest(unittest.TestCase):
    """Проверки загрузки VFS с диска."""

    def test_minimal(self):
        """Минимальная VFS: один файл."""
        vfs = load_directory(os.path.join(VFS_DIR, "minimal"), "u")
        self.assertEqual(vfs.stats()[:2], (0, 1))

    def test_several_files(self):
        """Несколько файлов в корне."""
        vfs = load_directory(os.path.join(VFS_DIR, "files"), "u")
        self.assertEqual(vfs.stats()[:2], (0, 5))
        self.assertIn("файл a", vfs.read_file("a.txt").lower())

    def test_deep_with_empty_dirs(self):
        """Вложенность от трёх уровней и пустые каталоги."""
        vfs = load_directory(os.path.join(VFS_DIR, "deep"), "u")
        deep = "home/alex/docs/old/archive/2020/report.txt"
        self.assertIn("Отчёт", vfs.read_file(deep))
        self.assertEqual(vfs.lookup("tmp").children, {})

    def test_missing_directory(self):
        """Нет каталога — VfsError."""
        with self.assertRaises(VfsError) as ctx:
            load_directory("/definitely/missing", "u")
        self.assertIn(ERR_NOT_FOUND, str(ctx.exception))

    def test_file_instead_of_directory(self):
        """Вместо каталога передан файл — неверный формат."""
        path = os.path.join(VFS_DIR, "minimal", "readme.txt")
        with self.assertRaises(VfsError) as ctx:
            load_directory(path, "u")
        self.assertIn("неверный формат", str(ctx.exception))

    def test_disk_is_not_modified(self):
        """Изменения в памяти не затрагивают диск."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "f.txt"), "w") as handle:
                handle.write("data")
            vfs = load_directory(tmp, "u")
            vfs.root.children.clear()
            self.assertEqual(os.listdir(tmp), ["f.txt"])

    def test_default_vfs(self):
        """VFS по умолчанию создаётся без диска."""
        vfs = default_vfs("u")
        self.assertIn("заметки", vfs.read_file("home/user/notes.txt"))


if __name__ == "__main__":
    unittest.main()
