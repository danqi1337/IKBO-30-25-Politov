"""Тесты команд chown и rmdir (этап 5)."""

import os
import tempfile
import unittest

from helpers import OWNER, make_shell
from emulator.vfs import load_directory


def run(shell, line):
    """Выполняет строку и возвращает (вывод, признак ошибки)."""
    result = shell.execute(line)
    return result.output, result.is_error


class ChownTest(unittest.TestCase):
    """Проверки команды chown."""

    def setUp(self):
        """Создаёт оболочку с тестовой VFS."""
        self.shell = make_shell()
        self.vfs = self.shell.vfs

    def owner(self, path):
        """Возвращает владельца узла path."""
        return self.vfs.lookup(path).owner

    def test_change_file_owner(self):
        """Владелец файла меняется."""
        self.assertEqual(run(self.shell, "chown bob readme.txt"), ("", False))
        self.assertEqual(self.owner("readme.txt"), "bob")
        self.assertEqual(self.owner("empty.txt"), OWNER)

    def test_directory_without_r_is_not_recursive(self):
        """Без -R содержимое каталога не затрагивается."""
        run(self.shell, "chown bob home")
        self.assertEqual(self.owner("home"), "bob")
        self.assertEqual(self.owner("home/alex"), OWNER)

    def test_recursive(self):
        """С -R меняется всё поддерево."""
        run(self.shell, "chown -R bob home")
        self.assertEqual(self.owner("home/alex/docs/old/x.txt"), "bob")

    def test_several_paths(self):
        """Можно указать несколько путей."""
        run(self.shell, "chown bob readme.txt tmp")
        self.assertEqual(self.owner("tmp"), "bob")

    def test_owner_visible_in_ls(self):
        """Новый владелец виден в ls -l."""
        run(self.shell, "chown bob readme.txt")
        self.assertIn("- bob", run(self.shell, "ls -l readme.txt")[0])

    def test_errors(self):
        """Ошибки аргументов."""
        self.assertIn("missing operand", run(self.shell, "chown")[0])
        self.assertIn("after 'bob'", run(self.shell, "chown bob")[0])
        self.assertIn("No such file", run(self.shell, "chown bob nope")[0])
        for owner in ("1x", "a:b"):
            out = run(self.shell, f"chown {owner} readme.txt")[0]
            self.assertIn("invalid user", out)
        self.assertIn("invalid option", run(self.shell, "chown -x b f")[0])

    def test_error_changes_nothing(self):
        """При ошибке в одном из путей ничего не меняется."""
        self.assertTrue(run(self.shell, "chown bob readme.txt nope")[1])
        self.assertEqual(self.owner("readme.txt"), OWNER)


class RmdirTest(unittest.TestCase):
    """Проверки команды rmdir."""

    def setUp(self):
        """Создаёт оболочку с тестовой VFS."""
        self.shell = make_shell()

    def exists(self, path):
        """Проверяет наличие пути в VFS."""
        return not run(self.shell, f"ls {path}")[1]

    def test_remove_empty(self):
        """Пустой каталог удаляется."""
        self.assertEqual(run(self.shell, "rmdir tmp"), ("", False))
        self.assertFalse(self.exists("tmp"))

    def test_several_dirs(self):
        """Можно удалить несколько каталогов."""
        run(self.shell, "rmdir tmp home/alex/empty")
        self.assertFalse(self.exists("home/alex/empty"))

    def test_not_empty(self):
        """Непустой каталог не удаляется."""
        out, err = run(self.shell, "rmdir home/alex")
        self.assertTrue(err)
        self.assertEqual(out, "rmdir: failed to remove 'home/alex': "
                              "Directory not empty")
        self.assertTrue(self.exists("home/alex"))

    def test_file_and_missing(self):
        """Файл и несуществующий путь."""
        self.assertIn("Not a directory", run(self.shell, "rmdir readme.txt")[0])
        self.assertIn("No such file", run(self.shell, "rmdir nope")[0])
        self.assertTrue(run(self.shell, 'rmdir ""')[1])

    def test_cwd_and_root_are_busy(self):
        """Текущий каталог и корень удалить нельзя."""
        run(self.shell, "cd tmp")
        self.assertIn("busy", run(self.shell, "rmdir .")[0])
        self.assertIn("busy", run(self.shell, "rmdir /tmp")[0])
        self.assertIn("busy", run(self.shell, "rmdir /")[0])

    def test_parents_option(self):
        """С -p удаляется цепочка пустых каталогов."""
        shell = make_shell({"a": {"b": {"c": {}}}, "keep.txt": "x"})
        self.assertEqual(run(shell, "rmdir -p a/b/c"), ("", False))
        self.assertEqual(run(shell, "ls")[0], "keep.txt")

    def test_parents_option_stops_on_non_empty(self):
        """С -p удаление останавливается на непустом родителе."""
        shell = make_shell({"a": {"b": {}, "f.txt": "x"}})
        out, err = run(shell, "rmdir -p a/b")
        self.assertTrue(err)
        self.assertIn("failed to remove 'a'", out)
        self.assertEqual(run(shell, "ls a")[0], "f.txt")

    def test_no_operand(self):
        """Без аргументов - ошибка."""
        self.assertIn("missing operand", run(self.shell, "rmdir")[0])
        self.assertIn("invalid option", run(self.shell, "rmdir -x t")[0])

    def test_disk_is_not_touched(self):
        """Удаление в VFS не затрагивает каталог на диске."""
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "empty"))
            shell = make_shell()
            shell.vfs = load_directory(tmp, OWNER)
            self.assertEqual(run(shell, "rmdir empty"), ("", False))
            self.assertEqual(os.listdir(tmp), ["empty"])


if __name__ == "__main__":
    unittest.main()
