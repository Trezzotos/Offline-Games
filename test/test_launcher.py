"""Test del launcher di script di gioco."""

import sys
from pathlib import Path
from unittest.mock import patch

from common.launcher import SRC_DIR, SubprocessLauncher


def test_launch_uses_current_interpreter_and_absolute_path() -> None:
    """Lo script viene avviato con l'interprete corrente e path assoluto."""
    with patch("subprocess.Popen") as popen:
        SubprocessLauncher().launch("sudoku.py")
    popen.assert_called_once_with([sys.executable, str(SRC_DIR / "sudoku.py")])


def test_launch_respects_custom_base_dir(tmp_path: Path) -> None:
    """La directory base è configurabile."""
    with patch("subprocess.Popen") as popen:
        SubprocessLauncher(tmp_path).launch("x.py")
    assert popen.call_args[0][0][1] == str(tmp_path / "x.py")
