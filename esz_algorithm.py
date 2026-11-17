"""Kern: Teilfolgen, Schensted-Form, Hakenformel, Kapazität in W Stapeln (Min-Cost-Fluss) und Erdős-Szekeres-Kennzahlen.

Konvention (wie in der README): Container 1 bis n haben den Abholrang (1 = wird zuerst geholt). Die Ankunftsfolge ist eine Folge von
Rängen. Ein Container-Stapel ist FALLEND: ein Container darf nur auf einen mit größerem Rang gelegt werden, oben liegt der kleinste.
In Ankunftsreihenfolge ist ein Stapel daher eine fallende Teilfolge; „blockierfrei“ heißt, dass nie umgesetzt werden muss.
Bei wachsenden Stapeln vertauschen sich die Rollen (Parameter `fallend=False`).

Rechenwege (der App-Kern ist der Fluss; die Form ist die Kontrolle):
  * `kapazitaet_fluss`: größte Zahl Container, die in W Stapel unbegrenzter Höhe passen, als Min-Cost-Fluss auf dem Vergleichbarkeits-DAG
    (W knotendisjunkte Ketten), liefert auch die Belegung.
  * `kapazitaet_form`: Summe der ersten W Spalten (fallende Stapel) bzw. Zeilen (wachsende Stapel) der Schensted-Form (Greene-Kleitman).
  * `kapazitaet_hoehe`: Zustandssuche bei begrenzter Stapelhöhe H.
Die Tests prüfen alle Wege gegeneinander und gegen Aufzählungen (tests/test_oracle_erdos_szekeres.py).
Reine Standardbibliothek; Brüche exakt (`fractions`)."""

import math
from bisect import bisect_left, bisect_right
from collections import deque
from fractions import Fraction
from functools import lru_cache

# --- Teilfolgen -----------------------------------------------------------------------------------------------------------------------------

def lis(a) -> int:
    """Länge der längsten STRENG wachsenden Teilfolge (Patience, O(n log n))."""
    spitzen: list = []
    for x in a:
        i = bisect_left(spitzen, x)
        if i == len(spitzen):
            spitzen.append(x)
        else:
            spitzen[i] = x
    return len(spitzen)


def lds(a) -> int:
    """Länge der längsten STRENG fallenden Teilfolge."""
    return lis([-x for x in a])


def lis_schwach(a) -> int:
    """Längste schwach wachsende Teilfolge (gleiche Werte erlaubt)."""
    spitzen: list = []
    for x in a:
        i = bisect_right(spitzen, x)
        if i == len(spitzen):
            spitzen.append(x)
        else:
            spitzen[i] = x
    return len(spitzen)


def lds_schwach(a) -> int:
    """Längste schwach fallende Teilfolge (gleiche Werte erlaubt)."""
    return lis_schwach([-x for x in a])


def paarungen(wort) -> dict:
    """Die vier Produkte (wachsend x fallend) für ein Wort mit möglichen Gleichständen.
    `streng_streng` ist die Paarung der Permutationen; `streng_schwach` (streng wachsend, schwach fallend) und `schwach_streng` halten
    LIS·LDS >= n für jedes Wort, `streng_streng` nicht (Beispiel (2, 2, 2, 2))."""
    w = list(wort)
    return {
        "streng_streng": lis(w) * lds(w),
        "streng_schwach": lis(w) * lds_schwach(w),
        "schwach_streng": lis_schwach(w) * lds(w),
        "schwach_schwach": lis_schwach(w) * lds_schwach(w),
    }


def standardisiere(a) -> tuple:
    """Ersetzt paarweise verschiedene Werte durch ihre Ränge 1..n (Ordnung bleibt, Namen ändern sich)."""
    werte = sorted(a)
    if len(set(werte)) != len(werte):
        raise ValueError("Werte müssen paarweise verschieden sein")
    rang = {w: i + 1 for i, w in enumerate(werte)}
    return tuple(rang[x] for x in a)


def es_paare(a) -> list:
    """Beweisgitter: für jede Position i das Paar (längste wachsende Teilfolge, die bei i endet; längste fallende, die bei i endet).
    Bei paarweise verschiedenen Werten sind die n Paare paarweise verschieden (Schubfach): von zwei Positionen i < j endet bei j eine wachsende
    oder eine fallende Teilfolge, die um eins länger ist."""
    n = len(a)
    inc, dec = [], []
    for i in range(n):
        li = di = 1
        for j in range(i):
            if a[j] < a[i]:
                li = max(li, inc[j] + 1)
            elif a[j] > a[i]:
                di = max(di, dec[j] + 1)
        inc.append(li)
        dec.append(di)
    return list(zip(inc, dec))


# --- Schensted-Form und Hakenformel ---------------------------------------------------------------------------------------------------------

def tableau(a) -> list:
    """Schensted-Zeileneinfügen (verdrängt den kleinsten größeren Wert); gibt das Tableau P als Liste von Zeilen zurück.
    Erste Zeile = LIS, Zahl der Zeilen = LDS (paarweise verschiedene Werte)."""
    zeilen: list = []
    for x in a:
        for zeile in zeilen:
            i = bisect_left(zeile, x)
            if i == len(zeile):
                zeile.append(x)
                x = None
                break
            zeile[i], x = x, zeile[i]
        if x is not None:
            zeilen.append([x])
    return zeilen


def form(a) -> tuple:
    """Zeilenlängen des Schensted-Tableaus."""
    return tuple(len(z) for z in tableau(a))


def konjugiert(lam) -> tuple:
    """Spaltenhöhen der Form."""
    if not lam:
        return ()
    return tuple(sum(1 for r in lam if r > j) for j in range(lam[0]))


def haken_f(lam) -> int:
    """Zahl der Standard-Tableaux der Form (Hakenformel): n! geteilt durch das Produkt der Hakenlängen."""
    n = sum(lam)
    lc = konjugiert(lam)
    produkt = 1
    for i, r in enumerate(lam):
        for j in range(r):
            produkt *= (r - j - 1) + (lc[j] - i - 1) + 1
    return math.factorial(n) // produkt


def partitionen(n, groesster=None):
    """Alle Partitionen von n als absteigende Tupel."""
    if groesster is None:
        groesster = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, groesster), 0, -1):
        for rest in partitionen(n - k, k):
            yield (k,) + rest


def kapazitaet_form(lam, W, fallend=True) -> int:
    """Summe der ersten W Spalten (fallende Stapel, Container) bzw. der ersten W Zeilen (wachsende Stapel) der Form."""
    if W <= 0:
        return 0
    return sum(konjugiert(lam)[:W]) if fallend else sum(lam[:W])


def rechteck(a, b) -> tuple:
    """Rechteckform mit b Zeilen der Länge a."""
    return (a,) * b


def scharf_anzahl(a, b) -> int:
    """Zahl der Folgen der Länge a·b ohne wachsende Teilfolge der Länge a+1 und ohne fallende der Länge b+1: (f der Rechteckform)^2.
    Eine Folge dieser Länge hat dann LIS = a und LDS = b."""
    return haken_f(rechteck(a, b)) ** 2


def gleichheitsfaelle(n) -> int:
    """Zahl der Folgen der Länge n mit LIS·LDS = n: Summe von (f^Rechteck)^2 über alle Zerlegungen n = a·b."""
    return sum(scharf_anzahl(a, n // a) for a in range(1, n + 1) if n % a == 0)


@lru_cache(maxsize=None)
def formenliste(n) -> tuple:
    """Alle Formen von n mit der Zahl der Folgen je Form (= f^2, RSK), LIS (erste Zeile) und LDS (Zeilenzahl): Tupel (lam, f2, lis, lds)."""
    zeilen = []
    for lam in partitionen(n):
        zeilen.append((lam, haken_f(lam) ** 2, lam[0] if lam else 0, len(lam)))
    return tuple(zeilen)


# --- Kennzahlen über alle n! Folgen (exakt aus den Formen) ----------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def produkt_verteilung(n) -> dict:
    """{LIS·LDS: Zahl der Folgen der Länge n}."""
    d: dict = {}
    for _lam, f2, li, ld in formenliste(n):
        d[li * ld] = d.get(li * ld, 0) + f2
    return dict(sorted(d.items()))


def knappheit(n) -> dict:
    """Wie knapp ist LIS·LDS >= n? Alles exakt als Brüche: Mittel von LIS·LDS und von max(LIS, LDS), Anteil der Folgen mit Gleichheit."""
    fak = math.factorial(n)
    s_prod = s_max = s_gleich = 0
    for _lam, f2, li, ld in formenliste(n):
        s_prod += f2 * li * ld
        s_max += f2 * max(li, ld)
        if li * ld == n:
            s_gleich += f2
    return {
        "n": n,
        "e_produkt": Fraction(s_prod, fak),
        "e_max": Fraction(s_max, fak),
        "anteil_scharf": Fraction(s_gleich, fak),
        "folgen_scharf": s_gleich,
        "garantie_max": math.isqrt(n - 1) + 1 if n > 0 else 0,   # ceil(sqrt(n)) in Ganzzahlen
    }


def erwartete_kapazitaet(n, W, fallend=True) -> Fraction:
    """E[c_W] über alle n! Folgen, exakt."""
    s = sum(f2 * kapazitaet_form(lam, W, fallend) for lam, f2, _li, _ld in formenliste(n))
    return Fraction(s, math.factorial(n))


def anteil_ganz_passend(n, W, fallend=True) -> tuple:
    """(Zahl, Anteil) der Folgen, die ganz in W Stapel passen: LIS <= W (fallende Stapel) bzw. LDS <= W (wachsende)."""
    z = sum(f2 for _lam, f2, li, ld in formenliste(n) if (li if fallend else ld) <= W)
    return z, Fraction(z, math.factorial(n))


def garantie_wert(n, W, lis_wert) -> Fraction:
    """Kapazitätsgarantie c_W >= min(n, W·n/LIS) (eigene Folgerung aus der Form: die ersten W der LIS Spalten haben mindestens den Anteil W/LIS der
    Zellen, weil die Spaltenhöhen nicht wachsen)."""
    return min(Fraction(n), Fraction(W * n, lis_wert))


def garantie_statistik(n, W) -> dict:
    """Über alle n! Folgen (aus den Formen, fallende Stapel): Verteilung von c_W, Verletzungen der Garantie, Gleichheitsfälle,
    Zeilen je LIS-Wert: {lis: (Folgen, kleinstes c_W, Garantie, Folgen mit c_W = Garantie)}."""
    verteilung: dict = {}
    verletzungen = gleich = gleich_aufgerundet = 0
    je_lis: dict = {}
    for lam, f2, li, _ld in formenliste(n):
        c = kapazitaet_form(lam, W)
        verteilung[c] = verteilung.get(c, 0) + f2
        g = garantie_wert(n, W, li)
        if c < g:
            verletzungen += f2
        # Gleichheit nur dort, wo die Garantie nicht auf n gekappt ist (LIS >= W); bei LIS < W passt ohnehin alles
        if li >= W and c == g:
            gleich += f2
        if li >= W and c == -(-g.numerator // g.denominator):
            gleich_aufgerundet += f2
        z = je_lis.setdefault(li, [0, n, g, 0])
        z[0] += f2
        z[1] = min(z[1], c)
        if li >= W and c == g:
            z[3] += f2
    return {
        "folgen": math.factorial(n),
        "verteilung": dict(sorted(verteilung.items())),
        "verletzungen": verletzungen,
        "gleich": gleich,
        "gleich_aufgerundet": gleich_aufgerundet,
        "je_lis": {k: tuple(v) for k, v in sorted(je_lis.items())},
    }


def falle_statistik(n, W) -> dict:
    """Falle Zeilen gegen Spalten (Zähleinheit Folgen, exakt aus den Formen): bei wie vielen Folgen gibt die Summe der ersten W ZEILEN statt der
    ersten W SPALTEN eine andere Kapazität? Dazu mittlere und größte Überschätzung (Zeilen minus Spalten)."""
    fak = math.factorial(n)
    anders = 0
    summe = 0
    groesste = 0
    for lam, f2, _li, _ld in formenliste(n):
        z = kapazitaet_form(lam, W, fallend=False)
        s = kapazitaet_form(lam, W, fallend=True)
        if z != s:
            anders += f2
            groesste = max(groesste, abs(z - s))
        summe += f2 * (z - s)
    return {"n": n, "W": W, "folgen_anders": anders, "anteil_anders": Fraction(anders, fak), "mittlere_ueberschaetzung": Fraction(summe, fak),
            "groesste_abweichung": groesste}


# --- Kapazität in W Stapeln: Min-Cost-Fluss -------------------------------------------------------------------------------------------------

class _Netz:
    """Kleines Netz für Min-Cost-Fluss mit Bellman-Ford (SPFA); Kanten paarweise gespeichert (Rückkante = Index ^ 1)."""

    def __init__(self, knoten):
        self.adj = [[] for _ in range(knoten)]
        self.nach: list = []
        self.kap: list = []
        self.kosten: list = []

    def kante(self, u, v, kap, kosten) -> int:
        e = len(self.nach)
        self.adj[u].append(e)
        self.nach.append(v)
        self.kap.append(kap)
        self.kosten.append(kosten)
        self.adj[v].append(e + 1)
        self.nach.append(u)
        self.kap.append(0)
        self.kosten.append(-kosten)
        return e

    def kuerzester_weg(self, s, t):
        unendlich = float("inf")
        dist = [unendlich] * len(self.adj)
        vor = [-1] * len(self.adj)
        in_queue = [False] * len(self.adj)
        dist[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            in_queue[u] = False
            for e in self.adj[u]:
                if self.kap[e] > 0 and dist[u] + self.kosten[e] < dist[self.nach[e]]:
                    dist[self.nach[e]] = dist[u] + self.kosten[e]
                    vor[self.nach[e]] = e
                    if not in_queue[self.nach[e]]:
                        in_queue[self.nach[e]] = True
                        queue.append(self.nach[e])
        return dist[t], vor


def kapazitaet_fluss(a, W, fallend=True) -> tuple:
    """Größte Zahl Container, die blockierfrei in W Stapel unbegrenzter Höhe passen, und eine Belegung.

    Modell: Vergleichbarkeits-DAG auf den Positionen (Kante i -> j für i < j, wenn a[i] > a[j] bei fallenden Stapeln bzw. a[i] < a[j] bei wachsenden).
    Gesucht sind W knotendisjunkte Ketten mit möglichst vielen Knoten. Netz: Quelle -> ein_i (Kapazität 1), ein_i -> aus_i (Kapazität 1, Kosten -1),
    aus_i -> ein_j (Kapazität 1) für jede DAG-Kante, aus_i -> Senke; W Einheiten Fluss, jede Einheit auf dem kürzesten Weg (Kosten höchstens 0).

    Rückgabe: (Kapazität, Stapel) mit Stapel = Liste von W Listen von POSITIONEN in Ankunftsreihenfolge (unten zuerst); Container draußen
    stehen in keinem Stapel. Die Stapel sind nach Größe absteigend sortiert."""
    n = len(a)
    if W <= 0 or n == 0:
        return 0, [[] for _ in range(max(W, 0))]
    quelle, senke = 0, 1

    def ein(i):
        return 2 + 2 * i

    def aus(i):
        return 3 + 2 * i

    netz = _Netz(2 + 2 * n)
    e_start = [netz.kante(quelle, ein(i), 1, 0) for i in range(n)]
    for i in range(n):
        netz.kante(ein(i), aus(i), 1, -1)
    for i in range(n):
        netz.kante(aus(i), senke, 1, 0)
    e_dag = {}
    for i in range(n):
        for j in range(i + 1, n):
            if (a[i] > a[j]) if fallend else (a[i] < a[j]):
                e_dag[(i, j)] = netz.kante(aus(i), ein(j), 1, 0)
    for _ in range(W):
        dist, vor = netz.kuerzester_weg(quelle, senke)
        if dist >= 0:
            break
        v = senke
        while v != quelle:
            e = vor[v]
            netz.kap[e] -= 1
            netz.kap[e ^ 1] += 1
            v = netz.nach[e ^ 1]
    nachfolger = {i: j for (i, j), e in e_dag.items() if netz.kap[e] == 0}
    stapel = []
    for i in range(n):
        if netz.kap[e_start[i]] == 0:
            kette = [i]
            while kette[-1] in nachfolger:
                kette.append(nachfolger[kette[-1]])
            stapel.append(kette)
    stapel.sort(key=lambda k: (-len(k), k[0]))
    stapel += [[] for _ in range(W - len(stapel))]
    return sum(len(k) for k in stapel), stapel


def pruefe_belegung(a, stapel, W, fallend=True) -> bool:
    """Zulässigkeitsprüfer: höchstens W Stapel, jeder Container höchstens einmal, jeder Stapel in Ankunftsreihenfolge fallend (bzw. wachsend)."""
    if len(stapel) > W:
        return False
    gesehen = set()
    for kette in stapel:
        for i in kette:
            if i in gesehen or not 0 <= i < len(a):
                return False
            gesehen.add(i)
        for p, q in zip(kette, kette[1:]):
            if not p < q or not ((a[p] > a[q]) if fallend else (a[p] < a[q])):
                return False
    return True


# --- Kapazität bei begrenzter Stapelhöhe ----------------------------------------------------------------------------------------------------

def kapazitaet_hoehe(a, W, H, fallend=True) -> int:
    """Größte Zahl Container in W Stapeln mit höchstens H Containern je Stapel (Zustandssuche über (oberster Rang, Höhe) je Stapel).
    Zustände werden als sortierte Mehrfachmenge gehalten (Stapel sind austauschbar). Für n <= 7 und kleine W, H gedacht."""
    if W <= 0 or H <= 0:
        return 0
    leer = (math.inf if fallend else -math.inf, 0)
    zustaende = {tuple([leer] * W): 0}
    for x in a:
        neu = dict(zustaende)
        for zust, c in zustaende.items():
            gesehen = set()
            for idx, (spitze, h) in enumerate(zust):
                if (spitze, h) in gesehen:
                    continue
                gesehen.add((spitze, h))
                passt = spitze > x if fallend else spitze < x
                if passt and h < H:
                    liste = list(zust)
                    liste[idx] = (x, h + 1)
                    ns = tuple(sorted(liste))
                    if neu.get(ns, -1) < c + 1:
                        neu[ns] = c + 1
        zustaende = neu
    return max(zustaende.values())
