"""Виртуальная файловая система, целиком хранящаяся в памяти."""

import os

ERR_NOT_FOUND = "No such file or directory"
ERR_NOT_DIR = "Not a directory"
ERR_IS_DIR = "Is a directory"
ERR_NOT_EMPTY = "Directory not empty"
ERR_BUSY = "Device or resource busy"
PLACEHOLDER = ".gitkeep"

DEFAULT_TREE = {
    "readme.txt": "Это VFS по умолчанию\n",
    "home": {"user": {"notes.txt": "Мои заметки\n"}},
}


class VfsError(Exception):
    """Ошибка загрузки VFS или операции над ней."""


class Node:
    """Узел дерева VFS: файл или каталог."""

    def __init__(self, name, is_dir, owner, data=b""):
        """Создаёт узел без родителя и без потомков."""
        self.name = name
        self.is_dir = is_dir
        self.owner = owner
        self.data = data
        self.parent = None
        self.children = {}

    @property
    def size(self):
        """Размер содержимого файла в байтах."""
        return len(self.data)

    def text(self):
        """Содержимое файла как текст UTF-8."""
        return self.data.decode("utf-8", errors="replace")

    def add(self, child):
        """Добавляет потомка в каталог."""
        child.parent = self
        self.children[child.name] = child

    def remove(self):
        """Отсоединяет узел от родительского каталога."""
        del self.parent.children[self.name]
        self.parent = None


def _add_tree(parent, tree, owner):
    """Рекурсивно создаёт узлы по вложенному словарю tree."""
    for name, value in tree.items():
        if isinstance(value, dict):
            child = Node(name, True, owner)
            _add_tree(child, value, owner)
        else:
            data = value if isinstance(value, bytes) else value.encode()
            child = Node(name, False, owner, data)
        parent.add(child)


class Vfs:
    """Дерево каталогов и файлов в памяти с текущим каталогом."""

    def __init__(self, root, source=None):
        """Создаёт VFS с корнем root; source - откуда она загружена."""
        self.root = root
        self.cwd = root
        self.source = source

    @classmethod
    def from_dict(cls, tree, owner, source=None):
        """Строит VFS из словаря {имя: текст | bytes | словарь}."""
        root = Node("", True, owner)
        _add_tree(root, tree, owner)
        return cls(root, source)

    def lookup(self, path):
        """Находит узел по абсолютному или относительному пути."""
        if not path:
            raise VfsError(ERR_NOT_FOUND)
        node = self.root if path.startswith("/") else self.cwd
        for part in path.split("/"):
            node = self._step(node, part)
        return node

    def _step(self, node, part):
        """Делает один шаг пути из каталога node по имени part."""
        if not node.is_dir:
            raise VfsError(ERR_NOT_DIR)
        if part in ("", "."):
            return node
        if part == "..":
            return node.parent or node
        child = node.children.get(part)
        if child is None:
            raise VfsError(ERR_NOT_FOUND)
        return child

    def path_of(self, node):
        """Возвращает абсолютный путь узла."""
        parts = []
        while node.parent is not None:
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts))

    def pwd(self):
        """Абсолютный путь текущего каталога."""
        return self.path_of(self.cwd)

    def chdir(self, path):
        """Делает каталог path текущим."""
        node = self.lookup(path)
        if not node.is_dir:
            raise VfsError(ERR_NOT_DIR)
        self.cwd = node

    def read_file(self, path):
        """Возвращает текст файла path."""
        node = self.lookup(path)
        if node.is_dir:
            raise VfsError(ERR_IS_DIR)
        return node.text()

    def set_owner(self, node, owner, recursive):
        """Назначает владельца узлу, при recursive - и всему поддереву."""
        node.owner = owner
        if recursive:
            for child in node.children.values():
                self.set_owner(child, owner, True)

    def _holds_cwd(self, node):
        """Истинно, если node - текущий каталог или его предок."""
        current = self.cwd
        while current is not None:
            if current is node:
                return True
            current = current.parent
        return False

    def remove_dir(self, path):
        """Удаляет пустой каталог path (только в памяти)."""
        node = self.lookup(path)
        if not node.is_dir:
            raise VfsError(ERR_NOT_DIR)
        if node.parent is None:
            raise VfsError(ERR_BUSY)
        if node.children:
            raise VfsError(ERR_NOT_EMPTY)
        if self._holds_cwd(node):
            raise VfsError(ERR_BUSY)
        node.remove()

    def stats(self):
        """Возвращает (каталогов без корня, файлов, байт)."""
        dirs = files = size = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.is_dir:
                dirs += 1
                stack.extend(node.children.values())
            else:
                files += 1
                size += node.size
        return dirs - 1, files, size


def _read_file(path):
    """Читает файл с диска целиком (в память)."""
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError as exc:
        raise VfsError(f"{path}: {exc.strerror}") from exc


def _read_dir(path):
    """Читает каталог с диска во вложенный словарь."""
    try:
        names = sorted(os.listdir(path))
    except OSError as exc:
        raise VfsError(f"{path}: {exc.strerror}") from exc
    tree = {}
    for name in names:
        full = os.path.join(path, name)
        if os.path.islink(full) or name == PLACEHOLDER:
            continue
        if os.path.isdir(full):
            tree[name] = _read_dir(full)
        elif os.path.isfile(full):
            tree[name] = _read_file(full)
    return tree


def load_directory(path, owner):
    """Загружает каталог path с диска в память как VFS.

    Файлы .gitkeep (заглушки для пустых каталогов в git) и символьные
    ссылки пропускаются. Диск после загрузки больше не используется.
    """
    if not os.path.exists(path):
        raise VfsError(f"{path}: {ERR_NOT_FOUND}")
    if not os.path.isdir(path):
        raise VfsError(f"{path}: неверный формат, VFS должна быть каталогом")
    return Vfs.from_dict(_read_dir(path), owner, source=path)


def default_vfs(owner):
    """Создаёт небольшую VFS по умолчанию (без обращения к диску)."""
    return Vfs.from_dict(DEFAULT_TREE, owner)
