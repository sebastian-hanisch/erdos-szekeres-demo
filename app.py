"""Kapazität und Schärfe: Erdős-Szekeres und Greene - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Wie viele Container passen blockierfrei in W Stapel (Min-Cost-Fluss, Kontrolle: Summe der ersten W Spalten der Schensted-Form), was garantiert
Erdős-Szekeres jeder Folge, und wie selten ist die Garantie scharf? Aufbau nach DEMO-PLAYBOOK §2; Zufall nur über den ganzzahligen SplitMix64.

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import esz_algorithm as A
import esz_constants as C
import esz_evaluation as ev
import esz_scenario as S
import esz_texts as X
from esz_layout import dunkles_design, kopf_css
from esz_presets import (
    SETTING_SPECS,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
    zufallsfolge_ziehen,
)
from esz_visualization import (
    build_form,
    build_garantie_je_lis,
    build_garantie_verteilung,
    build_gitter,
    build_knapp,
    build_stapel,
    build_v_kurven,
)

st.set_page_config(page_title="Kapazität und Schärfe – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _kapazitaet(folge, W, richtung):
    return ev.analyse_kapazitaet(folge, W, richtung)


@st.cache_data(show_spinner=False)
def _falle():
    return ev.falle_tabelle()


@st.cache_data(show_spinner=False)
def _es(a, b, seed):
    return ev.analyse_es(a, b, seed)


@st.cache_data(show_spinner="Rechne die Formen aller Folgen (bei n = 40 etwa eine Sekunde) …")
def _knapp(n):
    return A.knappheit(n), A.produkt_verteilung(n)


@st.cache_data(show_spinner=False)
def _knapp_tabelle():
    return ev.knapp_tabelle()


@st.cache_data(show_spinner=False)
def _garantie(n, W):
    return ev.analyse_garantie(n, W)


@st.cache_data(show_spinner="Rechne das Verweilzeit-Modell (bei n = 40 und 1000 Folgen etwa 2 Sekunden, auf der Cloud eher mehr) …")
def _modell_v(n, anzahl, seed):
    return ev.simuliere_v(n, anzahl, seed)


@st.cache_data(show_spinner=False)
def _uniform(n):
    return ev.exakt_uniform(n)


def _ausgabe(verdikt):
    kind, text = verdikt
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in esz_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Kapazität und Schärfe: Erdős-Szekeres und Greene")
st.markdown(X.EINLEITUNG)

with st.expander("So funktioniert Kapazität und Schärfe", expanded=True):
    st.markdown(X.SO_FUNKTIONIERT)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Zufall**")
    seed = st.number_input("Zufalls-Seed", *bounds("seed"), key="seed", step=1,
                           help="Gilt für die Zufallsfolge in Experiment 1, die Beispielfolge des Beweisgitters in Experiment 2 und das Verweilzeit-Modell in Experiment 5.")
    st.button("🎲 Neuen Zufalls-Seed ziehen", width="stretch", on_click=randomize_seed)
    st.caption("Alle weiteren Regler stehen im Hauptbereich bei ihrem Experiment.")

# ============================================================================================================================================
# Kernfrage 1: Kapazität
# ============================================================================================================================================

st.markdown("## ❓ Kernfrage 1: Wie viele Container passen in W Stapel? (Experiment 1)")
st.markdown(X.KERNFRAGE_1_EINLEITUNG)
folge_text = st.text_input("Folge der Ränge (Ankunftsreihenfolge)", key="folge", max_chars=120,
                           help=f"Ganze Zahlen, durch Leerzeichen getrennt, höchstens {C.N_FOLGE_MAX}. Beispiel: 1 3 6 2 5 4")
c1, c2, c3, c4 = st.columns([1, 1.3, 1, 1])
w1 = c1.slider("Stapelzahl W", *bounds("w1"), key="w1", help="So viele Stapel stehen zur Verfügung (unbegrenzte Höhe).")
richtung = c2.radio("Stapelart", C.RICHTUNGEN, key="richtung", format_func=lambda r: C.RICHTUNG_TEXT[r],
                    help="Container-Stapel fallen (oben liegt der kleinste Rang). Wachsende Stapel zeigen, wie sich Zeilen und Spalten vertauschen.")
n_zufall = c3.slider("Länge der Zufallsfolge", *bounds("n_zufall"), key="n_zufall", help="Länge der Folge, die der Knopf rechts zieht.")
c4.markdown("&nbsp;")
c4.button("🎲 Zufallsfolge ziehen", on_click=zufallsfolge_ziehen, width="stretch", help="Zieht eine gleichverteilte Folge (Modell U) mit dem Zufalls-Seed der Seitenleiste.")

folge, fehler = S.parse_folge(folge_text)
if fehler:
    st.warning(fehler)
else:
    a1 = _kapazitaet(folge, int(w1), richtung)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Container n", a1.n)
    m2.metric("Form", ev.form_text(a1.lam))
    m3.metric("Mindestzahl Stapel" if a1.fallend else "Mindestzahl (wachsende Stapel)", a1.lis if a1.fallend else a1.lds)
    m4.metric(f"Kapazität in {a1.W} {ev.stapel_wort(a1.W)}", f"{a1.kap} von {a1.n}")
    g1, g2 = st.columns([1.2, 1])
    with g1:
        st.markdown("**Belegung aus dem Fluss** (unten liegt, was zuerst ankam; Beschriftung: Rang)")
        st.plotly_chart(build_stapel(a1), width="stretch", key="chart_stapel")
    with g2:
        st.markdown("**Schensted-Form** (farbig: zählt zur Kapazität)")
        st.plotly_chart(build_form(a1), width="stretch", key="chart_form")
    tab = pd.DataFrame({
        "Stapelzahl W": [r["W"] for r in a1.tabelle],
        "Kapazität (Fluss)": [r["fluss"] for r in a1.tabelle],
        "Summe der ersten W Spalten": [r["spalten"] for r in a1.tabelle],
        "Summe der ersten W Zeilen": [r["zeilen"] for r in a1.tabelle],
        "gewählt": ["◀" if r["W"] == a1.W else "" for r in a1.tabelle],
    })
    st.dataframe(tab, hide_index=True, width="stretch")
    st.caption(("Für fallende Stapel (Container) gehört die Spaltensumme zur Kapazität, die Zeilensumme ist die Falle." if a1.fallend
                else "Für wachsende Stapel gehört die Zeilensumme zur Kapazität, die Spaltensumme ist die Falle.")
               + " Der Fluss ist der Rechenweg der App, die passende Summe die Kontrolle; beide stimmen in allen geprüften Folgen überein (siehe README).")
    _ausgabe(ev.verdict_kapazitaet(a1))

# ============================================================================================================================================
# Kernfrage 2: Garantie und Schärfe
# ============================================================================================================================================

st.markdown("---")
st.markdown("## ❓ Kernfrage 2: Was garantiert jede Folge, und wie selten ist die Garantie scharf? (Experimente 2 und 3)")

st.subheader("🔬 Experiment 2: Die Garantie und das Gitter")
st.caption("Erdős–Szekeres: Jede Folge der Länge a·b + 1 hat eine wachsende Teilfolge der Länge a + 1 oder eine fallende der Länge b + 1. "
           "Die Aufzählung aller Folgen bis Länge 9 ist vorgerechnet (esz_tables.json).")
e1, e2 = st.columns(2)
a_ = e1.slider("a (Länge der wachsenden Teilfolgen, die man vermeiden will, ist a + 1)", *bounds("a"), key="a")
b_ = e2.slider("b (Länge der fallenden Teilfolgen, die man vermeiden will, ist b + 1)", *bounds("b"), key="b")
es = _es(int(a_), int(b_), int(seed))
x1, x2, x3 = st.columns(3)
x1.metric("Länge a·b + 1", es.ab + 1)
x2.metric("scharfe Folgen der Länge a·b (Hakenformel)", ev.tausend(es.scharf_formel))
x3.metric("Gleichheit LIS·LDS = a·b (alle Zerlegungen)", ev.tausend(es.gleich_formel))
p1, p2 = st.columns(2)
with p1:
    st.plotly_chart(build_gitter(es.a, es.b, es.paare, es.beispiel, f"Beispielfolge der Länge {es.ab + 1} (Zufalls-Seed {int(seed)}): ein Punkt zu viel"),
                    width="stretch", key="chart_gitter_beispiel")
    st.caption(f"Folge: {S.folge_text(es.beispiel) if es.ab + 1 <= 24 else S.folge_text(es.beispiel[:24]) + ' …'}. LIS = {A.lis(es.beispiel)}, LDS = {A.lds(es.beispiel)}; "
               f"{len(es.aussen)} von {es.ab + 1} Paaren liegen außerhalb des {es.a} × {es.b}-Gitters.")
with p2:
    st.plotly_chart(build_gitter(es.a, es.b, es.paare_block, es.block, f"Blockfolge der Länge {es.ab}: jedes Gitterfeld genau einmal"),
                    width="stretch", key="chart_gitter_block")
    st.caption(f"Folge: {S.folge_text(es.block) if es.ab <= 24 else S.folge_text(es.block[:24]) + ' …'}. LIS = {es.a}, LDS = {es.b}: "
               "die Blockfolge ist eine der scharfen Folgen.")
_ausgabe(ev.verdict_es(es))

st.markdown("**Mit Gleichständen (Container gleichen Ranges teilen sich einen Stapel): die Paarung entscheidet.**")
st.caption("Mit gleichen Rängen darf ein Stapel schwach fallen. Dann gilt „streng wachsend × schwach fallend ≥ n“, aber nicht „streng wachsend × streng fallend ≥ n“.")
wort_text = st.text_input("Wort (Ränge mit möglichen Gleichständen)", key="wort", max_chars=80, help=f"Ganze Zahlen, höchstens {C.WORT_MAX}. Beispiel: 2 2 2 2")
wort, wort_fehler = S.parse_wort(wort_text)
if wort_fehler:
    st.warning(wort_fehler)
else:
    _ausgabe(ev.verdict_wort(wort))
wt = ev.wort_tabelle()
st.dataframe(pd.DataFrame({
    "Länge n": [z["n"] for z in wt],
    "Wörter über 1..n (n^n)": [ev.tausend(z["woerter"]) for z in wt],
    "streng × streng verletzt": [ev.tausend(z["streng_streng"]) for z in wt],
    "streng × schwach verletzt": [ev.tausend(z["streng_schwach"]) for z in wt],
    "schwach × streng verletzt": [ev.tausend(z["schwach_streng"]) for z in wt],
}), hide_index=True, width="stretch")
st.caption("Vorgerechnet (alle n^n Wörter, esz_tables.json): Zahl der Wörter, in denen das Produkt kleiner als n ist.")

st.subheader("🔬 Experiment 3: Wie knapp ist die Garantie im Mittel?")
n_knapp = st.slider("Länge n der Folgen", *bounds("n_knapp"), key="n_knapp",
                    help="Exakt aus den Formen aller n! Folgen (Hakenformel, Brüche), bis n = 40.")
kn, verteilung = _knapp(int(n_knapp))
st.plotly_chart(build_knapp(int(n_knapp), verteilung, kn["e_produkt"]), width="stretch", key="chart_knapp")
kt = _knapp_tabelle()
st.dataframe(pd.DataFrame({
    "n": [z["n"] for z in kt],
    "Mittel LIS·LDS": [float(z["e_produkt"]) for z in kt],
    "Mittel LIS·LDS / n": [float(z["quotient"]) for z in kt],
    "Mittel max(LIS, LDS)": [float(z["e_max"]) for z in kt],
    "⌈√n⌉ (Garantie)": [z["garantie_max"] for z in kt],
    "2√n": [float(z["zwei_wurzel"]) for z in kt],
    "Anteil scharf (LIS·LDS = n)": [ev.anteil_text(z["anteil_scharf"]) for z in kt],
}), hide_index=True, width="stretch", column_config={
    "Mittel LIS·LDS": st.column_config.NumberColumn(format="%.2f"),
    "Mittel LIS·LDS / n": st.column_config.NumberColumn(format="%.3f"),
    "Mittel max(LIS, LDS)": st.column_config.NumberColumn(format="%.2f"),
    "2√n": st.column_config.NumberColumn(format="%.2f"),
})
st.caption("Exakt aus den Formen (Modell U: alle n! Folgen gleich wahrscheinlich). 2√n ist eine Vergleichsspalte aus der Literatur (Größenordnung der erwarteten LIS) und hier nicht gemessen.")
_ausgabe(ev.verdict_knapp(kn))

# ============================================================================================================================================
# Kernfrage 3: Zeilen und Spalten
# ============================================================================================================================================

st.markdown("---")
st.markdown("## ❓ Kernfrage 3: Was ändert sich, wenn man Zeilen und Spalten verwechselt?")
st.caption("Zähleinheit: Folgen der Länge n (alle n! gleich wahrscheinlich), exakt aus den Formen. Falsch gerechnet heißt: die Summe der ersten W Zeilen statt der ersten W Spalten.")
ft = _falle()
st.dataframe(pd.DataFrame({
    "n": [z["n"] for z in ft],
    "andere Kapazität bei W = 1": [100 * float(z["anders_w1"]) for z in ft],
    "bei W = 2": [100 * float(z["anders_w2"]) for z in ft],
    "bei W = 3": [100 * float(z["anders_w3"]) for z in ft],
    "mittlere Überschätzung bei W = 1": [float(z["mittel_w1"]) for z in ft],
    "größte Abweichung bei W = 1": [z["groesste_w1"] for z in ft],
}), hide_index=True, width="stretch", column_config={
    "andere Kapazität bei W = 1": st.column_config.NumberColumn(format="%.1f %%"),
    "bei W = 2": st.column_config.NumberColumn(format="%.1f %%"),
    "bei W = 3": st.column_config.NumberColumn(format="%.1f %%"),
    "mittlere Überschätzung bei W = 1": st.column_config.NumberColumn(format="%.2f"),
})
_ausgabe(ev.verdict_falle(ft))

# ============================================================================================================================================
# Experiment 4: Kapazitätsgarantie und Höhe
# ============================================================================================================================================

st.markdown("---")
st.subheader("🔬 Experiment 4: Kapazitätsgarantie und Stapelhöhe")
st.caption("Garantie (eigene Folgerung aus der Form): in W Stapeln passen mindestens min(n, W·n/LIS) Container. Für W = 1 ist das Erdős–Szekeres.")
q1, q2 = st.columns(2)
n_g = q1.slider("Länge n", *bounds("n_g"), key="n_g", help="Alle n! Folgen bis n = 9 sind vorgerechnet.")
w_g = q2.slider("Stapelzahl W", *bounds("w_g"), key="w_g")
g = _garantie(int(n_g), int(w_g))
q3, q4 = st.columns(2)
with q3:
    st.plotly_chart(build_garantie_verteilung(g), width="stretch", key="chart_garantie_verteilung")
with q4:
    st.plotly_chart(build_garantie_je_lis(g), width="stretch", key="chart_garantie_je_lis")
_ausgabe(ev.verdict_garantie(g))

st.markdown("**Mit begrenzter Stapelhöhe H** (alle Folgen aufgezählt, vorgerechnet; nur n ≤ 7, W ≤ 3, H ≤ 4)")
h1, h2, h3 = st.columns(3)
n_h = h1.slider("Länge n", *bounds("n_h"), key="n_h", help="Alle n! Folgen aufgezählt, nur bis n = 7.")
w_h = h2.radio("Stapelzahl W", C.W_H_OPTIONEN, key="w_h", horizontal=True)
h_h = h3.slider("Stapelhöhe H", *bounds("h_h"), key="h_h")
ha = ev.analyse_hoehe(int(n_h), int(w_h), int(h_h))
_ausgabe(ev.verdict_hoehe(ha))
hz = [ev.analyse_hoehe(int(n_h), int(w_h), h) for h in range(C.H_H_MIN, C.H_H_MAX + 1)]
st.dataframe(pd.DataFrame({
    "H": [h.H for h in hz], "Folgen": [ev.tausend(h.folgen) for h in hz], "min(W·H, c_W) erreicht": [ev.tausend(h.erreicht) for h in hz],
    "darunter": [ev.tausend(h.darunter) for h in hz], "darüber": [ev.tausend(h.darueber) for h in hz], "größte Lücke": [h.luecke for h in hz],
}), hide_index=True, width="stretch")

# ============================================================================================================================================
# Experiment 5: Verweilzeit-Modell
# ============================================================================================================================================

st.markdown("---")
st.subheader("🔬 Experiment 5: Wie viel passt bei kurzer und bei langer Verweilzeit?")
st.caption("Ausgedachtes Verweilzeit-Modell, **keine reale Ankunftsfolge**: Container i kommt zur Zeit i, bleibt im Mittel D Ankunftsabstände und fährt dann ab; der Rang ist die "
           "Reihenfolge der Abfahrten. Je kleiner D, desto näher an „fast sortiert“. D = ∞ ist Modell U (alle Folgen gleich wahrscheinlich). Nur die Rangfolge der Abfahrten geht ein.")
v1, v2, v3, v4 = st.columns(4)
n_v = v1.slider("Länge n", *bounds("n_v"), key="n_v")
anz_v = v2.slider("Zahl der Folgen", *bounds("anz_v"), key="anz_v", step=C.ANZ_V_SCHRITT)
d_v = v3.selectbox("Mittlere Verweilzeit D (für das Verdikt)", C.D_OPTIONEN, key="d_v", format_func=lambda d: S.d_text(ev.d_wert(d)))
w_v = v4.slider("Stapelzahl W (für das Verdikt)", *bounds("w_v"), key="w_v")
sim = _modell_v(int(n_v), int(anz_v), int(seed))
exakt = _uniform(int(n_v))
st.plotly_chart(build_v_kurven(sim, exakt, int(w_v)), width="stretch", key="chart_v")
zeilen = []
for d, z in sim["d"].items():
    zeilen.append({"D": S.d_text(ev.d_wert(d)), "mittlere LIS": z["lis"], "mittlere LDS": z["lds"],
                   **{f"c_{w}/n": 100 * z["w"][w]["mittel"] for w in range(1, 5)}, f"ganz passend bei W = {int(w_v)}": 100 * z["w"][int(w_v)]["ganz"]})
spalten_cfg = {f"c_{w}/n": st.column_config.NumberColumn(format="%.1f %%") for w in range(1, 5)}
spalten_cfg[f"ganz passend bei W = {int(w_v)}"] = st.column_config.NumberColumn(format="%.1f %%")
spalten_cfg["mittlere LIS"] = st.column_config.NumberColumn(format="%.2f")
spalten_cfg["mittlere LDS"] = st.column_config.NumberColumn(format="%.2f")
st.dataframe(pd.DataFrame(zeilen), hide_index=True, width="stretch", column_config=spalten_cfg)
st.caption(f"Mittel über {sim['anzahl']} Folgen je D (gemeinsame Zufallszahlen für alle D, Zufalls-Seed {sim['seed']}); Fehlerbalken: 95-%-Band des Mittels. "
           f"Letzte Zeile: Modell U; die Rauten im Diagramm sind der exakte Wert aus den Formen (n = {sim['n']}).")
_ausgabe(ev.verdict_v(sim, exakt, d_v, int(w_v)))

st.markdown("---")

# ============================================================================================================================================
# Grenzen und Formeln
# ============================================================================================================================================

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(X.GRENZEN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(X.FORMELN)

sync_query_params({key: st.session_state[key] for key in SETTING_SPECS})

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
