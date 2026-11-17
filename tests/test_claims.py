"""Claims: jede Zahl der README (Abschnitt „Befunde“) wird hier nachgerechnet (Zahl → Test, exakt oder als Band).

Ganzzahlen und Brüche exakt; Zählungen aus dem Zufall (Verweilzeit-Modell) als Band; Rechenzeiten der README sind Hinweise und stehen nicht in den Tests.
Die Tabelle „Zahl → Test“ steht in der README; die Aussagen der App (Grenzen, Verdikte) prüfen test_verdicts.py und test_presets.py."""

import math
from itertools import permutations
from pathlib import Path

import _orakel as O
import pytest

import esz_algorithm as A
import esz_evaluation as ev
import esz_scenario as S
import esz_tables as T

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_claim_handfolge(hand):
    assert A.tableau(hand) == [[1, 2, 4], [3, 5], [6]] and A.form(hand) == (3, 2, 1)
    assert A.haken_f((3, 2, 1)) == 16 and A.haken_f((3, 2, 1)) ** 2 == 256
    assert sum(1 for p in permutations(range(1, 7)) if A.form(p) == (3, 2, 1)) == 256
    assert [A.kapazitaet_fluss(hand, w)[0] for w in (1, 2, 3)] == [3, 5, 6]
    # bei W = 2 bleibt genau der Container mit Rang 1 draußen: nur sein Weglassen lässt eine Menge mit LIS <= 2 übrig
    ohne = [r for r in range(1, 7) if O.lis_dp([x for x in hand if x != r]) <= 2]
    assert ohne == [1]
    _c, stapel = A.kapazitaet_fluss(hand, 2)
    assert {hand[i] for k in stapel for i in k} == {2, 3, 4, 5, 6}


@pytest.mark.slow
def test_claim_fluss_gleich_spaltensumme_n8():
    """Alle 40 320 Folgen n = 8, W = 1 bis 3: Fluss = Spaltensumme, jede Belegung gültig."""
    n = 0
    for p in permutations(range(1, 9)):
        lam = A.form(p)
        for w in (1, 2, 3):
            c, stapel = A.kapazitaet_fluss(p, w)
            assert c == A.kapazitaet_form(lam, w) and A.pruefe_belegung(p, stapel, w) and sum(len(k) for k in stapel) == c, (p, w)
        n += 1
    assert n == 40320


def test_claim_es_alle_folgen_bis_n9():
    for n in range(1, 10):
        t = T.aufzaehlung(n)
        assert t["folgen"] == math.factorial(n)
        assert sum(t["paare"].values()) == t["folgen"]
        assert all(li * ld >= n for (li, ld) in t["paare"]), n       # 0 Verletzungen


def test_claim_gleichheitsfaelle():
    erwartet = [1, 2, 2, 6, 2, 52, 2, 394, 1766]
    for n, e in enumerate(erwartet, start=1):
        t = T.aufzaehlung(n)
        gleich = sum(v for (li, ld), v in t["paare"].items() if li * ld == n)
        assert gleich == e == A.gleichheitsfaelle(n), n
    assert A.gleichheitsfaelle(6) == 1 + 25 + 25 + 1


def test_claim_scharfe_folgen():
    t6, t8, t9, t4 = T.aufzaehlung(6), T.aufzaehlung(8), T.aufzaehlung(9), T.aufzaehlung(4)

    def zahl(t, a, b):
        return sum(v for (li, ld), v in t["paare"].items() if li <= a and ld <= b)

    assert zahl(t4, 2, 2) == 4 and zahl(t6, 2, 3) == 25 and zahl(t8, 2, 4) == 196 and zahl(t9, 3, 3) == 1764 == 42 ** 2
    blk = S.blockfolge(3, 3)
    assert blk == (7, 8, 9, 4, 5, 6, 1, 2, 3) and (A.lis(blk), A.lds(blk)) == (3, 3)


def test_claim_anteil_scharf():
    erwartet = {4: "25,0 %", 6: "7,2 %", 8: "0,98 %", 9: "0,49 %", 10: "0,097 %", 20: "2,3 · 10⁻⁶", 40: "1,3 · 10⁻¹³"}
    for n, text in erwartet.items():
        assert ev.anteil_text(A.knappheit(n)["anteil_scharf"]) == text, n


def test_claim_knappheit():
    quot = {4: 1.375, 6: 1.577, 8: 1.723, 10: 1.834, 20: 2.162, 40: 2.459}
    for n, q in quot.items():
        assert float(A.knappheit(n)["e_produkt"] / n) == pytest.approx(q, abs=0.0006), n
    # Faktor 1,4 bis 2,5 im ganzen Bereich n = 4 bis 40
    alle = [float(A.knappheit(n)["e_produkt"] / n) for n in range(4, 41)]
    assert round(min(alle), 1) == 1.4 and round(max(alle), 1) == 2.5
    assert float(A.knappheit(40)["e_max"]) == pytest.approx(10.78, abs=0.005) and A.knappheit(40)["garantie_max"] == 7
    assert float(A.knappheit(10)["e_max"]) == pytest.approx(4.94, abs=0.005) and A.knappheit(10)["garantie_max"] == 4
    assert float(A.knappheit(10)["e_produkt"]) == pytest.approx(18.34, abs=0.005)


def test_claim_kapazitaetsgarantie():
    for n in range(2, 10):
        t = T.aufzaehlung(n)
        assert all(t["garantie_verletzungen"][w] == 0 for w in (1, 2, 3, 4)), n
    gl = {n: T.aufzaehlung(n)["garantie_gleich"] for n in (6, 8, 9)}
    assert [gl[n][1] for n in (6, 8, 9)] == [52, 394, 1766]
    assert [gl[n][2] for n in (6, 8, 9)] == [157, 1626, 6626]
    assert round(100 * gl[8][2] / 40320, 1) == 4.0
    aufger = {n: A.garantie_statistik(n, 1)["gleich_aufgerundet"] for n in (6, 8, 9)}
    assert aufger == {6: 158, 8: 3391, 9: 43671}
    assert [round(100 * aufger[n] / math.factorial(n), 1) for n in (6, 8, 9)] == [21.9, 8.4, 12.0]


def test_claim_ganz_passend_n8():
    alle = list(permutations(range(1, 9)))
    erwartet = {2: 1430, 3: 15767, 4: 33324}
    for w, z in erwartet.items():
        assert A.anteil_ganz_passend(8, w)[0] == z
        assert sum(1 for p in alle if O.lis_dp(p) <= w) == z
    assert [round(100 * z / 40320, 2) for z in erwartet.values()] == [3.55, 39.1, 82.65]


def test_claim_erwartete_kapazitaet():
    n10 = [round(float(A.erwartete_kapazitaet(10, w)) / 10, 3) for w in (1, 2, 3, 4)]
    n20 = [round(float(A.erwartete_kapazitaet(20, w)) / 20, 3) for w in (1, 2, 3, 4)]
    assert n10 == [0.433, 0.698, 0.859, 0.950] and n20 == [0.331, 0.560, 0.722, 0.836]
    assert round(float(A.erwartete_kapazitaet(40, 1)) / 40, 3) == 0.249


def test_claim_falle():
    erwartet = [70.0, 64.4, 74.6, 75.5, 72.4, 73.3]
    for n, e in zip(range(5, 11), erwartet):
        st = A.falle_statistik(n, 1)
        assert round(100 * float(st["anteil_anders"]), 1) == e, n
        assert st["mittlere_ueberschaetzung"] == 0
    assert A.falle_statistik(9, 1)["groesste_abweichung"] == 8
    alle = list(permutations(range(1, 7)))
    assert sum(1 for p in alle if O.lis_dp(p) != O.lds_dp(p)) == 464 and A.falle_statistik(6, 1)["folgen_anders"] == 464
    assert sum(1 for p in alle if O.lis_dp(p) == O.lds_dp(p)) == 256
    b = (4, 5, 6, 1, 2, 3)
    assert [O.kap_teilmengen(b, w) for w in (1, 2, 3)] == [2, 4, 6]
    assert [A.kapazitaet_form(A.form(b), w, fallend=False) for w in (1, 2, 3)] == [3, 6, 6]
    assert [A.kapazitaet_fluss(tuple(range(1, 7)), w)[0] for w in (1, 2, 3)] == [1, 2, 3]
    assert [A.kapazitaet_fluss(tuple(range(6, 0, -1)), w)[0] for w in (1, 2, 3)] == [6, 6, 6]
    # n = 6, W = 1: Aufzählung gegen die Zählung aus den Formen
    assert sum(1 for p in alle if A.kapazitaet_form(A.form(p), 1, fallend=False) != A.kapazitaet_form(A.form(p), 1)) == 464


def test_claim_gleichstaende():
    erwartet = {2: 2, 3: 15, 4: 64, 5: 1105, 6: 5376, 7: 208257}
    summe = {2: 4, 3: 27, 4: 256, 5: 3125, 6: 46656, 7: 823543}
    for n, v in erwartet.items():
        w = T.woerter(n)
        assert w["woerter"] == summe[n] and w["verletzungen"]["streng_streng"] == v, n
        assert w["verletzungen"]["streng_schwach"] == 0 and w["verletzungen"]["schwach_streng"] == 0, n
    assert round(100 * 208257 / 823543, 1) == 25.3
    p = A.paarungen((2, 2, 2, 2))
    assert (p["streng_schwach"], p["streng_streng"]) == (4, 1)


def test_claim_hoehe():
    erwartet = {(6, 3, 2): (612, 108), (7, 2, 3): (4691, 349), (7, 3, 3): (4953, 87), (7, 3, 4): (5037, 3)}
    for (n, w, h), (erreicht, darunter) in erwartet.items():
        t = T.hoehe(n, w, h)
        assert (t["erreicht"], t["darunter"]) == (erreicht, darunter) and t["folgen"] == math.factorial(n)
    for n in T.HOEHE_N:
        for w in T.HOEHE_W:
            for h in T.HOEHE_H:
                t = T.hoehe(n, w, h)
                assert t["darueber"] == 0 and t["groesste_luecke"] <= 1
                assert (t["groesste_luecke"] == 1) == (t["darunter"] > 0)


@pytest.fixture(scope="module")
def modell_v():
    return {n: {seed: ev.simuliere_v(n, 1000, seed) for seed in (16000, 16001)} for n in (10, 20)}


def test_claim_modell_v(modell_v):
    s = modell_v[10][16000]
    erwartet = {"0.5": (0.149, 0.261, 0.362, 0.462), "2": (0.247, 0.437, 0.583, 0.691), "16": (0.389, 0.639, 0.804, 0.912), "inf": (0.432, 0.698, 0.860, 0.954)}
    for d, zahlen in erwartet.items():
        for w, z in enumerate(zahlen, start=1):
            assert s["d"][d]["w"][w]["mittel"] == pytest.approx(z, abs=0.002), (d, w)
            # der zweite Zufalls-Seed liegt im Band (Standardfehler der Differenz etwa 0,003)
            assert abs(modell_v[10][16001]["d"][d]["w"][w]["mittel"] - s["d"][d]["w"][w]["mittel"]) < 0.01, (d, w)
    exakt = ev.exakt_uniform(10)
    assert [round(exakt[w]["mittel"], 3) for w in (1, 2, 3, 4)] == [0.433, 0.698, 0.859, 0.950]
    assert all(abs(s["d"]["inf"]["w"][w]["mittel"] - exakt[w]["mittel"]) < 0.02 for w in (1, 2, 3, 4))
    # D = 0,5: in keiner der 1000 Folgen passen alle in 3 Stapel (beide Zufalls-Seeds)
    assert s["d"]["0.5"]["w"][3]["ganz_n"] == 0 and modell_v[10][16001]["d"]["0.5"]["w"][3]["ganz_n"] == 0
    s20 = modell_v[20][16000]
    for w, z in enumerate((0.088, 0.158, 0.215, 0.266), start=1):
        assert s20["d"]["0.5"]["w"][w]["mittel"] == pytest.approx(z, abs=0.002), w
    for w, z in enumerate((0.329, 0.559, 0.722, 0.835), start=1):
        assert s20["d"]["inf"]["w"][w]["mittel"] == pytest.approx(z, abs=0.002), w
    # je kleiner D, desto weniger passt (monoton über die sieben D, W = 1 bis 4, beide Größen)
    for n in (10, 20):
        folge_d = ["0.5", "1", "2", "4", "8", "16", "inf"]
        for w in (1, 2, 3, 4):
            m = [modell_v[n][16000]["d"][d]["w"][w]["mittel"] for d in folge_d]
            assert all(m[i] < m[i + 1] for i in range(6)), (n, w, m)


def test_keine_planungswoerter_in_readme_und_app_texten():
    """Planungswörter stehen weder in der README noch in den Texten der App (die Fußzeile „Mehr zu den Demos“ stammt vom Werkzeug und ist hier kein Planungstext)."""
    import esz_texts as X

    verboten = ("Stück", "Linie", "Vormessung", "Phase 0", "V1", "sm_v", "trägt", "tragen", "Saatwert", "läuft lokal", "geplant")
    text = "\n".join(zeile for zeile in README.splitlines() if "Diese Demo ist Teil des Portfolios" not in zeile) + X.EINLEITUNG + X.GRENZEN + X.FORMELN + X.SO_FUNKTIONIERT
    for wort in verboten:
        assert wort not in text, wort


def test_readme_und_app_nennen_dieselben_zahlen_der_grenzen():
    """Die Zahlen der Tabelle „Wo die Annahmen enden“ (App) stehen auch in der README (Test auf den App-Text in der README)."""
    import esz_texts as X

    for zahl in ("612 von 720", "208 257 von 823 543".replace(" ", " ")):
        assert zahl in README.replace(" ", " "), zahl
        assert zahl in X.GRENZEN.replace(" ", " "), zahl
