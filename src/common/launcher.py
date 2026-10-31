"""Avvio di script di gioco in un nuovo processo."""

import subprocess
import sys
from pathlib import Path
from typing import Protocol

SRC_DIR = Path(__file__).resolve().parent.parent
MENU_SCRIPT = "main_menu.py"


class GameLauncher(Protocol):
    """Interfaccia per avviare uno script di gioco."""

    def launch(self, script_name: str) -> None:
        """Avvia lo script indicato."""


class SubprocessLauncher:
    """Avvia gli script come sotto-processi Python."""

    def __init__(self, base_dir: Path = SRC_DIR) -> None:
        self.base_dir = base_dir

    def launch(self, script_name: str) -> None:
        """Avvia ``script_name`` (relativo a ``base_dir``) senza attenderne la fine."""
        full_path = self.base_dir / script_name
        # Il processo figlio vive oltre questo: non va atteso con un context manager.
        subprocess.Popen(  # pylint: disable=consider-using-with
            [sys.executable, str(full_path)]
        )
