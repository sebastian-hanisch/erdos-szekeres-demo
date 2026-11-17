"""Kennzahlen, Verdikte (reine Funktionen: Art, Text) und die Messreihe des Verweilzeit-Modells.

Jedes Verdikt der App ist `verdict_*(...) -> (Art, Text)`; die App ruft `getattr(st, Art)(Text)`. tests/test_verdicts.py prüft Schwellen und jede Zahl
im Text an handgesetzten Werten. Zähleinheit überall: Folgen der Länge n (alle n! gleich wahrscheinlich = Modell U), wo nichts anderes steht."""

import math
from dataclasses import dataclass
from fractions import Fraction

import esz_algorithm as A
import esz_constants as C
import esz_scenario as S
import esz_tables as T

# --- Zahlen als deutscher Text --------------------------------------------------------------------------------------------------------------

def de(x, nd=2) -> str:
    """Dezimalzahl mit Komma und echtem Minuszeichen; Nachkommastellen ohne abschließende Nullen (257,50 -> 257,5; 115,00 -> 115)."""
    x = float(x)
    if not math.isfinite(x):
        return "–"
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", "−")


def de_fest(x, nd=1) -> str:
    """Dezimalzahl mit Komma, immer mit `nd` Stellen."""
    return f"{float(x):.{nd}f}".replace(".", ",").replace("-", "−")


def tausend(n) -> str:
    """Ganzzahl mit geschütztem Leerzeichen als Tausendertrenner (362 880)."""
    return f"{int(n):,}".replace(",", " ")


def hoch(exponent: int) -> str:
    return str(exponent).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))


def anteil_text(x) -> str:
    """Anteil (0 bis 1) als Prozentzahl mit zwei gültigen Stellen unter 1 %, einer Nachkommastelle ab 1 %; unter 0,001 % als Zehnerpotenz des Anteils."""
    x = float(x)
    if x == 0:
        return "0 %"
    p = 100 * x
    if p < 0.001:
        exponent = math.floor(math.log10(x))
        return f"{de_fest(x / 10 ** exponent, 1)} · 10{hoch(exponent)}"
    nd = 1 if p >= 1 else 1 - math.floor(math.log10(p))
    return de_fest(p, nd) + " %"


def prozent(x, nd=1) -> str:
    """Anteil (0 bis 1) als Prozentzahl mit Komma, immer mit `nd` Stellen."""
    return de_fest(100 * float(x), nd) + " %"


def raenge_text(raenge) -> str:
    r = [str(x) for x in raenge]
    return ("Rang " if len(r) == 1 else "Ränge ") + ", ".join(r)


def form_text(lam) -> str:
    """Form als „(3, 2, 1)“ (ein Eintrag ohne Komma am Ende)."""
    return "(" + ", ".join(str(x) for x in lam) + ")"


def stapel_wort(w: int) -> str:
    return "Stapel" if w == 1 else "Stapeln"


# --- Experiment 1: Kapazität in W Stapeln ---------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class KapAnalyse:
    folge: tuple            # Ränge 1..n in Ankunftsreihenfolge
    n: int
    W: int
    fallend: bool
    tableau: tuple          # Schensted-Tableau P (Zeilen)
    lam: tuple              # Form
    lis: int
    lds: int
    tabelle: tuple          # je Stapelzahl W: {"W", "fluss", "spalten", "zeilen"}
    kap: int                # Kapazität bei der gewählten Stapelzahl (Fluss)
    stapel: tuple           # je Stapel die Ränge in Ankunftsreihenfolge (unten zuerst)
    draussen: tuple         # Ränge der Container, die in keinen Stapel passen, in Ankunftsreihenfolge


def analyse_kapazitaet(folge, W: int, richtung: str = "fallend") -> KapAnalyse:
    fallend = richtung == "fallend"
    n = len(folge)
    t = A.tableau(folge)
    lam = tuple(len(z) for z in t)
    li, ld = A.lis(folge), A.lds(folge)
    wmax = max(li if fallend else ld, W)
    zeilen = []
    for w in range(1, wmax + 1):
        zeilen.append({
            "W": w,
            "fluss": A.kapazitaet_fluss(folge, w, fallend)[0],
            "spalten": A.kapazitaet_form(lam, w, fallend=True),
            "zeilen": A.kapazitaet_form(lam, w, fallend=False),
        })
    kap, stapel_pos = A.kapazitaet_fluss(folge, W, fallend)
    drin = {i for k in stapel_pos for i in k}
    return KapAnalyse(
        folge=tuple(folge), n=n, W=W, fallend=fallend, tableau=tuple(tuple(z) for z in t), lam=lam, lis=li, lds=ld, tabelle=tuple(zeilen), kap=kap,
        stapel=tuple(tuple(folge[i] for i in k) for k in stapel_pos),
        draussen=tuple(folge[i] for i in range(n) if i not in drin),
    )


def verdict_kapazitaet(a: KapAnalyse) -> tuple:
    kopf = a.tabelle[: min(len(a.tabelle), 4)]
    ws = " / ".join(str(r["W"]) for r in kopf)
    cs = " / ".join(str(r["fluss"]) for r in kopf)
    satz = f"Schensted-Form {form_text(a.lam)}: in {ws} {stapel_wort(kopf[-1]['W'])} passen {cs} Container."
    if a.kap == a.n:
        satz += f" Mit {a.W} {stapel_wort(a.W)} passen alle {a.n} Container blockierfrei."
    else:
        satz += f" Mit {a.W} {stapel_wort(a.W)} liegen {a.kap} von {a.n} Containern blockierfrei, draußen bleibt {raenge_text(a.draussen)}."
    zeile = next(r for r in a.tabelle if r["W"] == a.W)
    richtig, falsch = (zeile["spalten"], zeile["zeilen"]) if a.fallend else (zeile["zeilen"], zeile["spalten"])
    name_richtig, name_falsch = ("Spalten", "Zeilen") if a.fallend else ("Zeilen", "Spalten")
    if falsch != richtig:
        satz += (f" Die Summe der ersten {a.W} {name_falsch} der Form ergäbe {falsch} statt {richtig}: für diese Stapel zählen die {name_richtig}.")
    else:
        satz += f" Zeilen- und Spaltensumme geben hier dieselbe Zahl ({richtig}); die Verwechslung fiele bei dieser Folge nicht auf."
    return ("success" if a.kap == a.n else "info"), satz


def falle_tabelle(ns=C.FALLE_N, ws=(1, 2, 3)) -> list:
    """Messreihe zur Falle (Zähleinheit Folgen, exakt aus den Formen): Anteil der Folgen, bei denen die Zeilensumme statt der Spaltensumme eine andere
    Kapazität gibt, je n und W; dazu die mittlere Überschätzung (Zeilen minus Spalten) und die größte Abweichung."""
    zeilen = []
    for n in ns:
        zeile = {"n": n}
        for w in ws:
            st = A.falle_statistik(n, w)
            zeile[f"anders_w{w}"] = st["anteil_anders"]
            zeile[f"mittel_w{w}"] = st["mittlere_ueberschaetzung"]
            zeile[f"groesste_w{w}"] = st["groesste_abweichung"]
        zeilen.append(zeile)
    return zeilen


def verdict_falle(tabelle: list) -> tuple:
    w1 = [float(z["anders_w1"]) for z in tabelle]
    n_von, n_bis = tabelle[0]["n"], tabelle[-1]["n"]
    mittel_null = all(z[f"mittel_w{w}"] == 0 for z in tabelle for w in (1, 2, 3))
    text = (f"Wer statt der Spalten die Zeilen der Form summiert, liegt bei W = 1 in {prozent(min(w1))} bis {prozent(max(w1))} aller Folgen "
            f"(n = {n_von} bis {n_bis}) daneben")
    if mittel_null:
        text += ", im Mittel über alle Folgen aber um 0 Container: der Fehler hebt sich im Mittel auf und ist bei den meisten, aber nicht bei allen Folgen trotzdem falsch."
    else:
        text += "."
    return "warning", text


# --- Experiment 2: Erdős-Szekeres, Gitter und Schärfe ---------------------------------------------------------------------------------------

@dataclass(frozen=True)
class EsAnalyse:
    a: int
    b: int
    ab: int
    beispiel: tuple             # Folge der Länge a·b + 1
    paare: tuple                # Paare (wachsend endend, fallend endend) der Beispielfolge
    aussen: tuple               # Paare außerhalb des a × b-Gitters
    block: tuple                # Blockfolge der Länge a·b
    paare_block: tuple
    scharf_formel: int          # (f^Rechteck)^2
    gleich_formel: int          # Folgen der Länge a·b mit LIS·LDS = a·b (Summe über alle Zerlegungen)
    gezaehlt_n: dict | None     # Aufzählung der Länge a·b (nur bis 9): {"folgen", "scharf", "gleich"}
    gezaehlt_n1: dict | None    # Aufzählung der Länge a·b + 1 (nur bis 9): {"folgen", "verletzungen"}


def analyse_es(a: int, b: int, seed: int) -> EsAnalyse:
    ab = a * b
    beispiel = S.zufallsfolge(ab + 1, seed)
    paare = tuple(A.es_paare(beispiel))
    block = S.blockfolge(a, b)
    gez_n = gez_n1 = None
    tab = T.aufzaehlung(ab)
    if tab is not None:
        gez_n = {
            "folgen": tab["folgen"],
            "scharf": sum(v for (li, ld), v in tab["paare"].items() if li <= a and ld <= b),
            "gleich": sum(v for (li, ld), v in tab["paare"].items() if li * ld == ab),
        }
    tab1 = T.aufzaehlung(ab + 1)
    if tab1 is not None:
        gez_n1 = {"folgen": tab1["folgen"], "verletzungen": sum(v for (li, ld), v in tab1["paare"].items() if li <= a and ld <= b)}
    return EsAnalyse(
        a=a, b=b, ab=ab, beispiel=beispiel, paare=paare, aussen=tuple(p for p in paare if p[0] > a or p[1] > b), block=block,
        paare_block=tuple(A.es_paare(block)), scharf_formel=A.scharf_anzahl(a, b), gleich_formel=A.gleichheitsfaelle(ab), gezaehlt_n=gez_n, gezaehlt_n1=gez_n1,
    )


def verdict_es(e: EsAnalyse) -> tuple:
    teile = []
    if e.gezaehlt_n1 is not None:
        teile.append(f"Länge {e.ab + 1} = {e.a}·{e.b} + 1: in {tausend(e.gezaehlt_n1['folgen'] - e.gezaehlt_n1['verletzungen'])} von "
                     f"{tausend(e.gezaehlt_n1['folgen'])} Folgen gibt es eine wachsende Teilfolge der Länge {e.a + 1} oder eine fallende der Länge {e.b + 1} "
                     f"({tausend(e.gezaehlt_n1['verletzungen'])} Ausnahmen; Aufzählung vorgerechnet).")
    else:
        teile.append(f"Länge {e.ab + 1} = {e.a}·{e.b} + 1: zu viele Folgen zum Aufzählen; der Satz gilt für jede Länge über das Gitter-Argument "
                     "(die Paare sind verschieden, das Gitter hat nur a·b Felder).")
    if e.gezaehlt_n is not None:
        teile.append(f"Länge {e.ab}: genau {tausend(e.gezaehlt_n['scharf'])} Folgen haben weder eine wachsende Teilfolge der Länge {e.a + 1} noch eine fallende "
                     f"der Länge {e.b + 1} (Hakenformel: {tausend(e.scharf_formel)}); LIS·LDS = {e.ab} gilt in {tausend(e.gezaehlt_n['gleich'])} von "
                     f"{tausend(e.gezaehlt_n['folgen'])} Folgen ({anteil_text(Fraction(e.gezaehlt_n['gleich'], e.gezaehlt_n['folgen']))}).")
    else:
        teile.append(f"Länge {e.ab}: nach der Hakenformel genau {tausend(e.scharf_formel)} Folgen ohne wachsende Teilfolge der Länge {e.a + 1} und ohne fallende "
                     f"der Länge {e.b + 1}; die Aufzählung aller {e.ab}! Folgen ist nicht vorgerechnet (nur bis Länge 9).")
    return "success", " ".join(teile)


def wort_tabelle() -> list:
    """Messreihe zu den Gleichständen (vorgerechnet): je n die Zahl der Wörter und der Verletzungen je Paarung."""
    zeilen = []
    for n in range(1, T.N_WORT_MAX + 1):
        w = T.woerter(n)
        zeilen.append({"n": n, "woerter": w["woerter"], **w["verletzungen"]})
    return zeilen


def verdict_wort(wort: tuple) -> tuple:
    n = len(wort)
    p = A.paarungen(wort)
    li, ds = A.lis(list(wort)), A.lds_schwach(list(wort))
    text = (f"Wort {S.folge_text(wort)} (n = {n}): streng wachsend {li}, schwach fallend {ds}, Produkt {li * ds}"
            f"{' ≥ ' + str(n) if li * ds >= n else ' < ' + str(n)}; streng × streng: {p['streng_streng']}"
            f"{' ≥ ' + str(n) if p['streng_streng'] >= n else ' < ' + str(n) + ' (verletzt)'}.")
    return ("warning" if p["streng_streng"] < n else "info"), text


# --- Experiment 3: Wie knapp ist die Garantie? ----------------------------------------------------------------------------------------------

def knapp_tabelle(ns=C.KNAPP_TABELLE_N) -> list:
    zeilen = []
    for n in ns:
        k = A.knappheit(n)
        zeilen.append({**k, "quotient": k["e_produkt"] / n, "zwei_wurzel": 2 * math.sqrt(n)})
    return zeilen


def verdict_knapp(k: dict) -> tuple:
    n = k["n"]
    quot = k["e_produkt"] / n
    return "info", (f"n = {n}: im Mittel ist LIS·LDS = {de(k['e_produkt'], 1)} ({de(quot, 2)} · n), die Garantie sagt nur ≥ {n}. "
                    f"Scharf (LIS·LDS = {n}) ist die Garantie in {anteil_text(k['anteil_scharf'])} der Folgen. "
                    f"Im Mittel ist max(LIS, LDS) = {de(k['e_max'], 1)} gegen die Garantie ⌈√{n}⌉ = {k['garantie_max']}.")


# --- Experiment 4: Kapazitätsgarantie und Höhe ----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class GarantieAnalyse:
    n: int
    W: int
    folgen: int
    verteilung: dict            # {c_W: Folgen} aus den Formen
    verletzungen: int
    gleich: int
    gleich_aufgerundet: int
    je_lis: dict
    aufzaehlung: dict | None    # vorgerechnete Aufzählung (n <= 9): {"verteilung", "verletzungen", "gleich"}
    stimmt_ueberein: bool | None


def analyse_garantie(n: int, W: int) -> GarantieAnalyse:
    st = A.garantie_statistik(n, W)
    tab = T.aufzaehlung(n)
    auf = None
    ueber = None
    if tab is not None and W in tab["kapazitaet"]:
        auf = {"verteilung": tab["kapazitaet"][W], "verletzungen": tab["garantie_verletzungen"][W], "gleich": tab["garantie_gleich"][W]}
        ueber = (auf["verteilung"] == st["verteilung"] and auf["verletzungen"] == st["verletzungen"] and auf["gleich"] == st["gleich"])
    return GarantieAnalyse(n=n, W=W, folgen=st["folgen"], verteilung=st["verteilung"], verletzungen=st["verletzungen"], gleich=st["gleich"],
                           gleich_aufgerundet=st["gleich_aufgerundet"], je_lis=st["je_lis"], aufzaehlung=auf, stimmt_ueberein=ueber)


def verdict_garantie(g: GarantieAnalyse) -> tuple:
    text = (f"n = {g.n}, W = {g.W}: c_W ≥ min(n, W·n/LIS) gilt in {tausend(g.folgen - g.verletzungen)} von {tausend(g.folgen)} Folgen "
            f"({tausend(g.verletzungen)} Ausnahmen); scharf (Gleichheit) in {tausend(g.gleich)} Folgen ({anteil_text(Fraction(g.gleich, g.folgen))}).")
    if g.aufzaehlung is not None:
        text += " Die vorgerechnete Aufzählung aller Folgen " + ("stimmt mit der Rechnung aus den Formen überein." if g.stimmt_ueberein else "weicht von der Rechnung aus den Formen ab.")
    return ("success" if g.verletzungen == 0 else "error"), text


@dataclass(frozen=True)
class HoehenAnalyse:
    n: int
    W: int
    H: int
    folgen: int
    erreicht: int
    darunter: int
    darueber: int
    luecke: int


def analyse_hoehe(n: int, W: int, H: int) -> HoehenAnalyse | None:
    t = T.hoehe(n, W, H)
    if t is None:
        return None
    return HoehenAnalyse(n=n, W=W, H=H, folgen=t["folgen"], erreicht=t["erreicht"], darunter=t["darunter"], darueber=t["darueber"], luecke=t["groesste_luecke"])


def verdict_hoehe(h: HoehenAnalyse) -> tuple:
    text = (f"n = {h.n}, W = {h.W}, H = {h.H}: min(W·H, c_W) = min({h.W * h.H}, c_W) wird in {tausend(h.erreicht)} von {tausend(h.folgen)} Folgen erreicht, "
            f"in {tausend(h.darunter)} Folgen um höchstens {h.luecke} verfehlt, in {tausend(h.darueber)} Folgen überschritten (alle Folgen aufgezählt, vorgerechnet).")
    return ("success" if h.darueber == 0 and h.darunter == 0 else "info"), text


# --- Experiment 5: Verweilzeit-Modell -------------------------------------------------------------------------------------------------------

def d_wert(d_text: str):
    """D als Zahl bzw. D_UNENDLICH aus dem Wert des Reglers."""
    return S.D_UNENDLICH if d_text == "inf" else float(d_text)


def simuliere_v(n: int, anzahl: int, seed: int, w_max: int = C.W_V_MAX) -> dict:
    """Mittlere Kapazität im Verweilzeit-Modell: für jedes D der Liste dieselben `anzahl` Ziehungen (gemeinsame Zufallszahlen), je Folge die Kapazität
    c_W = Summe der ersten W Spalten der Form (Greene-Kleitman; gegen den Fluss geprüft in tests/test_oracle_erdos_szekeres.py).
    Ergebnis je D und W: Mittel von c_W/n, Standardfehler des Mittels, Anteil der Folgen, die ganz passen (LIS <= W); dazu mittlere LIS und LDS."""
    ziehungen = S.ziehungen_v(n, anzahl, seed)
    ergebnis = {}
    for d_text in C.D_OPTIONEN:
        D = d_wert(d_text)
        s1 = [0.0] * (w_max + 1)
        s2 = [0.0] * (w_max + 1)
        ganz = [0] * (w_max + 1)
        s_lis = s_lds = 0
        for expo in ziehungen:
            folge = S.folge_v(expo, D)
            lam = A.form(folge)
            spalten = A.konjugiert(lam)
            s_lis += lam[0]
            s_lds += len(lam)
            c = 0
            for w in range(1, w_max + 1):
                if w - 1 < len(spalten):
                    c += spalten[w - 1]
                x = c / n
                s1[w] += x
                s2[w] += x * x
                if lam[0] <= w:
                    ganz[w] += 1
        zeilen = {}
        for w in range(1, w_max + 1):
            mittel = s1[w] / anzahl
            varianz = max(0.0, s2[w] / anzahl - mittel * mittel) * anzahl / max(1, anzahl - 1)
            zeilen[w] = {"mittel": mittel, "se": math.sqrt(varianz / anzahl), "ganz": ganz[w] / anzahl, "ganz_n": ganz[w]}
        ergebnis[d_text] = {"lis": s_lis / anzahl, "lds": s_lds / anzahl, "w": zeilen}
    return {"n": n, "anzahl": anzahl, "seed": seed, "d": ergebnis}


def exakt_uniform(n: int, w_max: int = C.W_V_MAX) -> dict:
    """Modell U exakt aus den Formen: {W: {"mittel": E[c_W]/n, "ganz": Anteil der Folgen mit LIS <= W}}."""
    return {w: {"mittel": float(A.erwartete_kapazitaet(n, w)) / n, "ganz": float(A.anteil_ganz_passend(n, w)[1])} for w in range(1, w_max + 1)}


def verdict_v(sim: dict, exakt: dict, d_text: str, w: int) -> tuple:
    n = sim["n"]
    z = sim["d"][d_text]["w"][w]
    u = exakt[w]
    band = 1.96 * z["se"]
    text = (f"Verweilzeit-Modell, n = {n}, D = {S.d_text(d_wert(d_text))}, {sim['anzahl']} Folgen (Zufalls-Seed {sim['seed']}): in {w} {stapel_wort(w)} "
            f"passen im Mittel {prozent(z['mittel'])} der Container (± {de_fest(100 * band)} Prozentpunkte, 95-%-Band des Mittels); "
            f"ganz passen {z['ganz_n']} von {sim['anzahl']} Folgen ({prozent(z['ganz'])}). Uniform (exakt aus den Formen): {prozent(u['mittel'])} und {prozent(u['ganz'])} der Folgen passen ganz.")
    return "info", text
