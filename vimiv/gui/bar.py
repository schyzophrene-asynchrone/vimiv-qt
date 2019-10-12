# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Bar widget at the bottom including statusbar and commandline."""

from PyQt5.QtWidgets import QWidget, QStackedLayout, QSizePolicy

from vimiv import api, utils


class Bar(QWidget):
    """Bar at the bottom including statusbar and commandline.

    Attributes:
        _commandline: Commandline widget in the bar.
        _stack: QStackedLayout containing statusbar and commandline.
        _statusbar: Statusbar widget in the bar.
    """

    @api.objreg.register
    def __init__(self, statusbar, commandline):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        self._commandline = commandline
        self._statusbar = statusbar
        self._stack = QStackedLayout(self)

        self._stack.addWidget(statusbar)
        self._stack.addWidget(self._commandline)
        self._stack.setCurrentWidget(statusbar)

        self._commandline.editingFinished.connect(self._on_editing_finished)
        api.settings.statusbar.show.changed.connect(self._on_show_changed)

        if not api.settings.statusbar.show.value:
            self.hide()

    @api.keybindings.register("<colon>", "command", mode=api.modes.MANIPULATE)
    @api.keybindings.register("<colon>", "command")
    @api.commands.register(hide=True, store=False, mode=api.modes.MANIPULATE)
    @api.commands.register(hide=True, store=False)
    def command(self, text: str = ""):
        """Enter command mode.

        **syntax:** ``:command [--text=TEXT]``

        optional arguments:
            * ``--text``: String to append to the ``:`` prefix.
        """
        self._enter_command_mode(":" + text)

    @api.keybindings.register("?", "search --reverse")
    @api.keybindings.register("/", "search")
    @api.commands.register(hide=True, store=False)
    def search(self, reverse: bool = False):
        """Start a search.

        **syntax:** ``:search [--reverse]``

        optional arguments:
            * ``--reverse``: Search in reverse direction.
        """
        if reverse:
            self._enter_command_mode("?")
        else:
            self._enter_command_mode("/")

    def _enter_command_mode(self, text):
        """Enter command mode setting the text to text."""
        self.show()
        self._stack.setCurrentWidget(self._commandline)
        self._commandline.setText(text)
        api.modes.COMMAND.enter()

    @api.keybindings.register("<escape>", "leave-commandline", mode=api.modes.COMMAND)
    @api.commands.register(mode=api.modes.COMMAND)
    def leave_commandline(self):
        """Leave command mode."""
        self._commandline.editingFinished.emit()

    @utils.slot
    def _on_editing_finished(self):
        """Leave command mode on the editingFinished signal."""
        self._commandline.setText("")
        self._stack.setCurrentWidget(self._statusbar)
        self._maybe_hide()
        api.modes.COMMAND.leave()

    def _on_show_changed(self, value: bool):
        self._statusbar.setVisible(value)
        self._maybe_hide()

    def _maybe_hide(self):
        """Hide bar if statusbar is not visible and not in command mode."""
        always_show = api.settings.statusbar.show.value
        if not always_show and not self._commandline.hasFocus():
            self.hide()
        else:
            self.show()


def instance():
    return api.objreg.get(Bar)
