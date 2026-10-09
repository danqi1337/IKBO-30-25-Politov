"""Графический интерфейс эмулятора (tkinter)."""

import tkinter as tk
from tkinter import scrolledtext

from emulator.script import run_script
from emulator.sysinfo import window_title

FONT = ("Courier", 11)
TEXT_ROWS = 24
TEXT_COLUMNS = 90


class GuiError(Exception):
    """Графический интерфейс недоступен (нет дисплея и т. п.)."""


class EmulatorApp:
    """Окно эмулятора: область вывода и строка ввода."""

    def __init__(self, shell):
        """Создаёт окно для оболочки shell."""
        self.shell = shell
        self.history = []
        self.history_pos = 0
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            raise GuiError(str(exc)) from exc
        self.root.title(window_title())
        self._build_widgets()
        self._refresh_prompt()

    def _build_widgets(self):
        """Создаёт область вывода и строку ввода."""
        self.output = scrolledtext.ScrolledText(
            self.root, state="disabled", wrap="word", font=FONT,
            height=TEXT_ROWS, width=TEXT_COLUMNS,
        )
        self.output.pack(fill="both", expand=True)
        frame = tk.Frame(self.root)
        frame.pack(fill="x")
        self.prompt_label = tk.Label(frame, font=FONT)
        self.prompt_label.pack(side="left")
        self.entry = tk.Entry(frame, font=FONT)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>", self._on_up)
        self.entry.bind("<Down>", self._on_down)
        self.entry.focus_set()

    def write(self, text):
        """Добавляет строку text в область вывода."""
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def _refresh_prompt(self):
        """Обновляет приглашение рядом со строкой ввода."""
        self.prompt_label.configure(text=self.shell.prompt())

    def _finish_if_exited(self):
        """Закрывает окно, если оболочка завершила работу."""
        if not self.shell.running:
            self.root.destroy()

    def _on_enter(self, _event):
        """Выполняет введённую команду."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        self.shell.interact(line, self.write)
        self._refresh_prompt()
        self._finish_if_exited()

    def _show_history(self):
        """Показывает в строке ввода запись истории."""
        self.entry.delete(0, tk.END)
        if self.history_pos < len(self.history):
            self.entry.insert(0, self.history[self.history_pos])

    def _on_up(self, _event):
        """Листает историю команд назад."""
        if self.history_pos > 0:
            self.history_pos -= 1
            self._show_history()

    def _on_down(self, _event):
        """Листает историю команд вперёд."""
        if self.history_pos < len(self.history):
            self.history_pos += 1
            self._show_history()

    def start(self, banner, lines):
        """Показывает баннер и выполняет стартовый скрипт lines."""
        self.write(banner)
        run_script(self.shell, lines, self.write)
        self._refresh_prompt()
        self.root.after_idle(self._finish_if_exited)

    def run(self):
        """Запускает цикл обработки событий окна."""
        try:
            self.root.mainloop()
        except tk.TclError:
            return
