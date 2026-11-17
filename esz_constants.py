"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets.

Komplexität an den Reglergrenzen (Rechenbudget, DEMO-PLAYBOOK §1c): Fluss O(W·n^3) bei n <= 20, Formenliste n = 40: 37 338 Partitionen mit je
einer Hakenformel (rund 0,5 s, einmal je n zwischengespeichert), Modell V: n·Folgen = höchstens 40 · 1000 = 40 000 Exponentialzahlen (rund 2 s,
zwischengespeichert je Zufalls-Seed), Aufzählungen aller n! Folgen nie live, nur vorgerechnet (esz_tables.json)."""

# --- Regler ---------------------------------------------------------------------------------------------------------------------------------
SEED_MAX, DEFAULT_SEED = 999999, 2024

N_FOLGE_MAX = 20            # Experiment 1: höchstens so viele Container in der Eingabe (die Belegung wird gezeichnet)
WORT_MAX = 12               # Gleichstände: Wortlänge der Eingabe
W1_MIN, W1_MAX, DEFAULT_W1 = 1, 8, 2
N_ZUFALL_MIN, N_ZUFALL_MAX, DEFAULT_N_ZUFALL = 3, 20, 10
AB_MIN, AB_MAX, DEFAULT_A, DEFAULT_B = 1, 8, 3, 3
N_KNAPP_MIN, N_KNAPP_MAX, DEFAULT_N_KNAPP = 4, 40, 10
N_G_MIN, N_G_MAX, DEFAULT_N_G = 3, 9, 8
W_G_MIN, W_G_MAX, DEFAULT_W_G = 1, 4, 2
N_H_MIN, N_H_MAX, DEFAULT_N_H = 4, 7, 6
W_H_OPTIONEN = (2, 3)
H_H_MIN, H_H_MAX = 2, 4
DEFAULT_W_H, DEFAULT_H_H = 3, 2
N_V_MIN, N_V_MAX, DEFAULT_N_V = 10, 40, 10
ANZ_V_MIN, ANZ_V_MAX, ANZ_V_SCHRITT, DEFAULT_ANZ_V = 200, 1000, 100, 500
W_V_MIN, W_V_MAX, DEFAULT_W_V = 1, 6, 3
RICHTUNGEN = ("fallend", "wachsend")
RICHTUNG_TEXT = {"fallend": "fallende Stapel (Container: oben liegt der kleinste Rang)", "wachsend": "wachsende Stapel (zum Vergleich)"}
D_OPTIONEN = ("0.5", "1", "2", "4", "8", "16", "inf")   # mittlere Verweilzeit D in Ankunftsabständen; "inf" = uniform (Modell U)
DEFAULT_D_V = "2"
W_STAPEL_ANZEIGE = (1, 2, 3, 4, 5, 6, 7, 8)             # Spalten der Kurven in Experiment 5

SEED_ES_2X2 = 49            # zufallsfolge(5, 49) = (2, 5, 1, 4, 3): die Beispielfolge des Beweisgitters 2 × 2 ist die Handfolge der README
DEFAULT_FOLGE = "1 3 6 2 5 4"
DEFAULT_WORT = "3 1 3 2 1"

# Messreihen der README und der Tabellen (feste Zufalls-Seeds, nie ein einzelner Seed als Befund)
FALLE_N = (5, 6, 7, 8, 9, 10)
KNAPP_TABELLE_N = (4, 6, 8, 10, 20, 40)
MESS_SEEDS = (16000, 16001)

# --- Farben ---------------------------------------------------------------------------------------------------------------------------------
COLOR_STAPEL = ("#2F6B65", "#4c78a8", "#e0a030", "#9a5b9e", "#c0504d", "#5b8c3a", "#7a6a4f", "#3b8ea5")
COLOR_DRAUSSEN = "rgba(150,150,150,0.55)"
COLOR_SPALTEN = "#2F6B65"      # Spalten der Form, die zur Kapazität zählen
COLOR_ZEILEN = "#c0504d"       # Zeilen: die falsche Summe
COLOR_GITTER_AUSSEN = "#c0504d"
COLOR_LINE = "#4c78a8"
COLOR_BAND = "rgba(76,120,168,0.18)"

# --- Presets (jedes legt ALLE Regler fest; nicht genannte Regler bekommen ihren Standardwert) -------------------------------------------------
STANDARD = {
    "seed": DEFAULT_SEED, "folge": DEFAULT_FOLGE, "w1": DEFAULT_W1, "richtung": "fallend", "n_zufall": DEFAULT_N_ZUFALL,
    "a": DEFAULT_A, "b": DEFAULT_B, "wort": DEFAULT_WORT, "n_knapp": DEFAULT_N_KNAPP,
    "n_g": DEFAULT_N_G, "w_g": DEFAULT_W_G, "n_h": DEFAULT_N_H, "w_h": DEFAULT_W_H, "h_h": DEFAULT_H_H,
    "n_v": DEFAULT_N_V, "anz_v": DEFAULT_ANZ_V, "d_v": DEFAULT_D_V, "w_v": DEFAULT_W_V,
}

# Die Folgen „Fast sortiert“ und „Zufallsfolge“ stammen aus dem ganzzahligen SplitMix64 (tests/test_presets.py prüft, dass die Texte stimmen).
FOLGE_FAST_SORTIERT = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 20 17 19 18"
FOLGE_ZUFALL_20 = "3 19 1 14 20 7 8 4 18 6 13 15 16 17 5 11 12 10 9 2"

_PRESETS_ROH = {
    "Handfolge n = 6 (Voreinstellung)": {},
    "Blockfolge 3 × 3": {"folge": "7 8 9 4 5 6 1 2 3", "w1": 3, "a": 3, "b": 3},
    "Falle: Blockfolge 4 5 6 1 2 3": {"folge": "4 5 6 1 2 3", "w1": 2},
    "Identität (alles wächst)": {"folge": "1 2 3 4 5 6 7 8", "w1": 2},
    "Fast sortiert (D = 1)": {"folge": FOLGE_FAST_SORTIERT, "w1": 3, "n_v": 20, "d_v": "1", "w_v": 3},
    "Zufallsfolge uniform n = 20": {"folge": FOLGE_ZUFALL_20, "w1": 3, "n_knapp": 20, "n_v": 20, "d_v": "inf", "w_v": 3},
    "Gleichstände (2, 2, 2, 2)": {"wort": "2 2 2 2"},
    "ES 2 × 2": {"folge": "2 5 1 4 3", "w1": 2, "a": 2, "b": 2, "seed": SEED_ES_2X2},
}
PRESETS = {name: {**STANDARD, **werte} for name, werte in _PRESETS_ROH.items()}
PRESET_HELP = {
    "Handfolge n = 6 (Voreinstellung)": "Die Folge 1 3 6 2 5 4 mit Form (3, 2, 1): in 1, 2, 3 Stapel passen 3, 5, 6 Container.",
    "Blockfolge 3 × 3": "Drei Blöcke zu je drei wachsenden Rängen, die Blöcke fallend: eine der scharfen Folgen der Länge 9 (LIS · LDS = 9, LIS = LDS = 3).",
    "Falle: Blockfolge 4 5 6 1 2 3": "Zeilen und Spalten der Form unterscheiden sich: Spaltensumme 2 / 4 / 6, Zeilensumme 3 / 6 / 6.",
    "Identität (alles wächst)": "Jeder Container braucht einen eigenen Stapel: Kapazität 1 / 2 / 3 bei 1 / 2 / 3 Stapeln.",
    "Fast sortiert (D = 1)": "Eine Folge aus dem Verweilzeit-Modell mit D = 1 (Container fahren fast in Ankunftsreihenfolge ab).",
    "Zufallsfolge uniform n = 20": "Eine gleichverteilte Folge von 20 Containern (Modell U); Experimente 3 und 5 mit n = 20.",
    "Gleichstände (2, 2, 2, 2)": "Alle Container haben den Rang 2: streng wachsend 1, schwach fallend 4.",
    "ES 2 × 2": "Beweisgitter 2 × 2 mit der Folge 2 5 1 4 3 (n = 5 = 2·2 + 1; Zufalls-Seed 49): LIS = 2, LDS = 3, das Paar (2, 3) liegt außerhalb des Gitters.",
}
