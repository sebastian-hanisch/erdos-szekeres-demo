# Kapazität und Schärfe: Erdős-Szekeres und Greene – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-erdos-szekeres-demo.streamlit.app/)** -->

Konzepte-Demo für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Themenfeld „Sortieren und Muster“ (Kombinatorik). Sie gehört zu den Demos über Sortiermaschinen und Permutationen. Nachbar-Demos: [patience-stapel-demo](https://github.com/sebastian-hanisch/patience-stapel-demo) fragt nach der **Mindestzahl** Stapel bei freier Stapelzahl; hier ist die Stapelzahl **fest**, und es geht darum, **wie viele** Container hineinpassen. [tableaux-rsk-demo](https://github.com/sebastian-hanisch/tableaux-rsk-demo) erklärt die Schensted-Form, die hier nur als Kontrolle auftaucht; [zufallsfolgen-lis-demo](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo) behandelt die Verteilung der LIS; [sortierbar-umstauen-demo](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) schlägt die Brücke zum Umstauen.

**Vehikel:** Container kommen nacheinander an, jeder hat einen Abholrang (1 = wird zuerst geholt). Die Ankunftsfolgen stammen aus einem **ausgedachten Modell** (alle n! Folgen gleich wahrscheinlich, oder Container mit zufälliger Verweilzeit D). Es ist ein Modell und **keine reale Ankunftsfolge** eines Hafens oder Bahnhofs; Zahlen daraus gelten nur dort.

## Warum dieses Problem

Ein Container darf blockierfrei (ohne spätere Umstapelung) nur auf einen mit größerem Rang gelegt werden, jeder Stapel ist in Ankunftsreihenfolge eine **fallende** Teilfolge. Bei freier Stapelzahl ist die Mindestzahl Stapel die Länge der längsten **wachsenden** Teilfolge (LIS). Stehen aber nur **W Stapel** da, passt nicht alles. Die Kernfragen: (1) Wie viele Container passen in W Stapel (**Kapazität** c_W)? (2) Was garantiert jede Folge, und wie selten ist die Garantie von Erdős-Szekeres (LIS · LDS ≥ n) wirklich scharf? (3) Was ändert sich, wenn man Zeilen und Spalten der Schensted-Form verwechselt?

## Modell

Container 1 bis n, Ankunftsfolge σ (Permutation der Ränge), **fallende** Stapel unbegrenzter Höhe (Höhe H nur in Experiment 4). Die Kapazität c_W(σ) ist die größte Zahl Container, die blockierfrei in W Stapel passt; c_W = n genau dann, wenn W ≥ LIS. **Zähleinheit überall: Folgen der Länge n** (alle n! gleich wahrscheinlich, Modell U), wo nichts anderes steht; Gleichstände (Wörter) nur im Abschnitt „Mit Gleichständen“ und dort gekennzeichnet. Das **Verweilzeit-Modell** (Modell V): Container i kommt zur Zeit i an und fährt zur Zeit i + D·E_i ab (E_i exponentialverteilt mit Mittel 1); der Rang ist die Reihenfolge der Abfahrten. Nur diese Rangfolge geht ein; für D → ∞ entsteht Modell U. Alle Formeln stehen im 📐-Expander der App (vollständiges Modell mit Konventionstabelle).

**Wortfalle:** „Kapazität“ meint hier die Zahl blockierfrei einlagerbarer Container bei fester Stapelzahl, **nicht** die Stapelplätze einer Bucht (so in [mehrhafenstau-demo](https://github.com/sebastian-hanisch/mehrhafenstau-demo)).

## Methodik

- **App-Kern: Min-Cost-Fluss** (`esz_algorithm.py`, `kapazitaet_fluss`): W knotendisjunkte fallende Ketten mit möglichst vielen Containern auf dem Vergleichbarkeits-DAG; liefert Zahl **und** Belegung.
- **Kontrolle: Schensted-Form.** Zeileneinfügen (`tableau`, `form`); erste Zeile = LIS, Zeilenzahl = LDS, und c_W = Summe der ersten W **Spalten** (fallende Stapel) bzw. **Zeilen** (wachsende Stapel). Das ist die Aussage des Satzes von Greene-Kleitman; hier ist sie **nur nachgerechnet** (siehe „Ehrliche Grenzen“).
- **Verteilungen über alle n! Folgen** exakt aus den Formen: Zahl der Folgen je Form = f² (Hakenformel), Erwartungswerte als Brüche (`fractions`), bis n = 40.
- **Aufzählungen aller Folgen** (n = 8: 40 320, n = 9: 362 880) und aller Wörter (n ≤ 7: 823 543) sind **vorgerechnet** und als `esz_tables.json` eingefroren (`tools/esz_make_tables.py`, mit `--check` neu gerechnet und exakt verglichen). In der App heißt jede solche Zahl „vorgerechnet“.
- **Zufall nur über den ganzzahligen SplitMix64** (`esz_rng.py`, Kopie der geprüften Vorlage); die Zufalls-Seeds geben auf jeder Plattform dieselben Folgen.
- **Quellen (Stufen nach dem Quellenbericht):** Erdős/Szekeres 1935 (Aussage und Schärfe im Wortlaut gelesen, die Formeln fehlen im Text-Layer), Schensted 1961 (Lemma 3, Sätze 1 und 2 im Wortlaut gelesen), Aldous/Diaconis 1999 (Lemma 1 gelesen). **Greene 1974 und Greene-Kleitman sind nicht gelesen** (nur Suchtreffer); Dilworth/Mirsky nur über die README von [ketten-antiketten-demo](https://github.com/sebastian-hanisch/ketten-antiketten-demo). Nichts davon ist neu: Erdős-Szekeres, Greene und die Hakenformel sind Lehrbuch. Neu ist nur die Vorführbarkeit mit Zähleinheit, die Zahl der scharfen Folgen als Anteil und die Prüfung der Kapazität auf mehreren Wegen. Die Kapazitätsgarantie c_W ≥ min(n, W·n/LIS) ist eine **eigene Folgerung** (zwei Zeilen) und steht in keiner gelesenen Quelle.

## Befunde (gemessen, keine Behauptungen)

Alle Aussagen gelten für Ankunftsfolgen ohne Gleichstände, unbegrenzte Stapelhöhe und Modell U (alle n! Folgen gleich wahrscheinlich), wo nichts anderes steht. Die Spalte „Beleg“ nennt den Test in `tests/test_claims.py` (Zahl → Test) oder die Datei, in der die Messung steht.

| Frage | Befund | Beleg |
|---|---|---|
| Handfolge (1, 3, 6, 2, 5, 4) | Tableau 1 2 4 / 3 5 / 6, Form (3, 2, 1), f = 16, also 256 von 720 Folgen mit dieser Form; Kapazität 3 / 5 / 6 bei W = 1 / 2 / 3; bei W = 2 bleibt der Container mit Rang 1 draußen, und nur er (von Hand: ohne jeden anderen bleibt eine wachsende Teilfolge der Länge 3) | `test_claim_handfolge` |
| Fluss = Spaltensumme | Fluss, Spaltensumme, Teilmengensuche und Zuordnungssuche geben dieselbe Kapazität: Teilmengen in allen Folgen n ≤ 6 (alle W, fallende und wachsende Stapel), Zuordnungen in allen Folgen n ≤ 5 (W ≤ 3) und n = 6 (W ≤ 2); Fluss gegen Spaltensumme in allen 40 320 Folgen n = 8 für W = 1 bis 3, jede Belegung gültig; in 120 Zufallsfolgen n = 7 bis 20 | `test_claim_fluss_gleich_spaltensumme_n8` (Marke `slow`), `tests/test_oracle_erdos_szekeres.py` |
| Erdős-Szekeres | LIS · LDS ≥ n in allen n! Folgen für n = 1 bis 9 (Aufzählung, 0 Ausnahmen); für jede Länge ein Satz (Paare verschieden) | `test_claim_es_alle_folgen_bis_n9` |
| Gleichheit (scharf) | Folgen mit LIS · LDS = n für n = 1 bis 9: 1, 2, 2, 6, 2, 52, 2, 394, 1766, jeweils gleich der Summe von (f^Rechteck)² über alle Zerlegungen n = a·b | `test_claim_gleichheitsfaelle` |
| Schärfe | Folgen der Länge a·b ohne wachsende Teilfolge der Länge a + 1 und ohne fallende der Länge b + 1: 4 (2 × 2), 25 (2 × 3), 196 (2 × 4), 1764 (3 × 3 = 42²); die Blockfolge 7 8 9 4 5 6 1 2 3 ist eine davon (LIS = LDS = 3) | `test_claim_scharfe_folgen` |
| Anteil scharf | Anteil der Folgen mit LIS · LDS = n: n = 4: 25,0 %; n = 6: 7,2 %; n = 8: 0,98 %; n = 9: 0,49 %; n = 10: 0,097 %; n = 20: 2,3 · 10⁻⁶; n = 40: 1,3 · 10⁻¹³ (exakt aus den Formen) | `test_claim_anteil_scharf` |
| Wie knapp im Mittel | E[LIS · LDS] / n = 1,375 (n = 4), 1,577 (6), 1,723 (8), 1,834 (10), 2,162 (20), 2,459 (40); das mittlere Produkt liegt im Bereich n = 4 bis 40 also um den Faktor 1,4 bis 2,5 über der Garantie n. Mittel von max(LIS, LDS) bei n = 40: 10,8 gegen die Garantie ⌈√40⌉ = 7; bei n = 10: 4,9 gegen 4 | `test_claim_knappheit` |
| Kapazitätsgarantie | c_W ≥ min(n, W·n/LIS) in allen n! Folgen für n = 2 bis 9 und W = 1 bis 4 (0 Ausnahmen); für W = 1 ist das Erdős-Szekeres. Gleichheit bei W = 1: 52 / 394 / 1766 Folgen (n = 6 / 8 / 9); bei W = 2: 157 / 1626 / 6626 (n = 6 / 8 / 9), bei n = 8 also 4,0 % der Folgen. Mit Aufrundung bei W = 1: 158 (21,9 %), 3391 (8,4 %), 43 671 (12,0 %) | `test_claim_kapazitaetsgarantie` |
| Anteil, der ganz passt | n = 8: W = 2: 1430 von 40 320 Folgen (3,55 %), W = 3: 15 767 (39,1 %), W = 4: 33 324 (82,65 %) (Aufzählung gegen Summe der f² über Formen mit erster Zeile ≤ W) | `test_claim_ganz_passend_n8` |
| Erwartete Kapazität | E[c_W] / n (Modell U, exakt): n = 10: 0,433 / 0,698 / 0,859 / 0,950 für W = 1 bis 4; n = 20: 0,331 / 0,560 / 0,722 / 0,836; n = 40, W = 1: 0,249 | `test_claim_erwartete_kapazitaet` |
| Falle Zeilen / Spalten | Wer statt der ersten W Spalten die ersten W Zeilen summiert, liegt bei W = 1 in 70,0 / 64,4 / 74,6 / 75,5 / 72,4 / 73,3 % der Folgen daneben (n = 5 bis 10), im Mittel aber um 0 Container; die größte Abweichung bei W = 1 ist n − 1 (n = 9: 8). Bei n = 6 und W = 1 durch Aufzählung bestätigt: 464 von 720 (nur die 256 Folgen der selbstkonjugierten Form (3, 2, 1) haben LIS = LDS). Blockfolge 4 5 6 1 2 3: Spaltensumme 2 / 4 / 6, Zeilensumme 3 / 6 / 6; Identität: 1 / 2 / 3, Umkehrfolge: 6 / 6 / 6 (n = 6) | `test_claim_falle` |
| Gleichstände | Mit gleichen Rängen (Wörter über 1 bis n der Länge n, alle n^n, n ≤ 7) gilt streng wachsend × schwach fallend ≥ n in allen Wörtern (823 543 bei n = 7, 0 Verletzungen); streng × streng verletzt es in 2 von 4, 15 von 27, 64 von 256, 1105 von 3125, 5376 von 46 656 und 208 257 von 823 543 Wörtern (25,3 %, n = 7). Beispiel (2, 2, 2, 2): 1 · 4 = 4 = n, aber 1 · 1 = 1 | `test_claim_gleichstaende` |
| Begrenzte Höhe | Die Kapazität bei Höhe H liegt in allen Folgen höchstens bei min(W·H, c_W), erreicht es nicht immer, und die Lücke ist in allen gemessenen Fällen genau 1: n = 6, W = 3, H = 2: 612 von 720 Folgen (108 darunter); n = 7, W = 2, H = 3: 4691 von 5040; n = 7, W = 3, H = 3: 4953; n = 7, W = 3, H = 4: 5037. **Nur n = 4 bis 7, W = 2 und 3, H = 2 bis 4 gemessen; keine Formel.** | `test_claim_hoehe` |
| Verweilzeit-Modell | n = 10, 1000 Folgen, Zufalls-Seed 16000 (zweiter Zufalls-Seed 16001 liegt im Band): mittlerer Anteil c_W / n bei W = 1 / 2 / 3 / 4: D = 0,5: 0,149 / 0,261 / 0,362 / 0,462, in 0 von 1000 Folgen passen alle in 3 Stapel; D = 2: 0,247 / 0,437 / 0,583 / 0,691; D = 16: 0,389 / 0,639 / 0,804 / 0,912; uniform (D = ∞): 0,432 / 0,698 / 0,860 / 0,954 gegen exakt 0,433 / 0,698 / 0,859 / 0,950. n = 20, D = 0,5: 0,088 / 0,158 / 0,215 / 0,266 gegen uniform (simuliert) 0,329 / 0,559 / 0,722 / 0,835. Je kleiner D, desto weniger passt. Das sind Stichprobenwerte: die Einzelzahlen aus 1000 Folgen streuen um etwa ± 0,003 (n = 10) bzw. ± 0,002 (n = 20), die dritte Dezimale ist nicht scharf (uniform bei W = 4: 0,954 gegen exakt 0,950, mit Zufalls-Seed 16001 0,947). Gilt nur in diesem ausgedachten Modell und für diese Parameter. | `test_claim_modell_v` |

**Rechenzeit der App (Messung dieser README, nicht im Test; Hinweis, Zeiten hängen von der Maschine ab):** Seitenaufbau mit den Voreinstellungen rund 1,7 s (AppTest, Windows); Fluss bei n = 40 und W = 8 etwa 2 ms; Formen und Erwartungswerte für n = 40 etwa 0,4 s (einmal je n zwischengespeichert); Verweilzeit-Modell bei n = 40 und 1000 Folgen rund 1,6 s (35 µs je Exponentialzahl über `decimal`, einmal je Zufalls-Seed zwischengespeichert). Die Cloud-Zeit ist nicht gemessen.

## Befunde und Korrekturen gegenüber dem Plan

- **Aufzählungen vorgerechnet statt live.** Vorgesehen war die Live-Aufzählung bis n = 8; gebaut sind alle Aufzählungen (n ≤ 9, Höhe n ≤ 7, Wörter n ≤ 7) als eingefrorene Tabelle, weil die Cloud-Zeit nicht gemessen ist. Die Tests rechnen n ≤ 7 immer, n = 8 und 9 mit der Marke `slow` neu.
- **Gleichstände ohne Umschalter.** Statt eines „ohne / mit Gleichständen“-Umschalters steht der Abschnitt „Mit Gleichständen“ immer unter dem Gitter, mit eigenem Eingabefeld (sonst wäre der Regler im Modus ohne Gleichstände wirkungslos).
- **Eingabe bis n = 20 statt 12,** weil der Fluss bei n = 40 und W = 8 nur etwa 2 ms braucht (die Belegung wird für bis zu 20 Container gezeichnet).
- **Verweilzeit-Modell: höchstens 1000 Folgen statt 5000.** Die plattformfeste Exponentialzahl (über `decimal`) kostet 35 µs; 40 · 5000 Zahlen sprengen das Budget von etwa 2 Sekunden. Die Zahlen stammen aus dem ganzzahligen SplitMix64 und weichen deshalb in der dritten Stelle von der früheren Messung mit einem anderen Zufallsstrom ab.
- **Gleichheitsfälle der Kapazitätsgarantie nur dort, wo die Garantie nicht auf n gekappt ist** (LIS ≥ W): für W = 2 stimmen 157 / 1626 / 6626 mit der früheren Messung überein. Die „Aufrundung“ ist nur für W = 1 angegeben (158 / 3391 / 43 671), weil die frühere Messung sie für W ≥ 2 anders definierte.
- **Rundung gegenüber der früheren Messung korrigiert:** Die Abweichungsquote der Falle bei n = 9 und W = 1 ist 72,4 % (exakt 72,449 %; die frühere Tabelle nannte 72,5 % nach zweimaligem Runden), und E[c_1] / n bei n = 10 ist 0,433 (exakt 0,4335; früher 0,434).
- **Beweisgitter-Beispiel aus dem Zufalls-Seed.** Das Preset „ES 2 × 2“ setzt den Zufalls-Seed 49; er liefert die Beispielfolge 2 5 1 4 3.
- **Hakenformel und Schensted-Einfügen sind hier neu geschrieben,** nicht aus einer Nachbar-Demo kopiert (Eigenständigkeit); sie sind gegen Eckenrekursion, Greene-Definition und Aufzählung geprüft.
- **Experiment 4 (Höhe und Garantie) bleibt auf der Seite, nichts gestrichen.** Gemessen im Browser (Messung dieser README, nicht im Test): Seitenhöhe rund 10 400 Pixel bei 1300 Pixel Breite, etwa zehn Bildschirmhöhen für drei Kernfragen und fünf Experimente.

## Ehrliche Grenzen

- **Greene-Kleitman ist hier nicht bewiesen und nicht aus dem Original gelesen.** Die Gleichung „Kapazität = Summe der ersten W Spalten“ ist für fallende Stapel auf mehreren Wegen **nachgerechnet** (bis n = 8, siehe oben); für größere n bleibt sie ein Lehrbuchsatz. Alle Zahlen „aus den Formen“ für n > 9 setzen ihn voraus.
- **Alle n! Folgen sind nur bis Länge 9 aufgezählt** (Höhe und Wörter bis Länge 7); darüber kommen die Zahlen exakt aus den Formen.
- **Die Kapazitätsgarantie ist nur für n ≤ 9 und W ≤ 4 aufgezählt;** der Beweis ist die Form-Argumentation (zwei Zeilen), nicht aus einer Quelle.
- **Begrenzte Höhe:** nur n = 4 bis 7, W = 2 und 3, H = 2 bis 4, keine Formel. Ob die Lücke 1 für größere n bleibt, ist nicht gemessen.
- **Gleichstände:** nur die Paarungen und die Zählung über alle Wörter n ≤ 7; die Zahl der scharfen Wörter (Analogon zu (f^Rechteck)²) ist nicht gemessen.
- **Verweilzeit-Modell:** ausgedacht, nur die Rangfolge der Abfahrten geht ein, 1000 Folgen je Zeile (Standardfehler des Mittels etwa 0,001 bis 0,003, bei n = 20 eher 0,001 bis 0,002). Es gibt keine reale Ankunftsfolge dazu.
- **2√n** (Größenordnung der erwarteten LIS) steht in der Tabelle von Experiment 3 nur als Vergleichsspalte; die Näherung selbst ist hier nicht gemessen.
- **Zeilen- und Spaltensumme geben bei selbstkonjugierter Form dieselbe Zahl:** die Falle fällt dann nicht auf (die Handfolge ist ein solcher Fall).

## Verifikation

- **Kern:** Handbeispiele von Hand (`tests/test_algorithm.py`): Beweisgitter 2 5 1 4 3, die vier scharfen Folgen der Länge 4, Handfolge 3 / 5 / 6, Falle 2 / 4 / 6 gegen 3 / 6 / 6, Gleichstände (2, 2, 2, 2).
- **Orakel (`tests/test_oracle_erdos_szekeres.py`)**, anderer Rechenweg als die App: Aufzählung aller Teilmengen (Mirsky), Aufzählung aller Zuordnungen, Form nach der Definition von Greene-Kleitman, Hakenformel gegen Eckenrekursion und gegen die Zählung der Folgen je Form, Erdős-Szekeres, Schärfe und Erwartungswerte (Brüche) gegen die Aufzählung aller Folgen, Höhe gegen die Aufzählung aller Zuordnungen mit Höhengrenze, Paarungen der Wörter gegen Doppelschleifen. Das Orakel ist an den Handbeispielen geprüft.
- **Eigenschaften (`tests/test_eigenschaften_erdos_szekeres.py`):** Umbenennen der Ränge, Spiegeln der Folge (fallend gegen wachsend), Komplement, Inverse, Zuwachs je weiterem Stapel nie wachsend, c_W = n ab W = LIS, ein weiterer Container ändert c_W um 0 oder 1, Erdős-Szekeres bei Zufallsfolgen.
- **Randfälle (`tests/test_edge_cases.py`):** n = 1, n = 2, leere Folge, W = 0, W > n, Höhe 0 und 1, a·b = 1, Grenzen inklusive, Eingaben über der Reglergrenze, Gleichstände.
- **Tabellen (`tests/test_tables.py`):** `esz_tables.json` gegen Neu-Rechnung und gegen die Formeln.
- **Claims (`tests/test_claims.py`):** jede Zahl dieser README; je Preset die erwartete Verdikt-Zeile (`tests/test_presets.py`); die RNG-Datei ist eine unveränderte Kopie der Vorlage (`tests/test_scenario.py`).
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum, jedes Preset, Worst-Case am Reglermaximum), Layout (Schnellstart in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben, jede Änderung eines Reglers hebt es auf), Footer, Laufzeit-Importe.

## Tests

220 Tests (`pytest tests/ -v`); davon haben sieben die Marke `slow` (rund 20 Sekunden: Aufzählungen n = 8 und 9, Wörter und Höhe bei n = 7, Fluss auf allen 40 320 Folgen n = 8); `pytest tests -m "not slow"` lässt sie aus. Die CI führt alle aus.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App (Kernfragen 1 bis 3, Experimente 4 und 5, Grenzen, Formeln) |
| `esz_algorithm.py` | Kern: Teilfolgen, Schensted-Form, Hakenformel, Kapazität per Fluss und Spaltensumme, Höhe, Garantie, Falle |
| `esz_constants.py` | Regler-Grenzen, Farben, Presets |
| `esz_evaluation.py` | Analysen, Verdikte (reine Funktionen), Verweilzeit-Modell |
| `esz_layout.py` | Fester Kopf (Stylesheet) |
| `esz_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste), Zufalls-Seed |
| `esz_rng.py` | Ganzzahliger SplitMix64 (Kopie der geprüften Vorlage) |
| `esz_scenario.py` | Ankunftsfolgen: Zufallsfolge, Blockfolge, Verweilzeit-Modell, Eingabe-Prüfung |
| `esz_tables.py`, `esz_tables.json` | Vorgerechnete Aufzählungen und ihre Rechnung |
| `esz_texts.py` | Texte der App (Einleitung, Grenzen, Formeln) |
| `esz_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tools/esz_make_tables.py` | Rechnet `esz_tables.json` neu (`--check` vergleicht) |
| `pytest.ini` | Marke `slow` |
| `requirements.txt`, `requirements-dev.txt` | Laufzeit-Bibliotheken (ungepinnt), dazu pytest |
| `tests/` | Handbeispiele, Orakel, Eigenschaften, Randfälle, Tabellen, Claims, Presets, Layout, Szenario, AppTest, Footer, Laufzeit-Importe; `_orakel.py` enthält die unabhängigen Rechenwege |

## Bewusst nicht umgesetzt

- **Live-Aufzählung aller Folgen** (siehe „Befunde und Korrekturen“): nur vorgerechnet.
- **Eine Formel für die Höhenlücke** und die Zahl der scharfen Wörter bei Gleichständen: nicht gemessen, nicht behauptet.
- **Näherungsformeln für die LIS** (2√n, Streuung, Vorfaktor): gehören zu [zufallsfolgen-lis-demo](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo); hier nur die Größe E[LIS · LDS] als Maß für die Garantie.
- **Erklärung der Schensted-Bijektion** und der Hakenformel: [tableaux-rsk-demo](https://github.com/sebastian-hanisch/tableaux-rsk-demo); hier nur die Form als Zahl.
- **Matching-Verfahren, Zeitplan, Teams** für allgemeine Ordnungen (Dilworth/Mirsky): [ketten-antiketten-demo](https://github.com/sebastian-hanisch/ketten-antiketten-demo); die Greene-Kleitman-Verallgemeinerung auf allgemeine Ordnungen wird nicht behauptet.
- **Eine reale Ankunftsfolge:** keine Quelle, keine erfundene Hafen- oder Bahnhofszahl.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
