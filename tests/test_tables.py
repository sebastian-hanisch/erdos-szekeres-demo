"""Die vorgerechneten Tabellen (esz_tables.json) gegen Neu-Rechnung und gegen die Formeln.

Ganzzahlen aus Aufzählungen: auf jeder Plattform gleich, deshalb wird exakt verglichen. Länge 8 und 9 (und die Wörter der Länge 7) tragen die Marke `slow`;
`python tools/esz_make_tables.py --check` rechnet alles neu und vergleicht (rund 20 Sekunden)."""

import math

import pytest

import esz_algorithm as A
import esz_tables as T


def _roh(n):
    return T.lade()["aufzaehlung"][str(n)]


@pytest.mark.parametrize("n", range(1, 8))
def test_aufzaehlung_n_bis_7_gleich_neu_gerechnet(n):
    assert T.berechne_aufzaehlung(n) == _roh(n)


@pytest.mark.slow
@pytest.mark.parametrize("n", [8, 9])
def test_aufzaehlung_n8_n9_gleich_neu_gerechnet(n):
    assert T.berechne_aufzaehlung(n) == _roh(n)


@pytest.mark.parametrize("n", range(1, 10))
def test_aufzaehlung_gegen_die_formeln(n):
    """Folgen je Form = f², Summe = n!, Paare (LIS, LDS) aus den Formen, Gleichheitsfälle = Summe (f^Rechteck)², Kapazität = Spaltensumme."""
    t = T.aufzaehlung(n)
    assert t["folgen"] == math.factorial(n)
    assert t["formen"] == {lam: f2 for lam, f2, _a, _b in A.formenliste(n)}
    aus_formen = {}
    for _lam, f2, li, ld in A.formenliste(n):
        aus_formen[(li, ld)] = aus_formen.get((li, ld), 0) + f2
    assert t["paare"] == aus_formen
    assert sum(v for (li, ld), v in t["paare"].items() if li * ld == n) == A.gleichheitsfaelle(n)
    assert sum(1 for (li, ld) in t["paare"] if li * ld < n) == 0
    for w in (1, 2, 3, 4):
        assert t["kapazitaet"][w] == A.garantie_statistik(n, w)["verteilung"]
        assert t["garantie_verletzungen"][w] == 0
        assert t["garantie_gleich"][w] == A.garantie_statistik(n, w)["gleich"]


@pytest.mark.parametrize("n", [4, 5, 6])
def test_hoehe_gleich_neu_gerechnet(n):
    for w in T.HOEHE_W:
        for h in T.HOEHE_H:
            assert T.berechne_hoehe(n, w, h) == T.hoehe(n, w, h), (n, w, h)


@pytest.mark.slow
def test_hoehe_n7_gleich_neu_gerechnet():
    for w in T.HOEHE_W:
        for h in T.HOEHE_H:
            assert T.berechne_hoehe(7, w, h) == T.hoehe(7, w, h), (7, w, h)


def test_hoehe_nie_ueber_min_w_h_c_w_und_luecke_hoechstens_1():
    for n in T.HOEHE_N:
        for w in T.HOEHE_W:
            for h in T.HOEHE_H:
                t = T.hoehe(n, w, h)
                assert t["darueber"] == 0 and t["groesste_luecke"] <= 1
                assert t["erreicht"] + t["darunter"] == t["folgen"] == math.factorial(n)


@pytest.mark.parametrize("n", range(1, 7))
def test_woerter_gleich_neu_gerechnet(n):
    assert T.berechne_woerter(n) == T.woerter(n)


@pytest.mark.slow
def test_woerter_n7_gleich_neu_gerechnet():
    assert T.berechne_woerter(7) == T.woerter(7)


def test_woerter_nur_streng_mal_streng_verletzt():
    for n in range(1, T.N_WORT_MAX + 1):
        w = T.woerter(n)
        assert w["woerter"] == n ** n
        assert w["verletzungen"]["streng_schwach"] == w["verletzungen"]["schwach_streng"] == w["verletzungen"]["schwach_schwach"] == 0
    assert T.woerter(4)["verletzungen"]["streng_streng"] == 64
    assert T.woerter(7)["verletzungen"]["streng_streng"] == 208257


def test_datei_ist_vollstaendig():
    t = T.lade()
    assert sorted(int(k) for k in t["aufzaehlung"]) == list(range(1, 10))
    assert sorted(int(k) for k in t["woerter"]) == list(range(1, 8))
    assert sorted(int(k) for k in t["hoehe"]) == [4, 5, 6, 7]
