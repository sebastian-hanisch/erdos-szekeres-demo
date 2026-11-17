"""Orakel-Tests: die Rechenwege der App gegen unabhängige Rechenwege (ORACLE-PLAYBOOK §2, DEMO-PLAYBOOK §12).

App-Kern: Min-Cost-Fluss (`kapazitaet_fluss`), Spaltensumme der Schensted-Form, Hakenformel, Zustandssuche bei begrenzter Höhe, Erwartungswerte aus den Formen.
Orakel (tests/_orakel.py, nichts davon benutzt esz_algorithm):
  (a) Aufzählung aller Teilmengen (größte mit längster wachsender Teilfolge <= W: Mirsky),
  (b) Aufzählung aller Zuordnungen „Stapel 1..W oder draußen“,
  (c) Form nach der Definition von Greene-Kleitman (Vereinigung von k wachsenden Teilfolgen), dazu Hakenformel gegen Eckenrekursion und gegen die Zählung der
      Folgen je Form,
  (d) Erdős-Szekeres, Schärfe und Erwartungswerte (Brüche) gegen die Aufzählung aller Folgen,
  (e) Höhe gegen die Aufzählung aller Zuordnungen mit Höhengrenze, Paarungen der Wörter gegen Doppelschleifen.
Das Orakel ist an den Handbeispielen von tests/test_algorithm.py geprüft (Handfolge 3 / 5 / 6, Blockfolge 2 / 4 / 6). Schnelle Läufe < 10 s; größere
Läufe tragen die Marke `slow`."""

import random
from fractions import Fraction
from itertools import permutations, product

import _orakel as O
import pytest

import esz_algorithm as A
import esz_scenario as S


def _alle(n):
    return list(permutations(range(1, n + 1)))


# --- das Orakel selbst, an Handwerten -------------------------------------------------------------------------------------------------------

def test_orakel_an_den_handbeispielen(hand, block6):
    assert [O.kap_teilmengen(hand, w) for w in (1, 2, 3)] == [3, 5, 6]
    assert [O.kap_zuordnung(hand, w) for w in (1, 2, 3)] == [3, 5, 6]
    assert [O.kap_teilmengen(block6, w) for w in (1, 2, 3)] == [2, 4, 6]
    assert [O.kap_zuordnung(block6, w) for w in (1, 2, 3)] == [2, 4, 6]
    assert O.greene_zeilen(hand) == (3, 2, 1) and O.greene_zeilen(block6) == (3, 3)
    assert O.f_ecken((3, 2, 1)) == 16 and O.f_ecken((3, 3, 3)) == 42


# --- Kapazität: Fluss gegen Teilmengen und Zuordnungen --------------------------------------------------------------------------------------

@pytest.mark.parametrize("fallend", [True, False])
def test_fluss_gegen_teilmengensuche_alle_folgen_bis_n6(fallend):
    for n in range(1, 7):
        for p in _alle(n):
            for w in range(1, n + 1):
                c, stapel = A.kapazitaet_fluss(p, w, fallend)
                assert c == O.kap_teilmengen(p, w, fallend), (p, w)
                assert A.pruefe_belegung(p, stapel, w, fallend) and sum(len(k) for k in stapel) == c


def test_fluss_gegen_zuordnungssuche_n5_w3_und_n6_w2():
    for p in _alle(5):
        for w in (1, 2, 3):
            assert A.kapazitaet_fluss(p, w)[0] == O.kap_zuordnung(p, w), (p, w)
    for p in _alle(6):
        for w in (1, 2):
            assert A.kapazitaet_fluss(p, w)[0] == O.kap_zuordnung(p, w), (p, w)


def test_spaltensumme_gegen_teilmengensuche_alle_folgen_bis_n6():
    for n in range(1, 7):
        for p in _alle(n):
            lam = A.form(p)
            for w in range(1, n + 1):
                assert A.kapazitaet_form(lam, w) == O.kap_teilmengen(p, w), (p, w)
                assert A.kapazitaet_form(lam, w, fallend=False) == O.kap_teilmengen(p, w, fallend=False), (p, w)


def test_fluss_gegen_spaltensumme_zufallsfolgen_n7_bis_n20():
    rng = random.Random(7)
    for _ in range(120):
        n = rng.randint(7, 20)
        p = list(range(1, n + 1))
        rng.shuffle(p)
        lam = A.form(p)
        for w in (1, 2, 3, 5, 8):
            c, stapel = A.kapazitaet_fluss(p, w)
            assert c == A.kapazitaet_form(lam, w), (p, w)
            assert A.pruefe_belegung(p, stapel, w)
            c2, st2 = A.kapazitaet_fluss(p, w, fallend=False)
            assert c2 == A.kapazitaet_form(lam, w, fallend=False)
            assert A.pruefe_belegung(p, st2, w, fallend=False)


@pytest.mark.slow
def test_fluss_und_teilmengen_gegen_spaltensumme_alle_folgen_n7():
    for p in _alle(7):
        lam = A.form(p)
        for w in (1, 2, 3):
            assert A.kapazitaet_form(lam, w) == O.kap_teilmengen(p, w)
            assert A.kapazitaet_fluss(p, w)[0] == A.kapazitaet_form(lam, w)


# --- Form, Hakenformel ----------------------------------------------------------------------------------------------------------------------

def test_form_gegen_greene_definition_alle_folgen_bis_n6():
    for n in range(1, 7):
        for p in _alle(n):
            assert A.form(p) == O.greene_zeilen(p), p


def test_haken_gegen_eckenrekursion_alle_partitionen_bis_n14():
    for n in range(1, 15):
        for lam in A.partitionen(n):
            assert A.haken_f(lam) == O.f_ecken(lam), lam


def test_zahl_der_folgen_je_form_ist_f_quadrat_n_bis_7():
    for n in range(1, 8):
        zaehlung = {}
        for p in _alle(n):
            lam = A.form(p)
            zaehlung[lam] = zaehlung.get(lam, 0) + 1
        assert zaehlung == {lam: f2 for lam, f2, _a, _b in A.formenliste(n)}, n


def test_erste_zeile_ist_lis_zeilenzahl_ist_lds_alle_folgen_bis_n7():
    for n in range(1, 8):
        for p in _alle(n):
            lam = A.form(p)
            assert lam[0] == O.lis_dp(p) == A.lis(p) and len(lam) == O.lds_dp(p) == A.lds(p)


# --- Erdős-Szekeres, Schärfe, Garantie ------------------------------------------------------------------------------------------------------

def test_es_produkt_gleichheit_und_schaerfe_alle_folgen_bis_n7():
    for n in range(1, 8):
        gleich = 0
        for p in _alle(n):
            li, ld = O.lis_dp(p), O.lds_dp(p)
            assert li * ld >= n, p
            gleich += li * ld == n
        assert gleich == A.gleichheitsfaelle(n), n
    for n in range(1, 8):
        for a in range(1, n + 1):
            if n % a == 0:
                b = n // a
                z = sum(1 for p in _alle(n) if O.lis_dp(p) <= a and O.lds_dp(p) <= b)
                assert z == A.scharf_anzahl(a, b), (a, b)


@pytest.mark.slow
def test_es_und_schaerfe_alle_folgen_n8():
    alle = _alle(8)
    assert sum(1 for p in alle if O.lis_dp(p) * O.lds_dp(p) == 8) == A.gleichheitsfaelle(8) == 394
    assert all(O.lis_dp(p) * O.lds_dp(p) >= 8 for p in alle)
    assert sum(1 for p in alle if O.lis_dp(p) <= 2 and O.lds_dp(p) <= 4) == A.scharf_anzahl(2, 4) == 196


def test_es_aussage_ab_plus_1_alle_folgen_ab_plus_1_bis_7():
    """Länge ab + 1 hat LIS >= a + 1 oder LDS >= b + 1 (alle Folgen)."""
    for a, b in ((1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2), (1, 4), (4, 1), (2, 3), (3, 2), (1, 5), (5, 1), (1, 6), (6, 1)):
        for p in _alle(a * b + 1):
            assert O.lis_dp(p) >= a + 1 or O.lds_dp(p) >= b + 1, (a, b, p)


def test_paare_gegen_doppelschleife_und_verschieden():
    for n in range(1, 8):
        for p in _alle(n):
            paare = A.es_paare(p)
            assert paare == O.paare_dp(p) and len(set(paare)) == n


def test_blockfolge_hat_lis_a_und_lds_b_und_fuellt_das_gitter():
    for a in range(1, 7):
        for b in range(1, 7):
            f = S.blockfolge(a, b)
            assert sorted(f) == list(range(1, a * b + 1))
            assert (O.lis_dp(f), O.lds_dp(f)) == (a, b)
            assert set(O.paare_dp(f)) == {(i, j) for i in range(1, a + 1) for j in range(1, b + 1)}


def test_erwartungswerte_exakt_gegen_aufzaehlung_bis_n7():
    for n in range(1, 8):
        fak = O.fakultaet(n)
        alle = _alle(n)
        s_prod = sum(O.lis_dp(p) * O.lds_dp(p) for p in alle)
        s_max = sum(max(O.lis_dp(p), O.lds_dp(p)) for p in alle)
        k = A.knappheit(n)
        assert k["e_produkt"] == Fraction(s_prod, fak) and k["e_max"] == Fraction(s_max, fak)
    for n in range(1, 7):
        alle = _alle(n)
        for w in (1, 2, 3):
            s = sum(O.kap_teilmengen(p, w) for p in alle)
            assert A.erwartete_kapazitaet(n, w) == Fraction(s, O.fakultaet(n)), (n, w)


def test_anteil_ganz_passend_gegen_aufzaehlung_n7():
    alle = _alle(7)
    for w in (1, 2, 3, 4):
        z = sum(1 for p in alle if O.lis_dp(p) <= w)
        assert A.anteil_ganz_passend(7, w)[0] == z


def test_kapazitaetsgarantie_in_allen_folgen_bis_n7_w3():
    for n in range(2, 8):
        for p in _alle(n):
            li = O.lis_dp(p)
            lam = A.form(p)
            for w in (1, 2, 3):
                c = A.kapazitaet_form(lam, w)
                assert c * li >= min(n * li, w * n), (p, w)      # c >= min(n, w·n/LIS), mit LIS multipliziert


def test_garantie_statistik_gegen_aufzaehlung_n7():
    """Verletzungen und Gleichheitsfälle der Garantie aus den Formen gegen die Zählung über alle Folgen (ohne die Formenliste)."""
    alle = _alle(7)
    for w in (1, 2, 3):
        gleich = 0
        for p in alle:
            li = O.lis_dp(p)
            c = A.kapazitaet_form(A.form(p), w)
            if li >= w and c * li == w * 7:
                gleich += 1
        st = A.garantie_statistik(7, w)
        assert st["gleich"] == gleich and st["verletzungen"] == 0
        assert sum(st["verteilung"].values()) == 5040


# --- Höhe -----------------------------------------------------------------------------------------------------------------------------------

def test_hoehe_gegen_zuordnungssuche_alle_folgen_n5():
    for p in _alle(5):
        for w in (2, 3):
            for h in (1, 2, 3):
                assert A.kapazitaet_hoehe(p, w, h) == O.kap_hoehe_zuordnung(p, w, h), (p, w, h)


def test_hoehe_gegen_zuordnungssuche_zufallsfolgen_n6():
    rng = random.Random(11)
    for _ in range(25):
        p = list(range(1, 7))
        rng.shuffle(p)
        for w, h in ((2, 2), (2, 3), (3, 2)):
            assert A.kapazitaet_hoehe(p, w, h) == O.kap_hoehe_zuordnung(p, w, h), (p, w, h)


def test_hoehe_hat_hoechstens_min_w_h_und_c_w_alle_folgen_n6():
    for p in _alle(6):
        for w, h in ((2, 2), (3, 2), (2, 3)):
            assert A.kapazitaet_hoehe(p, w, h) <= min(w * h, A.kapazitaet_form(A.form(p), w))


# --- Gleichstände ---------------------------------------------------------------------------------------------------------------------------

def test_paarungen_gegen_doppelschleife_alle_woerter_bis_n5():
    for n in range(1, 6):
        for w in product(range(1, n + 1), repeat=n):
            pr = A.paarungen(w)
            assert pr["streng_streng"] == O.lis_dp(w) * O.lds_dp(w)
            assert pr["streng_schwach"] == O.lis_dp(w) * O.lds_dp(w, streng=False)
            assert pr["schwach_streng"] == O.lis_dp(w, streng=False) * O.lds_dp(w)
            assert pr["schwach_schwach"] == O.lis_dp(w, streng=False) * O.lds_dp(w, streng=False)
            assert pr["streng_schwach"] >= n and pr["schwach_streng"] >= n        # diese Paarungen halten in jedem Wort


def test_streng_mal_streng_verletzt_bei_gleichstaenden_n4_64_von_256():
    n = 4
    verletzt = sum(1 for w in product(range(1, n + 1), repeat=n) if O.lis_dp(w) * O.lds_dp(w) < n)
    assert verletzt == 64


# --- Verweilzeit-Modell ---------------------------------------------------------------------------------------------------------------------

def test_folge_v_ist_die_reihenfolge_der_abfahrten():
    """Container 0 bleibt lange (E = 5, D = 2: Abfahrt 10), Container 1 kurz (E = 0,1: 1,2), Container 2 mittel (E = 1: 4)."""
    assert S.folge_v((5.0, 0.1, 1.0), 2.0) == (3, 1, 2)
    assert S.folge_v((5.0, 0.1, 1.0), S.D_UNENDLICH) == (3, 1, 2)         # nur E ordnet: 0,1 < 1 < 5
    assert S.folge_v((0.0, 0.0, 0.0), 1.0) == (1, 2, 3)                      # Gleichstand der Abfahrt: nach dem Index


def test_modell_v_kleines_d_gibt_fast_sortierte_folgen():
    ziehungen = S.ziehungen_v(12, 40, 5)
    mittel_lis = {D: sum(O.lis_dp(S.folge_v(e, D)) for e in ziehungen) / 40 for D in (0.5, 4.0, S.D_UNENDLICH)}
    assert mittel_lis[0.5] > mittel_lis[4.0] > mittel_lis[S.D_UNENDLICH]


def test_modell_v_kapazitaet_form_gegen_fluss_auf_ziehungen():
    ziehungen = S.ziehungen_v(15, 30, 3)
    for D in (1.0, 8.0, S.D_UNENDLICH):
        for e in ziehungen:
            p = S.folge_v(e, D)
            lam = A.form(p)
            for w in (1, 3, 6):
                assert A.kapazitaet_fluss(p, w)[0] == A.kapazitaet_form(lam, w)


def test_modell_v_uniform_gegen_exakte_werte_im_band():
    """Die Spalte D = ∞ der Simulation liegt für n = 10 und 1500 Folgen innerhalb von 0,02 der exakten Werte aus den Formen (Standardfehler etwa 0,005)."""
    import esz_evaluation as ev

    sim = ev.simuliere_v(10, 1500, 16000)
    exakt = ev.exakt_uniform(10)
    for w in range(1, 7):
        assert abs(sim["d"]["inf"]["w"][w]["mittel"] - exakt[w]["mittel"]) < 0.02, w
