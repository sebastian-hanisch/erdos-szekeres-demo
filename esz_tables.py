"""Vorgerechnete Tabellen (esz_tables.json) und die Rechnungen, aus denen sie entstehen.

Die App liest nur die JSON-Datei: Aufzählungen aller n! Folgen (n = 8: 40 320, n = 9: 362 880) und die Zustandssuche über alle Folgen sind in der
Live-App zu teuer (Cloud langsamer als der Entwicklungsrechner). `tools/esz_make_tables.py` rechnet alles neu (`--check` vergleicht exakt mit der Datei).

Inhalt:
  aufzaehlung[n]  (n = 1..9): Zahl der Folgen je Form, je Paar (LIS, LDS), Kapazität c_W für W = 1..4 (Verteilung), Verletzungen und Gleichheitsfälle
                  der Kapazitätsgarantie c_W >= min(n, W·n/LIS) für W = 1..4.
  hoehe[n][W][H]  (n = 4..7, W = 2, 3, H = 2..4): Zahl der Folgen, in denen die Kapazität bei Stapelhöhe H gleich min(W·H, c_W) ist („erreicht“),
                  darunter, darüber; größte Lücke.
  woerter[n]      (n = 1..7): alle n^n Wörter über 1..n; Zahl der Wörter, in denen die vier Paarungen LIS·LDS >= n verletzen.
"""

import json
from functools import lru_cache
from itertools import permutations, product
from pathlib import Path

import esz_algorithm as A

PFAD = Path(__file__).with_name("esz_tables.json")
N_AUFZ_MAX = 9
W_AUFZ = (1, 2, 3, 4)
HOEHE_N = (4, 5, 6, 7)
HOEHE_W = (2, 3)
HOEHE_H = (2, 3, 4)
N_WORT_MAX = 7
PAARUNGEN = ("streng_streng", "streng_schwach", "schwach_streng", "schwach_schwach")


def _key(t) -> str:
    return ",".join(str(x) for x in t)


def berechne_aufzaehlung(n: int) -> dict:
    """Alle n! Folgen: Formen (Schensted), Paare (LIS, LDS) (Patience), Kapazität über die Spalten der Form, Kapazitätsgarantie."""
    formen: dict = {}
    paare: dict = {}
    kap = {W: {} for W in W_AUFZ}
    verletzungen = {W: 0 for W in W_AUFZ}
    gleich = {W: 0 for W in W_AUFZ}
    for p in permutations(range(1, n + 1)):
        lam = A.form(p)
        formen[lam] = formen.get(lam, 0) + 1
        li, ld = A.lis(p), A.lds(p)
        paare[(li, ld)] = paare.get((li, ld), 0) + 1
        spalten = A.konjugiert(lam)
        c = 0
        for W in W_AUFZ:
            c += spalten[W - 1] if W - 1 < len(spalten) else 0
            kap[W][c] = kap[W].get(c, 0) + 1
            grenze = min(n * li, W * n)            # Garantie min(n, W·n/LIS), mit LIS multipliziert
            if c * li < grenze:
                verletzungen[W] += 1
            elif c * li == grenze and li >= W:
                gleich[W] += 1
    return {
        "folgen": sum(formen.values()),
        "formen": {_key(k): v for k, v in sorted(formen.items(), reverse=True)},
        "paare": {_key(k): v for k, v in sorted(paare.items())},
        "kapazitaet": {str(W): {str(c): v for c, v in sorted(d.items())} for W, d in kap.items()},
        "garantie_verletzungen": {str(W): v for W, v in verletzungen.items()},
        "garantie_gleich": {str(W): v for W, v in gleich.items()},
    }


def berechne_hoehe(n: int, W: int, H: int) -> dict:
    """Alle n! Folgen: Kapazität bei Stapelhöhe H gegen min(W·H, c_W) (c_W aus der Form)."""
    erreicht = darunter = darueber = 0
    luecke = 0
    for p in permutations(range(1, n + 1)):
        ziel = min(W * H, A.kapazitaet_form(A.form(p), W))
        c = A.kapazitaet_hoehe(p, W, H)
        if c == ziel:
            erreicht += 1
        elif c < ziel:
            darunter += 1
            luecke = max(luecke, ziel - c)
        else:
            darueber += 1
    return {"folgen": erreicht + darunter + darueber, "erreicht": erreicht, "darunter": darunter, "darueber": darueber, "groesste_luecke": luecke}


def berechne_woerter(n: int) -> dict:
    """Alle n^n Wörter über 1..n: Verletzungen von LIS·LDS >= n je Paarung."""
    verletzungen = {k: 0 for k in PAARUNGEN}
    anzahl = 0
    for w in product(range(1, n + 1), repeat=n):
        anzahl += 1
        pr = A.paarungen(w)
        for k in PAARUNGEN:
            if pr[k] < n:
                verletzungen[k] += 1
    return {"woerter": anzahl, "verletzungen": verletzungen}


def berechne_alles(n_aufz=N_AUFZ_MAX, n_wort=N_WORT_MAX, hoehe_n=HOEHE_N) -> dict:
    return {
        "aufzaehlung": {str(n): berechne_aufzaehlung(n) for n in range(1, n_aufz + 1)},
        "hoehe": {str(n): {str(W): {str(H): berechne_hoehe(n, W, H) for H in HOEHE_H} for W in HOEHE_W} for n in hoehe_n},
        "woerter": {str(n): berechne_woerter(n) for n in range(1, n_wort + 1)},
    }


def schreibe(tabellen: dict) -> None:
    PFAD.write_text(json.dumps(tabellen, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8", newline="\n")


@lru_cache(maxsize=1)
def lade() -> dict:
    return json.loads(PFAD.read_text(encoding="utf-8"))


# --- Zugriff für die App --------------------------------------------------------------------------------------------------------------------

def aufzaehlung(n: int) -> dict | None:
    """Aufzählung aller n! Folgen (n <= 9) mit Schlüsseln als Tupel bzw. Zahlen; None bei n > 9."""
    roh = lade()["aufzaehlung"].get(str(n))
    if roh is None:
        return None
    return {
        "folgen": roh["folgen"],
        "formen": {tuple(int(x) for x in k.split(",")): v for k, v in roh["formen"].items()},
        "paare": {tuple(int(x) for x in k.split(",")): v for k, v in roh["paare"].items()},
        "kapazitaet": {int(W): {int(c): v for c, v in d.items()} for W, d in roh["kapazitaet"].items()},
        "garantie_verletzungen": {int(W): v for W, v in roh["garantie_verletzungen"].items()},
        "garantie_gleich": {int(W): v for W, v in roh["garantie_gleich"].items()},
    }


def hoehe(n: int, W: int, H: int) -> dict | None:
    return lade()["hoehe"].get(str(n), {}).get(str(W), {}).get(str(H))


def woerter(n: int) -> dict | None:
    return lade()["woerter"].get(str(n))
