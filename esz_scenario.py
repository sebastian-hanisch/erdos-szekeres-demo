"""Szenario: Ankunftsfolgen von Containern (ausgedachtes Modell, keine reale Ankunftsfolge), gesetzte Beispiele und Eingabe-Prüfung.

Zufall nur über den ganzzahligen SplitMix64 aus esz_rng.py (auf jeder Plattform dieselben Folgen zum selben Zufalls-Seed).

Modell U (uniform): alle n! Ankunftsfolgen gleich wahrscheinlich.
Modell V (Verweilzeit): Container i kommt zur Zeit i an (Abstand 1), bleibt eine exponentialverteilte Zeit mit Mittel D und fährt zur Zeit
i + D·E_i ab (E_i exponentialverteilt mit Mittel 1); der Abholrang ist die Reihenfolge der Abfahrtszeiten (Gleichstände nach dem Index). Je größer D,
desto weniger hängt der Rang an der Ankunftsreihenfolge; für D gegen unendlich ordnet allein E_i, das ist Modell U. Nur die RANGFOLGE der Abfahrten
geht ein. Die Modelle sind ausgedacht und keine Nachbildung eines Hafens oder Bahnhofs.
"""

import math

import esz_constants as C
from esz_rng import SplitMix64

D_UNENDLICH = None   # Kennzeichen für D gegen unendlich (Modell U über dieselben Ziehungen)


def zufallsfolge(n: int, seed: int) -> tuple:
    """Gleichverteilte Folge der Ränge 1..n (Modell U): Fisher-Yates mit ganzzahligem SplitMix64."""
    rng = SplitMix64(seed)
    liste = list(range(1, n + 1))
    rng.shuffle(liste)
    return tuple(liste)


def blockfolge(a: int, b: int) -> tuple:
    """b Blöcke zu je a aufeinanderfolgenden Rängen: innerhalb eines Blocks wachsend, die Blöcke fallend angeordnet. LIS = a, LDS = b.
    Beispiel a = b = 3: 7 8 9 4 5 6 1 2 3."""
    folge = []
    for k in range(b):
        start = (b - 1 - k) * a + 1
        folge.extend(range(start, start + a))
    return tuple(folge)


def ziehungen_v(n: int, anzahl: int, seed: int) -> list:
    """`anzahl` Folgen von je n Exponentialzahlen E_i (Mittel 1) aus einem SplitMix64-Strom. Eine Folge der Länge `anzahl` ist ein Präfix jeder
    längeren (gleicher Zufalls-Seed): mehr Folgen ändern die ersten nicht."""
    rng = SplitMix64(seed)
    return [tuple(rng.expovariate(1.0) for _ in range(n)) for _ in range(anzahl)]


def folge_v(expo, D) -> tuple:
    """Ankunftsfolge (Ränge) aus den Ziehungen E_i und der mittleren Verweilzeit D; D = D_UNENDLICH ordnet allein nach E_i (Modell U)."""
    n = len(expo)
    if D is D_UNENDLICH:
        zeit = list(expo)
    else:
        zeit = [i + D * e for i, e in enumerate(expo)]
    ordnung = sorted(range(n), key=lambda i: (zeit[i], i))
    rang = [0] * n
    for r, i in enumerate(ordnung):
        rang[i] = r + 1
    return tuple(rang)


def d_text(D) -> str:
    """D für die Anzeige (Komma als Dezimalzeichen)."""
    if D is D_UNENDLICH:
        return "∞ (uniform)"
    return f"{D:g}".replace(".", ",")


def parse_folge(text: str, n_max: int = C.N_FOLGE_MAX):
    """Liest eine Folge aus Text (Zahlen getrennt durch Leerzeichen, Komma oder Semikolon). Gibt (Folge der Ränge, None) zurück,
    wobei beliebige paarweise verschiedene ganze Zahlen auf die Ränge 1..n abgebildet werden, oder (None, Fehlermeldung)."""
    teile = [t for t in text.replace(",", " ").replace(";", " ").split() if t]
    if not teile:
        return None, "Die Folge ist leer: bitte Zahlen eingeben (zum Beispiel 1 3 6 2 5 4)."
    try:
        werte = [int(t) for t in teile]
    except ValueError:
        return None, "Nur ganze Zahlen sind erlaubt (zum Beispiel 1 3 6 2 5 4)."
    if len(werte) > n_max:
        return None, f"Höchstens {n_max} Container: die Folge hat {len(werte)}."
    if len(set(werte)) != len(werte):
        return None, "Doppelte Zahlen: Container mit gleichem Rang gehören zu den Gleichständen (Abschnitt „Mit Gleichständen“), hier müssen alle Zahlen verschieden sein."
    werte_sortiert = sorted(werte)
    rang = {w: i + 1 for i, w in enumerate(werte_sortiert)}
    return tuple(rang[w] for w in werte), None


def parse_wort(text: str, laenge_max: int = C.WORT_MAX):
    """Liest ein Wort (Gleichstände erlaubt): ganze Zahlen, getrennt durch Leerzeichen, Komma oder Semikolon. Gibt (Wort, None) oder (None, Meldung)."""
    teile = [t for t in text.replace(",", " ").replace(";", " ").split() if t]
    if not teile:
        return None, "Das Wort ist leer: bitte Zahlen eingeben (zum Beispiel 2 2 2 2)."
    try:
        werte = tuple(int(t) for t in teile)
    except ValueError:
        return None, "Nur ganze Zahlen sind erlaubt (zum Beispiel 2 2 2 2)."
    if len(werte) > laenge_max:
        return None, f"Höchstens {laenge_max} Zahlen: das Wort hat {len(werte)}."
    return werte, None


def folge_text(folge) -> str:
    return " ".join(str(x) for x in folge)


def ceil_sqrt(n: int) -> int:
    return math.isqrt(n - 1) + 1 if n > 0 else 0
