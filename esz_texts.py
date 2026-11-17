"""Texte der App (Einleitung, Erklärung, Grenzen, Formeln). Sie stehen hier, damit die Tests sie lesen und gegen die README halten können."""

GITHUB = "https://github.com/sebastian-hanisch/"
NACHBARN = {
    "tableaux": f"[tableaux-rsk-demo]({GITHUB}tableaux-rsk-demo)",
    "zufall": f"[zufallsfolgen-lis-demo]({GITHUB}zufallsfolgen-lis-demo)",
    "patience": f"[patience-stapel-demo]({GITHUB}patience-stapel-demo)",
    "umstauen": f"[sortierbar-umstauen-demo]({GITHUB}sortierbar-umstauen-demo)",
    "mhs": f"[mehrhafenstau-demo]({GITHUB}mehrhafenstau-demo)",
    "kak": f"[ketten-antiketten-demo]({GITHUB}ketten-antiketten-demo)",
}

EINLEITUNG = """
**Container kommen nacheinander an und werden in Stapeln abgelegt; jeder hat einen Abholrang (1 = wird zuerst geholt).** Blockierfrei heißt: nie umsetzen. Ein Container darf also nur auf einen mit **größerem** Rang gelegt werden, jeder Stapel ist in Ankunftsreihenfolge eine **fallende** Teilfolge. Stehen nur **W Stapel** da, passt nicht immer alles. Die Seite fragt: Wie viele Container passen (**Kapazität**; nach dem Lehrbuchsatz von Greene-Kleitman die Summe der ersten W Spalten der Schensted-Form, hier nur nachgerechnet)? Was garantiert **jede** Folge (**Erdős–Szekeres**: LIS · LDS ≥ n)? Und wie selten ist diese Garantie wirklich scharf?

Die Folgen stammen aus einem **ausgedachten Ankunftsmodell** (alle n! Folgen gleich wahrscheinlich, oder Container mit zufälliger Verweilzeit): ein Modell, **keine reale Ankunftsfolge** eines Hafens oder Bahnhofs. Weiter unten: die **Kernfragen 1 bis 3**, die Experimente 4 und 5, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""

SO_FUNKTIONIERT = """
1. **Stapel fallend füllen.** Ein Container darf nur auf einen Stapel, dessen oberster Container einen größeren Rang hat; in Ankunftsreihenfolge ist ein Stapel eine fallende Teilfolge. Die **Mindestzahl** Stapel, damit alles blockierfrei passt, ist die Länge der längsten **wachsenden** Teilfolge (LIS).
2. **Kapazität c_W:** die größte Zahl Container, die so in W Stapel passt (der Rest kommt in ein anderes Lager). Die App rechnet sie als **Min-Cost-Fluss**: W knotendisjunkte fallende Ketten mit möglichst vielen Containern; der Fluss liefert auch die Belegung.
3. **Kontrolle mit der Schensted-Form:** Fügt man die Folge Zahl für Zahl in ein Tableau ein (Zeilenverdrängen), entsteht eine Form. Ihre erste Zeile ist die LIS, die Zeilenzahl die LDS, und **c_W ist die Summe der ersten W Spalten** (Satz von Greene-Kleitman, hier nur nachgerechnet). Der Fluss und die Spaltensumme sind zwei getrennte Rechenwege.
4. **Warum das hilft:** Die Form macht aus einer Frage über viele Teilmengen eine Zählung von Zellen. Daraus folgen die Garantie (Experiment 2 und 3), die Falle „Zeilen statt Spalten“ (Kernfrage 3) und eine Kapazitätsgarantie (Experiment 4).
"""

GRENZEN = f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wo es weitergeht |
|---|---|---|
| **Unbegrenzte Stapelhöhe** | Mit Höhe H passt weniger: bei n = 6, W = 3, H = 2 erreicht min(W·H, c_W) nur 612 von 720 Folgen, sonst wird es um genau 1 verfehlt. Gemessen nur für n ≤ 7, W ≤ 3, H ≤ 4; **keine Formel**. | {NACHBARN['umstauen']} |
| **Alle Ränge verschieden** | Mit Gleichständen (gleicher Rang darf einen Stapel teilen) hält LIS · LDS ≥ n in allen Wörtern für die Paarung streng wachsend × schwach fallend, streng × streng verletzt es in 208 257 von 823 543 Wörtern (n = 7). | {NACHBARN['mhs']} |
| **Ausgedachtes Ankunftsmodell** | Das Verweilzeit-Modell ist keine reale Ankunftsfolge. Die Zahlen aus Experiment 5 gelten nur dort, für diese Parameter. | {NACHBARN['patience']} |
| **Greene-Satz als Rechenweg** | Die Gleichung „Kapazität = Summe der ersten W Spalten“ ist hier nur nachgerechnet (Fluss, Teilmengen, Zuordnungen), nicht bewiesen und nicht aus dem Original gelesen; für große n bleibt sie ein Lehrbuchsatz. | {NACHBARN['tableaux']} |
| **Aufzählung nur bis n = 9** | Alle n! Folgen sind nur bis Länge 9 aufgezählt (vorgerechnet); für größere n kommen die Zahlen exakt aus den Formen (setzt den Satz voraus). | {NACHBARN['zufall']} |
"""

FORMELN = r"""
**Konvention.** Container 1 bis n haben den Abholrang (1 = wird zuerst geholt); die Ankunftsfolge ist eine Permutation $\sigma = (\sigma_1, \dots, \sigma_n)$, $\sigma_i$ der Rang des $i$-ten ankommenden Containers. Ein Stapel ist **fallend**: ein Container darf nur auf einen mit größerem Rang. In Ankunftsreihenfolge ist ein Stapel also eine fallende Teilfolge, „blockierfrei“ heißt: nie umsetzen. Bei wachsenden Stapeln vertauschen sich Zeilen und Spalten.

| Symbol | Bedeutung |
|---|---|
| $\sigma$, $n$ | Ankunftsfolge der Ränge $1, \dots, n$ (paarweise verschieden) |
| $W$ | Zahl der Stapel (feste Zahl, unbegrenzte Höhe) |
| $c_W(\sigma)$ | **Kapazität**: größte Zahl Container, die blockierfrei in $W$ Stapel passt; $c_W = n$ genau dann, wenn $W \ge \mathrm{LIS}(\sigma)$ |
| $\mathrm{LIS}$, $\mathrm{LDS}$ | Länge der längsten streng wachsenden bzw. fallenden Teilfolge |
| $\lambda(\sigma)$ | **Schensted-Form**: Zeilenlängen des Tableaus beim Einfügen von $\sigma$; $\lambda_1 = \mathrm{LIS}$, Zahl der Zeilen $= \mathrm{LDS}$ |
| $\lambda'_j$ | Höhe der $j$-ten **Spalte** der Form |
| $f^\lambda$ | Zahl der Standard-Tableaux der Form $\lambda$ (Hakenformel) |
| scharf | die Garantie gilt mit Gleichheit |

**Kapazität als Optimierung.** Die Aufgabe ist: wähle $W$ paarweise disjunkte fallende Teilfolgen mit möglichst vielen Containern.

$$c_W(\sigma) = \max\Big\{ \sum_{k=1}^{W} |K_k| \;:\; K_1, \dots, K_W \text{ paarweise disjunkte fallende Teilfolgen von } \sigma \Big\}$$

**Fluss.** Knoten $\mathrm{ein}_i$, $\mathrm{aus}_i$ je Container, Quelle $s$, Senke $t$. Kanten: $s \to \mathrm{ein}_i$ (Kapazität 1, Kosten 0), $\mathrm{ein}_i \to \mathrm{aus}_i$ (Kapazität 1, Kosten $-1$), $\mathrm{aus}_i \to \mathrm{ein}_j$ für $i < j$ und $\sigma_i > \sigma_j$ (Kapazität 1, Kosten 0), $\mathrm{aus}_i \to t$ (Kapazität 1, Kosten 0). Der Fluss hat höchstens $W$ Einheiten; jede Einheit läuft auf einem kürzesten Weg (Bellman-Ford), solange er negative Kosten hat. Die Kosten des Flusses sind $-c_W$.

**Greene-Kleitman (Lehrbuchsatz, hier nur nachgerechnet).**

$$c_W(\sigma) = \lambda'_1 + \lambda'_2 + \dots + \lambda'_W$$

Für wachsende Stapel gilt dieselbe Gleichung mit den Zeilen: $\lambda_1 + \dots + \lambda_W$.

**Erdős–Szekeres.** Jede Folge der Länge $n > ab$ hat eine wachsende Teilfolge der Länge $a + 1$ oder eine fallende der Länge $b + 1$. Gleichwertig:

$$\mathrm{LIS}(\sigma) \cdot \mathrm{LDS}(\sigma) \ge n$$

*Beweis über das Gitter:* Das Paar $(\ell_i, d_i)$ aus der Länge der längsten wachsenden und der längsten fallenden Teilfolge, die bei $i$ enden, ist für verschiedene $i$ verschieden (von zwei Positionen $i < j$ endet bei $j$ eine um eins längere wachsende oder fallende Teilfolge). Die $n$ Paare passen also nicht in ein Gitter mit weniger als $n$ Feldern.

**Schärfe.** Folgen der Länge $ab$ ohne wachsende Teilfolge der Länge $a+1$ und ohne fallende der Länge $b+1$ haben genau die Rechteckform $\lambda = (a, \dots, a)$ mit $b$ Zeilen; ihre Zahl ist

$$\big(f^{(a^b)}\big)^2, \qquad f^\lambda = \frac{n!}{\prod_{(i,j) \in \lambda} h(i,j)}, \qquad h(i,j) = \lambda_i - j + \lambda'_j - i + 1$$

Je Form $\lambda$ gibt es genau $(f^\lambda)^2$ Folgen (Schensted-Bijektion), zusammen $\sum_\lambda (f^\lambda)^2 = n!$.

**Kapazitätsgarantie (eigene Folgerung).** Die Form hat $\mathrm{LIS}$ Spalten, deren Höhen nicht wachsen; die ersten $W$ Spalten enthalten daher mindestens den Anteil $W/\mathrm{LIS}$ der $n$ Zellen:

$$c_W(\sigma) \ge \min\Big(n, \frac{W\,n}{\mathrm{LIS}(\sigma)}\Big)$$

Für $W = 1$ ist das Erdős–Szekeres.

**Verweilzeit-Modell.** Container $i$ kommt zur Zeit $i$ an und fährt zur Zeit $i + D\,E_i$ ab, $E_i$ unabhängig exponentialverteilt mit Mittel 1; der Rang ist die Reihenfolge der Abfahrten (Gleichstand nach dem Index). Für $D \to \infty$ ordnet nur $E_i$: alle $n!$ Folgen sind gleich wahrscheinlich.

**Quellen (Stufen nach dem Quellenbericht).** Erdős, Szekeres: *A combinatorial problem in geometry*, Compositio Math. 2 (1935), 463–470: Aussage und Schärfe im Wortlaut gelesen, die Formeln fehlen im Text-Layer. Schensted: *Longest increasing and decreasing subsequences*, Canad. J. Math. 13 (1961), 179–191: Lemma 3 und Sätze 1 und 2 im Wortlaut gelesen (S. 179–185). Aldous, Diaconis: *Longest increasing subsequences: from patience sorting to the Baik-Deift-Johansson theorem*, Bull. AMS 36 (1999), 413–432: Lemma 1 gelesen (S. 413–417). **Greene (1974) und Greene-Kleitman: nicht gelesen** (nur Suchtreffer), der Satz oben steht hier als Lehrbuchsatz mit eigener Nachrechnung. Dilworth und Mirsky nur über die README von """ + NACHBARN["kak"] + """. Die Kapazitätsgarantie ist eine eigene Folgerung, in keiner gelesenen Quelle belegt.
"""

KERNFRAGE_1_EINLEITUNG = (
    "**Die Folge** (Ränge in Ankunftsreihenfolge, beliebige verschiedene ganze Zahlen werden auf Ränge 1 bis n abgebildet) und die **Stapelzahl W** stellen Sie hier ein; "
    "das Schnellstart-Preset in der Seitenleiste setzt eine ganze Szenerie."
)
