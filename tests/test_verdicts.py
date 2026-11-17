"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt fertige Analysen; die Tests setzen sie von Hand, damit Schwellen und Zähler im Text direkt
geprüft werden und nicht über den Umweg einer Zufallsinstanz."""

from fractions import Fraction

import esz_algorithm as A
import esz_evaluation as ev

NB = " "   # geschütztes Leerzeichen als Tausendertrenner


# --- Zahlen als Text ------------------------------------------------------------------------------------------------------------------------

def test_de_und_prozent():
    assert ev.de(257.5, 2) == "257,5" and ev.de(115.0, 2) == "115" and ev.de(-1.5, 1) == "−1,5"
    assert ev.de_fest(3.0, 1) == "3,0" and ev.prozent(0.6444, 1) == "64,4 %"
    assert ev.tausend(362880) == f"362{NB}880"


def test_anteil_text_zwei_gueltige_stellen_unter_1_prozent():
    assert ev.anteil_text(Fraction(1, 4)) == "25,0 %"
    assert ev.anteil_text(Fraction(52, 720)) == "7,2 %"
    assert ev.anteil_text(Fraction(1766, 362880)) == "0,49 %"
    assert ev.anteil_text(Fraction(9728, 10 ** 7)) == "0,097 %"
    assert ev.anteil_text(0) == "0 %"
    assert ev.anteil_text(1.3259e-13) == "1,3 · 10⁻¹³"


def test_raenge_text_und_form_text():
    assert ev.raenge_text([1]) == "Rang 1" and ev.raenge_text([4, 7]) == "Ränge 4, 7"
    assert ev.form_text((3, 2, 1)) == "(3, 2, 1)" and ev.form_text((8,)) == "(8)"


# --- Kernfrage 1 ----------------------------------------------------------------------------------------------------------------------------

def _kap(folge, W, richtung="fallend"):
    return ev.analyse_kapazitaet(folge, W, richtung)


def test_verdict_kapazitaet_handfolge_nennt_form_kapazitaeten_und_draussen():
    art, text = ev.verdict_kapazitaet(_kap((1, 3, 6, 2, 5, 4), 2))
    assert art == "info"
    assert text.startswith("Schensted-Form (3, 2, 1): in 1 / 2 / 3 Stapeln passen 3 / 5 / 6 Container.")
    assert "Mit 2 Stapeln liegen 5 von 6 Containern blockierfrei, draußen bleibt Rang 1." in text
    assert "dieselbe Zahl (5)" in text


def test_verdict_kapazitaet_alles_passt_ist_success():
    art, text = ev.verdict_kapazitaet(_kap((1, 3, 6, 2, 5, 4), 3))
    assert art == "success" and "Mit 3 Stapeln passen alle 6 Container blockierfrei." in text and "draußen" not in text


def test_verdict_kapazitaet_ein_stapel_wort():
    _art, text = ev.verdict_kapazitaet(_kap((4, 5, 6, 1, 2, 3), 1))
    assert "Mit 1 Stapel liegen 2 von 6 Containern blockierfrei" in text and "Ränge" in text
    assert "ergäbe 3 statt 2" in text and "zählen die Spalten" in text


def test_verdict_kapazitaet_falle_blockfolge_w2():
    _art, text = ev.verdict_kapazitaet(_kap((4, 5, 6, 1, 2, 3), 2))
    assert "in 1 / 2 / 3 Stapeln passen 2 / 4 / 6 Container" in text and "ergäbe 6 statt 4" in text


def test_verdict_kapazitaet_wachsende_stapel_drehen_die_falle_um():
    """Wachsende Stapel: Kapazität = Zeilensumme; die Spaltensumme ist dann die falsche."""
    _art, text = ev.verdict_kapazitaet(_kap((4, 5, 6, 1, 2, 3), 1, "wachsend"))
    assert "in 1 / 2 Stapeln passen 3 / 6 Container" in text and "Summe der ersten 1 Spalten" in text
    assert "ergäbe 2 statt 3" in text and "zählen die Zeilen" in text


def test_verdict_kapazitaet_n1():
    art, text = ev.verdict_kapazitaet(_kap((1,), 3))
    assert art == "success" and "Form (1)" in text and "alle 1 Container" in text


def test_verdict_falle_nennt_spanne_und_mittel_null():
    zeilen = [{"n": 5, "anders_w1": Fraction(7, 10), "mittel_w1": 0, "mittel_w2": 0, "mittel_w3": 0},
              {"n": 6, "anders_w1": Fraction(29, 45), "mittel_w1": 0, "mittel_w2": 0, "mittel_w3": 0}]
    art, text = ev.verdict_falle(zeilen)
    assert art == "warning" and "64,4 % bis 70,0 %" in text and "n = 5 bis 6" in text and "um 0 Container" in text


def test_verdict_falle_ohne_mittelwert_null_behauptet_keine_aufhebung():
    zeilen = [{"n": 5, "anders_w1": Fraction(1, 2), "mittel_w1": Fraction(1, 3), "mittel_w2": 0, "mittel_w3": 0}]
    assert "um 0 Container" not in ev.verdict_falle(zeilen)[1]


# --- Kernfrage 2 ----------------------------------------------------------------------------------------------------------------------------

def test_verdict_es_3x3_aus_der_aufzaehlung():
    art, text = ev.verdict_es(ev.analyse_es(3, 3, 1))
    assert art == "success"
    assert f"genau 1{NB}764 Folgen" in text and f"(Hakenformel: 1{NB}764)" in text
    assert f"LIS·LDS = 9 gilt in 1{NB}766 von 362{NB}880 Folgen (0,49 %)" in text
    assert "Länge 10 = 3·3 + 1: zu viele Folgen" in text


def test_verdict_es_2x4_laenge_9_aufgezaehlt():
    _art, text = ev.verdict_es(ev.analyse_es(2, 4, 1))
    assert f"Länge 9 = 2·4 + 1: in 362{NB}880 von 362{NB}880 Folgen" in text and "(0 Ausnahmen" in text
    assert "genau 196 Folgen" in text and f"LIS·LDS = 8 gilt in 394 von 40{NB}320 Folgen (0,98 %)" in text


def test_verdict_es_2x2_n5_n4():
    _art, text = ev.verdict_es(ev.analyse_es(2, 2, 49))
    assert "Länge 5 = 2·2 + 1: in 120 von 120 Folgen" in text and "genau 4 Folgen" in text and "LIS·LDS = 4 gilt in 6 von 24 Folgen (25,0 %)" in text


def test_verdict_es_ueber_der_aufzaehlung_nennt_die_hakenformel():
    _art, text = ev.verdict_es(ev.analyse_es(4, 4, 1))
    assert "zu viele Folgen" in text and "nicht vorgerechnet (nur bis Länge 9)" in text and "nach der Hakenformel genau" in text


def test_verdict_wort_beide_zweige():
    art, text = ev.verdict_wort((2, 2, 2, 2))
    assert art == "warning" and "streng wachsend 1, schwach fallend 4, Produkt 4 ≥ 4" in text and "streng × streng: 1 < 4 (verletzt)" in text
    art, text = ev.verdict_wort((1, 2, 3))
    assert art == "info" and "streng × streng: 3 ≥ 3" in text      # LIS 3, LDS 1


def test_verdict_knapp_n4_exakt():
    """n = 4: Mittel 11/2 = 5,5; 5,5/4 = 1,375 (2 Stellen: 1,38); Mittel von max(LIS, LDS) = (1·4 + 9·3 + 4·2 + 9·3 + 1·4)/24 = 70/24 = 2,9."""
    art, text = ev.verdict_knapp(A.knappheit(4))
    assert art == "info" and "n = 4: im Mittel ist LIS·LDS = 5,5 (1,38 · n)" in text
    assert "Scharf (LIS·LDS = 4) ist die Garantie in 25,0 % der Folgen" in text and "max(LIS, LDS) = 2,9 gegen die Garantie ⌈√4⌉ = 2" in text


# --- Experiment 4 ---------------------------------------------------------------------------------------------------------------------------

def test_verdict_garantie_n8_w2():
    art, text = ev.verdict_garantie(ev.analyse_garantie(8, 2))
    assert art == "success"
    assert f"gilt in 40{NB}320 von 40{NB}320 Folgen (0 Ausnahmen)" in text and f"scharf (Gleichheit) in 1{NB}626 Folgen (4,0 %)" in text
    assert "stimmt mit der Rechnung aus den Formen überein" in text


def test_verdict_garantie_ohne_aufzaehlung_nennt_sie_nicht():
    n = 9 + 1
    # n = 10 liegt über der Reglergrenze der App, die Funktion rechnet trotzdem aus den Formen
    _art, text = ev.verdict_garantie(ev.analyse_garantie(n, 2))
    assert "vorgerechnete Aufzählung" not in text


def test_verdict_hoehe_n6_w3_h2():
    art, text = ev.verdict_hoehe(ev.analyse_hoehe(6, 3, 2))
    assert art == "info" and "min(W·H, c_W) = min(6, c_W) wird in 612 von 720 Folgen erreicht" in text
    assert "in 108 Folgen um höchstens 1 verfehlt, in 0 Folgen überschritten" in text


def test_verdict_hoehe_ohne_luecke_ist_success():
    art, text = ev.verdict_hoehe(ev.analyse_hoehe(6, 3, 4))
    assert art == "success" and "in 720 von 720 Folgen erreicht" in text


def test_analyse_hoehe_ausserhalb_der_tabelle_ist_none():
    assert ev.analyse_hoehe(8, 3, 2) is None and ev.analyse_hoehe(6, 5, 2) is None


# --- Experiment 5 ---------------------------------------------------------------------------------------------------------------------------

def test_verdict_v_mit_handgesetzter_messung():
    sim = {"n": 10, "anzahl": 500, "seed": 7, "d": {"2": {"lis": 7.0, "lds": 2.4, "w": {3: {"mittel": 0.581, "se": 0.005, "ganz": 0.0, "ganz_n": 0}}}}}
    exakt = {3: {"mittel": 0.8592, "ganz": 0.162}}
    art, text = ev.verdict_v(sim, exakt, "2", 3)
    assert art == "info"
    assert "n = 10, D = 2, 500 Folgen (Zufalls-Seed 7)" in text and "in 3 Stapeln passen im Mittel 58,1 % der Container (± 1,0 Prozentpunkte" in text
    assert "ganz passen 0 von 500 Folgen (0,0 %)" in text and "Uniform (exakt aus den Formen): 85,9 % und 16,2 % der Folgen passen ganz." in text


def test_d_wert():
    assert ev.d_wert("0.5") == 0.5 and ev.d_wert("inf") is None
