# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Fixtures for pytest."""

import pytest

from PyQt5.QtGui import QPixmap, QImageWriter

from vimiv.commands import commands
from vimiv.config import keybindings, settings
from vimiv.utils import objreg, impaths


@pytest.fixture
def tmpimage(tmpdir, qtbot):
    """Create an image to work with."""
    path = str(tmpdir.join("foo.png"))
    width = 10
    height = 10
    pm = QPixmap(width, height)
    qtbot.addWidget(pm)
    writer = QImageWriter(path)
    assert writer.write(pm.toImage())
    return path


@pytest.fixture
def cleansetup(mocker):
    """Clean setup for the gui classes.

    Patches applying styles and cleans up the registries when done.
    """
    mocker.patch("vimiv.config.styles.apply")
    yield
    # Disconnect any connected signals
    try:
        commands.signals.disconnect()
        impaths.signals.disconnect()
    # Fails if no signals were connected
    except TypeError:
        pass
    objreg.clear()
    commands.clear()
    keybindings.clear()
    settings.reset()
    assert not objreg._registry
