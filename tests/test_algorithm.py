"""Einheiten des Kerns an Handbeispielen (Mini-Instanzen, von Hand nachgerechnet; DEMO-PLAYBOOK §1b).

Jeder Erwartungswert steht als Handrechnung im Kommentar, nicht als Abschrift der Ausgabe des Codes."""

from fractions import Fraction
from itertools import permutations

import pytest

import esz_algorithm as A
import esz_scenario as S

# --- Teilfolgen -----------------------------------------------------------------------------------------------------------------------------

def test_lis_lds_von_hand():
    """(2, 5, 1, 4, 3): wachsend 2 5 oder 2 4 oder 2 3 oder 1 4 oder 1 3: Länge 2; fallend 5 4 3: Länge 3."""
    assert A.lis((2, 5, 1, 4, 3)) == 2 and A.lds((2, 5, 1, 4, 3)) == 3


def test_schwache_teilfolgen_mit_gleichstand():
    """(2, 2, 2, 2): streng wachsend 1, schwach wachsend 4, streng fallend 1, schwach fallend 4."""
    w = (2, 2, 2, 2)
    assert (A.lis(w), A.lis_schwach(w), A.lds(w), A.lds_schwach(w)) == (1, 4, 1, 4)


def test_paarungen_gleichstand_h5():
    """(2, 2, 2, 2): streng×streng = 1·1 = 1 < 4 (verletzt), streng wachsend × schwach fallend = 1·4 = 4 = n."""
    p = A.paarungen((2, 2, 2, 2))
    assert p["streng_streng"] == 1 and p["streng_schwach"] == 4 and p["schwach_streng"] == 4 and p["schwach_schwach"] == 16


def test_standardisieren():
    assert A.standardisiere((10, 30, 20)) == (1, 3, 2)
    with pytest.raises(ValueError):
        A.standardisiere((1, 1, 2))


# --- Beweisgitter (H1) ----------------------------------------------------------------------------------------------------------------------

def test_es_paare_von_hand_h1():
    """(2, 5, 1, 4, 3): 2:(1,1); 5:(2,1) weil 2<5; 1:(1,2) weil 2>1 und 5>1 fallen nur auf Länge 2; 4:(2,2) (2,4 wächst; 5,4 fällt);
    3:(2,3) (5,4,3 fällt, 2,3 wächst). Fünf verschiedene Paare, das 2×2-Gitter hat nur vier Felder, (2,3) liegt außerhalb."""
    p = A.es_paare((2, 5, 1, 4, 3))
    assert p == [(1, 1), (2, 1), (1, 2), (2, 2), (2, 3)]
    assert len(set(p)) == 5


def test_blockfolge_3x3_von_hand():
    """3 Blöcke zu je 3: der erste Block hat die größten Ränge 7 8 9, dann 4 5 6, dann 1 2 3."""
    assert S.blockfolge(3, 3) == (7, 8, 9, 4, 5, 6, 1, 2, 3)
    assert S.blockfolge(2, 2) == (3, 4, 1, 2)
    paare = set(A.es_paare(S.blockfolge(3, 3)))
    assert paare == {(i, j) for i in (1, 2, 3) for j in (1, 2, 3)}     # jedes Gitterfeld genau einmal


# --- Schärfe (H2) ---------------------------------------------------------------------------------------------------------------------------

def test_haken_von_hand():
    """Form (2, 2): Haken 3 2 / 2 1, Produkt 12, f = 4!/12 = 2. Form (3, 3): Haken 4 3 2 / 3 2 1 = 144, f = 720/144 = 5.
    Form (3, 2, 1): Haken 5 3 1 / 3 1 / 1 = 45, f = 720/45 = 16."""
    assert A.haken_f((2, 2)) == 2 and A.haken_f((3, 3)) == 5 and A.haken_f((3, 2, 1)) == 16


def test_scharfe_folgen_n4_h2():
    """Genau vier Folgen der Länge 4 haben weder eine wachsende noch eine fallende Teilfolge der Länge 3."""
    scharf = sorted(p for p in permutations(range(1, 5)) if A.lis(p) <= 2 and A.lds(p) <= 2)
    assert scharf == [(2, 1, 4, 3), (2, 4, 1, 3), (3, 1, 4, 2), (3, 4, 1, 2)]
    assert A.scharf_anzahl(2, 2) == 4 == 2 ** 2


def test_scharfe_anzahlen_rechtecke():
    """f(3,3) = 5 -> 25 (2 Zeilen à 3), f(4,4) = 14 -> 196, f(3,3,3) = 42 -> 1764."""
    assert A.scharf_anzahl(3, 2) == 25 and A.scharf_anzahl(4, 2) == 196 and A.scharf_anzahl(3, 3) == 1764
    assert A.haken_f((3, 3, 3)) == 42


def test_gleichheitsfaelle_von_hand():
    """n = 6: Zerlegungen 1·6, 2·3, 3·2, 6·1 mit (f^Rechteck)² = 1 + 25 + 25 + 1 = 52. n = 4: 1 + 4 + 1 = 6. n = 9: 1 + 1764 + 1 = 1766."""
    assert A.gleichheitsfaelle(6) == 52 and A.gleichheitsfaelle(4) == 6 and A.gleichheitsfaelle(9) == 1766


# --- Handfolge n = 6 (H3) -------------------------------------------------------------------------------------------------------------------

def test_tableau_von_hand_h3(hand):
    """Einfügen: 1 | 1 3 | 1 3 6 | 2 verdrängt 3 (Zeile 2: 3) | 5 verdrängt 6 (Zeile 2: 3 6) | 4 verdrängt 5, 5 verdrängt 6 (Zeile 2: 3 5; Zeile 3: 6)."""
    assert A.tableau(hand) == [[1, 2, 4], [3, 5], [6]]
    assert A.form(hand) == (3, 2, 1)


def test_form_erste_zeile_ist_lis_und_zeilenzahl_lds(hand):
    lam = A.form(hand)
    assert lam[0] == A.lis(hand) == 3 and len(lam) == A.lds(hand) == 3


def test_anzahl_folgen_der_form_ist_f_quadrat_h3():
    """Form (3, 2, 1): f = 16, also 256 Folgen der Länge 6 mit dieser Form (Aufzählung aller 720)."""
    assert A.haken_f((3, 2, 1)) ** 2 == 256
    assert sum(1 for p in permutations(range(1, 7)) if A.form(p) == (3, 2, 1)) == 256


def test_kapazitaet_handfolge_3_5_6(hand):
    """Fallende Stapel: [6, 5, 4] (Ankunft 3., 5., 6.) und [3, 2] (2., 4.) und [1]. W = 1: 6 5 4 (3); W = 2: dazu 3 2 (5); W = 3: alles (6)."""
    assert [A.kapazitaet_fluss(hand, w)[0] for w in (1, 2, 3)] == [3, 5, 6]
    assert [A.kapazitaet_form(A.form(hand), w) for w in (1, 2, 3)] == [3, 5, 6]


def test_belegung_handfolge_mit_zwei_stapeln_laesst_rang_1_draussen(hand):
    """Mit zwei Stapeln passen 5; die einzige Teilmenge aus 5 Containern mit LIS <= 2 lässt den Rang 1 weg (von Hand: ohne 3, 6, 2, 5 oder 4 bleibt 1 3 6 bzw. 1 2 5 bzw. 1 2 4 wachsend)."""
    c, stapel = A.kapazitaet_fluss(hand, 2)
    assert c == 5
    ranks = [[hand[i] for i in k] for k in stapel]
    assert sorted(x for k in ranks for x in k) == [2, 3, 4, 5, 6]
    assert all(k[i] > k[i + 1] for k in ranks for i in range(len(k) - 1))
    assert A.pruefe_belegung(hand, stapel, 2)


def test_belegung_handfolge_mit_drei_stapeln_ist_vollstaendig(hand):
    c, stapel = A.kapazitaet_fluss(hand, 3)
    assert c == 6 and sorted(i for k in stapel for i in k) == list(range(6))
    assert A.pruefe_belegung(hand, stapel, 3)


# --- Falle (H4) -----------------------------------------------------------------------------------------------------------------------------

def test_falle_blockfolge_spalten_2_4_6_zeilen_3_6_6(block6):
    """(4, 5, 6, 1, 2, 3): Tableau 1 2 3 / 4 5 6, Form (3, 3). Spalten (2, 2, 2): Summe 2 / 4 / 6. Zeilen: 3 / 6 / 6.
    Von Hand: ein Stapel nimmt nur 4 1, 5 2 oder 6 3 (Länge 2); drei Stapel [4,1], [5,2], [6,3] nehmen alle sechs."""
    assert A.tableau(block6) == [[1, 2, 3], [4, 5, 6]]
    lam = A.form(block6)
    assert lam == (3, 3) and A.konjugiert(lam) == (2, 2, 2)
    assert [A.kapazitaet_form(lam, w) for w in (1, 2, 3)] == [2, 4, 6]
    assert [A.kapazitaet_form(lam, w, fallend=False) for w in (1, 2, 3)] == [3, 6, 6]
    assert [A.kapazitaet_fluss(block6, w)[0] for w in (1, 2, 3)] == [2, 4, 6]


def test_identitaet_und_umkehrfolge():
    """Identität (alles wächst): jeder Container braucht einen eigenen Stapel, Kapazität = W. Umkehrfolge: alles passt in einen Stapel."""
    ident, umk = tuple(range(1, 7)), tuple(range(6, 0, -1))
    assert [A.kapazitaet_fluss(ident, w)[0] for w in (1, 2, 3)] == [1, 2, 3]
    assert [A.kapazitaet_fluss(umk, w)[0] for w in (1, 2, 3)] == [6, 6, 6]
    assert A.kapazitaet_form(A.form(ident), 1, fallend=False) == 6     # die Zeilensumme würde alles in einen Stapel legen


def test_falle_statistik_n6_w1_464_von_720():
    """n = 6: nur die 256 Folgen der selbstkonjugierten Form (3, 2, 1) haben LIS = LDS; bei den übrigen 720 - 256 = 464 geben Zeilen- und Spaltensumme für W = 1
    verschiedene Zahlen."""
    st = A.falle_statistik(6, 1)
    assert st["folgen_anders"] == 464 == 720 - 256
    assert st["mittlere_ueberschaetzung"] == 0


# --- Wachsende Stapel -----------------------------------------------------------------------------------------------------------------------

def test_wachsende_stapel_vertauschen_zeilen_und_spalten(block6):
    """Wachsende Stapel: die Identität passt ganz in einen Stapel, die Umkehrfolge braucht n Stapel; (4,5,6,1,2,3) hat zwei wachsende Teilfolgen 4 5 6 und 1 2 3."""
    ident = tuple(range(1, 7))
    assert A.kapazitaet_fluss(ident, 1, fallend=False)[0] == 6
    assert A.kapazitaet_fluss(tuple(range(6, 0, -1)), 2, fallend=False)[0] == 2
    assert [A.kapazitaet_fluss(block6, w, fallend=False)[0] for w in (1, 2)] == [3, 6]


# --- Kapazitätsgarantie und Höhe ------------------------------------------------------------------------------------------------------------

def test_garantie_wert_von_hand():
    """n = 6, W = 1, LIS = 3: min(6, 6/3) = 2. W = 2: min(6, 12/3) = 4. LIS = 1, W = 2: min(6, 12) = 6 (gekappt)."""
    assert A.garantie_wert(6, 1, 3) == 2 and A.garantie_wert(6, 2, 3) == 4 and A.garantie_wert(6, 2, 1) == 6


def test_hoehe_handbeispiel():
    """Folge 1 2 3 4 5 6 (alles wächst), W = 3 Stapel, Höhe 2: jeder Container braucht einen eigenen Stapel, es passen 3. Umkehrfolge 6 5 4 3 2 1 mit
    W = 3, H = 2: dreimal zwei Container = 6; mit H = 1: 3."""
    assert A.kapazitaet_hoehe((1, 2, 3, 4, 5, 6), 3, 2) == 3
    assert A.kapazitaet_hoehe((6, 5, 4, 3, 2, 1), 3, 2) == 6
    assert A.kapazitaet_hoehe((6, 5, 4, 3, 2, 1), 3, 1) == 3
    assert A.kapazitaet_hoehe((6, 5, 4, 3, 2, 1), 2, 2) == 4


def test_hoehe_n6_w3_h2_erreicht_612_von_720():
    """Querprobe zu `esz_tables.json`: min(W·H, c_W) = min(6, c_3) wird in 612 von 720 Folgen erreicht, sonst um genau 1 verfehlt."""
    erreicht = darunter = 0
    for p in permutations(range(1, 7)):
        ziel = min(6, A.kapazitaet_form(A.form(p), 3))
        c = A.kapazitaet_hoehe(p, 3, 2)
        assert c <= ziel
        if c == ziel:
            erreicht += 1
        else:
            assert ziel - c == 1
            darunter += 1
    assert (erreicht, darunter) == (612, 108)


# --- Formen und Verteilungen ----------------------------------------------------------------------------------------------------------------

def test_summe_f_quadrat_ist_n_fakultaet():
    import math

    for n in range(1, 13):
        assert sum(f2 for _l, f2, _a, _b in A.formenliste(n)) == math.factorial(n)


def test_partitionen_zahl():
    """Zahl der Partitionen: 1, 2, 3, 5, 7, 11, 15, 22, 30 für n = 1 bis 9 (Handwerte der Partitionszahlen)."""
    assert [len(list(A.partitionen(n))) for n in range(1, 10)] == [1, 2, 3, 5, 7, 11, 15, 22, 30]


def test_knappheit_n4_von_hand():
    """n = 4: Formen (4): f=1, LIS·LDS = 4·1; (3,1): f=3, 3·2 = 6; (2,2): f=2, 2·2 = 4; (2,1,1): f=3, 2·3 = 6; (1,1,1,1): f=1, 1·4 = 4.
    Folgen je Form f²: 1, 9, 4, 9, 1 (Summe 24). Σ f²·LIS·LDS = 4 + 54 + 16 + 54 + 4 = 132, geteilt durch 24 = 5,5. Gleichheit (Produkt 4): 1 + 4 + 1 = 6 von 24."""
    k = A.knappheit(4)
    assert k["e_produkt"] == Fraction(132, 24) == Fraction(11, 2)
    assert k["folgen_scharf"] == 6 and k["anteil_scharf"] == Fraction(1, 4)
    assert k["garantie_max"] == 2


def test_erwartete_kapazitaet_n3_von_hand():
    """n = 3: Formen (3): 1 Folge, (2,1): 4 Folgen, (1,1,1): 1 Folge. c_1 = Spalte 1: 1, 2, 3. E[c_1] = (1 + 8 + 3)/6 = 2."""
    assert A.erwartete_kapazitaet(3, 1) == 2
    assert A.erwartete_kapazitaet(3, 2) == Fraction(1 * 2 + 4 * 3 + 1 * 3, 6)      # c_2: 2, 3, 3
