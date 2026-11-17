"""Rechnet die vorgerechneten Tabellen (esz_tables.json) neu.

    python tools/esz_make_tables.py            # schreibt esz_tables.json (rund 1 bis 2 Minuten)
    python tools/esz_make_tables.py --check    # rechnet neu und vergleicht exakt mit der Datei (Exit-Code 1 bei Abweichung)

Alle Werte sind Ganzzahlen aus Aufzählungen aller Folgen bzw. Wörter und deshalb auf jeder Plattform gleich."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import esz_tables as T  # noqa: E402


def main(argv) -> int:
    start = time.perf_counter()
    neu = T.berechne_alles()
    print(f"neu gerechnet in {time.perf_counter() - start:.0f} s")
    if "--check" in argv:
        alt = T.lade()
        if alt == neu:
            print("esz_tables.json stimmt mit der Neu-Rechnung überein")
            return 0
        for bereich in neu:
            if alt.get(bereich) != neu[bereich]:
                print(f"ABWEICHUNG im Bereich {bereich}")
        return 1
    T.schreibe(neu)
    print(f"geschrieben: {T.PFAD}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
