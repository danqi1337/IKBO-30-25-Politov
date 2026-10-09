"""Тесты команд ls, cd, tail, tac (этап 4)."""

import unittest

from helpers import make_shell


def run(shell, line):
    """Выполняет строку и возвращает (вывод, признак ошибки)."""
    result = shell.execute(line)
    return result.output, result.is_error


class LsTest(unittest.TestCase):
    """Проверки команды ls."""

    def setUp(self):
        """Создаёт оболочку с тестовой VFS."""
        self.shell = make_shell()

    def test_root_listing_sorted(self):
        """Имена отсортированы."""
        out, err = run(self.shell, "ls")
        self.assertFalse(err)
        self.assertEqual(out, "empty.txt  home  numbers.txt  readme.txt  tmp")

    def test_path_argument(self):
        """ls ПУТЬ показывает указанный каталог."""
        self.assertEqual(run(self.shell, "ls home/alex")[0],
                         "docs  empty  notes.txt")

    def test_file_argument(self):
        """ls ФАЙЛ выводит имя файла."""
        self.assertEqual(run(self.shell, "ls readme.txt")[0], "readme.txt")

    def test_long_format(self):
        """ls -l показывает тип, владельца и размер."""
        out, _ = run(self.shell, "ls -l home/alex")
        self.assertIn("d alice", out)
        self.assertIn("- alice 4 notes.txt", out.replace("  ", " "))

    def test_hidden_files(self):
        """Скрытые файлы видны только с -a."""
        shell = make_shell({".hid": "x", "vis": "y"})
        self.assertEqual(run(shell, "ls")[0], "vis")
        self.assertEqual(run(shell, "ls -a")[0], ".hid  vis")
        self.assertEqual(run(shell, "ls -a -l")[0], run(shell, "ls -la")[0])

    def test_multiple_paths_have_headers(self):
        """Несколько путей — заголовки с именами."""
        out, _ = run(self.shell, "ls tmp home")
        self.assertIn("tmp:\n\n\nhome:\nalex", out)

    def test_empty_directory(self):
        """Пустой каталог даёт пустой вывод."""
        self.assertEqual(run(self.shell, "ls tmp"), ("", False))

    def test_errors(self):
        """Несуществующий путь и неверные опции."""
        out, err = run(self.shell, "ls nope")
        self.assertTrue(err)
        self.assertEqual(out, "ls: cannot access 'nope': "
                              "No such file or directory")
        self.assertIn("invalid option -- 'z'", run(self.shell, "ls -z")[0])
        self.assertIn("unrecognized option", run(self.shell, "ls --x")[0])
        self.assertTrue(run(self.shell, 'ls ""')[1])


class CdTest(unittest.TestCase):
    """Проверки команды cd."""

    def setUp(self):
        """Создаёт оболочку с тестовой VFS."""
        self.shell = make_shell()

    def test_cd_changes_prompt(self):
        """cd меняет каталог и приглашение."""
        run(self.shell, "cd home/alex")
        self.assertTrue(self.shell.prompt().endswith(":/home/alex$ "))
        self.assertEqual(run(self.shell, "ls docs")[0], "old  plan.txt")

    def test_cd_without_args_goes_to_root(self):
        """cd без аргументов возвращает в корень."""
        run(self.shell, "cd home/alex")
        run(self.shell, "cd")
        self.assertEqual(self.shell.vfs.pwd(), "/")

    def test_cd_dotdot(self):
        """cd .. поднимается на уровень выше."""
        run(self.shell, "cd /home/alex/docs")
        run(self.shell, "cd ../..")
        self.assertEqual(self.shell.vfs.pwd(), "/home")

    def test_cd_errors(self):
        """Ошибки: нет каталога, файл, лишние аргументы."""
        self.assertEqual(run(self.shell, "cd nope")[0],
                         "cd: nope: No such file or directory")
        self.assertEqual(run(self.shell, "cd readme.txt")[0],
                         "cd: readme.txt: Not a directory")
        self.assertIn("too many", run(self.shell, "cd a b")[0])
        self.assertEqual(self.shell.vfs.pwd(), "/")


class TailTest(unittest.TestCase):
    """Проверки команды tail."""

    def setUp(self):
        """Создаёт оболочку с тестовой VFS."""
        self.shell = make_shell()

    def test_default_ten_lines(self):
        """По умолчанию выводятся последние 10 строк."""
        lines = run(self.shell, "tail numbers.txt")[0].split("\n")
        self.assertEqual(lines, [str(i) for i in range(6, 16)])

    def test_short_file_fully_printed(self):
        """Короткий файл выводится целиком."""
        self.assertEqual(run(self.shell, "tail readme.txt")[0],
                         "первая\nвторая\nтретья")

    def test_count_forms(self):
        """Формы -n N, -nN и -N эквивалентны."""
        expected = "14\n15"
        for form in ("-n 2", "-n2", "-2"):
            out, _ = run(self.shell, f"tail {form} numbers.txt")
            self.assertEqual(out, expected, form)

    def test_zero_lines(self):
        """-n 0 ничего не выводит."""
        self.assertEqual(run(self.shell, "tail -n 0 numbers.txt")[0], "")

    def test_empty_file(self):
        """Пустой файл даёт пустой вывод."""
        self.assertEqual(run(self.shell, "tail empty.txt"), ("", False))

    def test_several_files_have_headers(self):
        """Для нескольких файлов выводятся заголовки."""
        out, _ = run(self.shell, "tail -n 1 readme.txt home/alex/notes.txt")
        self.assertEqual(
            out, "==> readme.txt <==\nтретья\n\n"
                 "==> home/alex/notes.txt <==\nb")

    def test_errors(self):
        """Ошибки аргументов и чтения."""
        self.assertIn("missing file operand", run(self.shell, "tail")[0])
        self.assertIn("No such file", run(self.shell, "tail nope")[0])
        self.assertIn("Is a directory", run(self.shell, "tail home")[0])
        self.assertIn("invalid number", run(self.shell, "tail -n x f")[0])
        self.assertIn("requires an argument", run(self.shell, "tail -n")[0])
        self.assertIn("invalid option", run(self.shell, "tail -z f")[0])


class TacTest(unittest.TestCase):
    """Проверки команды tac."""

    def setUp(self):
        """Создаёт оболочку с тестовой VFS."""
        self.shell = make_shell()

    def test_reverses_lines(self):
        """Строки выводятся в обратном порядке."""
        self.assertEqual(run(self.shell, "tac readme.txt")[0],
                         "третья\nвторая\nпервая")

    def test_several_files(self):
        """Файлы обрабатываются по очереди."""
        out, _ = run(self.shell, "tac home/alex/notes.txt readme.txt")
        self.assertEqual(out, "b\na\nтретья\nвторая\nпервая")

    def test_errors(self):
        """Ошибки: нет операнда, нет файла, каталог, опции."""
        self.assertIn("missing file operand", run(self.shell, "tac")[0])
        self.assertIn("No such file", run(self.shell, "tac nope")[0])
        self.assertIn("Is a directory", run(self.shell, "tac home")[0])
        self.assertIn("not supported", run(self.shell, "tac -x f")[0])


if __name__ == "__main__":
    unittest.main()
