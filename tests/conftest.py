"""Gemeinsame Fixtures: die Handbeispiele, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand():
    """Handfolge n = 6: (1, 3, 6, 2, 5, 4). Tableau 1 2 4 / 3 5 / 6, Form (3, 2, 1), Kapazität 3 / 5 / 6 bei W = 1 / 2 / 3."""
    return (1, 3, 6, 2, 5, 4)


@pytest.fixture
def block6():
    """Falle: (4, 5, 6, 1, 2, 3). Tableau 1 2 3 / 4 5 6, Form (3, 3). Spaltensumme 2 / 4 / 6, Zeilensumme 3 / 6 / 6."""
    return (4, 5, 6, 1, 2, 3)
