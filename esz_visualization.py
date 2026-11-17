"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import esz_constants as C
import esz_scenario as S


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _zelle(fig, x, y, text, farbe, breite=0.42, hoehe=0.45, schrift=12, textfarbe="white"):
    """Ein Feld (Container oder Zelle der Form) als Rechteck mit Beschriftung; Beschriftungen als Annotation (kein Text-Trace)."""
    fig.add_shape(type="rect", x0=x - breite, x1=x + breite, y0=y - hoehe, y1=y + hoehe, fillcolor=farbe, line=dict(color="rgba(255,255,255,0.9)", width=1))
    fig.add_annotation(x=x, y=y, text=str(text), showarrow=False, font=dict(size=schrift, color=textfarbe))


# --- Experiment 1 ---------------------------------------------------------------------------------------------------------------------------

def build_stapel(a):
    """Die W Stapel mit der Belegung aus dem Fluss (unten liegt, was zuerst ankam) und die Container draußen. Beschriftung: Rang."""
    spalten = list(a.stapel) + [list(a.draussen)]
    hoehe_max = max(1, max(len(s) for s in spalten))
    fig = go.Figure()
    xs = []
    for k, inhalt in enumerate(spalten):
        x = k if k < a.W else a.W + 0.35
        xs.append(x)
        farbe = C.COLOR_STAPEL[k % len(C.COLOR_STAPEL)] if k < a.W else C.COLOR_DRAUSSEN
        for h, rang in enumerate(inhalt):
            _zelle(fig, x, h + 1, rang, farbe, schrift=12 if hoehe_max <= 12 else 9, textfarbe="white" if k < a.W else "black")
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(tickmode="array", tickvals=xs, ticktext=[f"Stapel {k + 1}" for k in range(a.W)] + ["draußen"], range=[-0.6, a.W + 0.95], showgrid=False, zeroline=False)
    fig.update_yaxes(range=[0.3, hoehe_max + 0.7], showticklabels=False, showgrid=False, zeroline=False)
    return _base(fig, height=int(min(560, max(240, 70 + 26 * hoehe_max))))


def build_form(a):
    """Das Schensted-Tableau: Zellen, die zur Kapazität zählen (erste W Spalten bei fallenden Stapeln, erste W Zeilen bei wachsenden), sind farbig."""
    fig = go.Figure()
    for i, zeile in enumerate(a.tableau):
        for j, wert in enumerate(zeile):
            zaehlt = (j < a.W) if a.fallend else (i < a.W)
            _zelle(fig, j + 1, i + 1, wert, C.COLOR_SPALTEN if zaehlt else C.COLOR_DRAUSSEN, textfarbe="white" if zaehlt else "black")
    fig.add_trace(go.Scatter(x=[1], y=[1], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    breite = max(len(z) for z in a.tableau) if a.tableau else 1
    fig.update_xaxes(range=[0.4, breite + 0.6], tickmode="array", tickvals=list(range(1, breite + 1)), ticktext=[f"Sp. {j}" for j in range(1, breite + 1)],
                     showgrid=False, zeroline=False)
    fig.update_yaxes(range=[len(a.tableau) + 0.6, 0.4], tickmode="array", tickvals=list(range(1, len(a.tableau) + 1)),
                     ticktext=[f"Z. {i}" for i in range(1, len(a.tableau) + 1)], showgrid=False, zeroline=False)
    return _base(fig, height=int(min(420, max(200, 80 + 34 * len(a.tableau)))))


# --- Experiment 2 ---------------------------------------------------------------------------------------------------------------------------

def build_gitter(a, b, paare, folge, titel):
    """Beweisgitter: je Container ein Punkt (längste wachsende Teilfolge bis hier, längste fallende bis hier). Punkte im a × b-Gitter sind farbig,
    Punkte außerhalb rot. Beschriftung: Rang des Containers."""
    fig = go.Figure()
    innen = [(p, r) for p, r in zip(paare, folge) if p[0] <= a and p[1] <= b]
    aussen = [(p, r) for p, r in zip(paare, folge) if not (p[0] <= a and p[1] <= b)]
    for liste, farbe, name in ((innen, C.COLOR_SPALTEN, "im Gitter"), (aussen, C.COLOR_GITTER_AUSSEN, "außerhalb")):
        if liste:
            fig.add_trace(go.Scatter(
                x=[p[0] for p, _ in liste], y=[p[1] for p, _ in liste], mode="markers+text", text=[str(r) for _, r in liste], textposition="middle center",
                textfont=dict(color="white", size=11), marker=dict(size=26, color=farbe), name=name,
                hovertemplate="Rang %{text}: wachsend %{x}, fallend %{y}<extra></extra>"))
    fig.add_shape(type="rect", x0=0.5, x1=a + 0.5, y0=0.5, y1=b + 0.5, line=dict(color="rgba(128,128,128,0.8)", width=2, dash="dot"))
    xmax = max([a] + [p[0] for p in paare])
    ymax = max([b] + [p[1] for p in paare])
    fig.update_xaxes(title_text="längste wachsende Teilfolge, die hier endet", range=[0.4, xmax + 0.6], dtick=1, showgrid=True)
    fig.update_yaxes(title_text="längste fallende, die hier endet", range=[0.4, ymax + 0.6], dtick=1, showgrid=True)
    fig.update_layout(title=dict(text=titel, font=dict(size=13)))
    _base(fig, height=400)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


# --- Experiment 3 ---------------------------------------------------------------------------------------------------------------------------

def build_knapp(n, verteilung, e_produkt):
    """Verteilung von LIS·LDS über alle n! Folgen (exakt aus den Formen); Marken: Garantie n und Mittel."""
    fak = sum(verteilung.values())
    xs = list(verteilung)
    fig = go.Figure(go.Bar(x=xs, y=[100 * v / fak for v in verteilung.values()], marker_color=C.COLOR_LINE, name="Anteil der Folgen",
                           hovertemplate="LIS·LDS = %{x}: %{y:.3f} %<extra></extra>"))
    fig.add_vline(x=n, line=dict(color=C.COLOR_GITTER_AUSSEN, width=2, dash="dash"), annotation_text="Garantie n", annotation_position="top left")
    fig.add_vline(x=float(e_produkt), line=dict(color=C.COLOR_SPALTEN, width=2), annotation_text="Mittel", annotation_position="top right")
    fig.update_xaxes(title_text="LIS · LDS")
    fig.update_yaxes(title_text="Anteil der Folgen (%)")
    return _base(fig)


# --- Experiment 4 ---------------------------------------------------------------------------------------------------------------------------

def build_garantie_verteilung(g):
    fak = g.folgen
    xs = list(g.verteilung)
    fig = go.Figure(go.Bar(x=xs, y=[100 * v / fak for v in g.verteilung.values()], marker_color=C.COLOR_SPALTEN, name="Anteil der Folgen",
                           hovertemplate="c_W = %{x}: %{y:.2f} %<extra></extra>"))
    fig.update_xaxes(title_text=f"Kapazität c_{g.W} (Container, die in {g.W} Stapel passen)", dtick=1)
    fig.update_yaxes(title_text="Anteil der Folgen (%)")
    return _base(fig)


def build_garantie_je_lis(g):
    """Je LIS-Wert: kleinste Kapazität über alle Folgen gegen die Garantie min(n, W·n/LIS)."""
    lis_werte = list(g.je_lis)
    kleinste = [g.je_lis[k][1] for k in lis_werte]
    garantie = [float(g.je_lis[k][2]) for k in lis_werte]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=lis_werte, y=kleinste, marker_color=C.COLOR_SPALTEN, name="kleinstes c_W über alle Folgen mit diesem LIS",
                         hovertemplate="LIS = %{x}: kleinstes c_W = %{y}<extra></extra>"))
    fig.add_trace(go.Scatter(x=lis_werte, y=garantie, mode="lines+markers", line=dict(color=C.COLOR_GITTER_AUSSEN, width=3), name="Garantie min(n, W·n/LIS)",
                             hovertemplate="LIS = %{x}: Garantie %{y:.2f}<extra></extra>"))
    fig.update_xaxes(title_text="LIS (längste wachsende Teilfolge)", dtick=1)
    fig.update_yaxes(title_text="Container")
    return _base(fig)


# --- Experiment 5 ---------------------------------------------------------------------------------------------------------------------------

def build_v_kurven(sim, exakt, w_markiert):
    """Mittleres c_W/n über die mittlere Verweilzeit D, eine Kurve je Stapelzahl W (Fehlerbalken: 95-%-Band des Mittels). Rauten bei ∞: Modell U exakt."""
    d_texte = list(sim["d"])
    labels = [S.d_text(S.D_UNENDLICH if d == "inf" else float(d)) for d in d_texte]
    fig = go.Figure()
    w_max = max(sim["d"][d_texte[0]]["w"])
    for w in range(1, w_max + 1):
        y = [100 * sim["d"][d]["w"][w]["mittel"] for d in d_texte]
        err = [100 * 1.96 * sim["d"][d]["w"][w]["se"] for d in d_texte]
        farbe = C.COLOR_STAPEL[(w - 1) % len(C.COLOR_STAPEL)]
        fig.add_trace(go.Scatter(x=labels, y=y, mode="lines+markers", name=f"W = {w}", line=dict(color=farbe, width=4 if w == w_markiert else 2),
                                 error_y=dict(type="data", array=err, visible=True, thickness=1),
                                 hovertemplate="D = %{x}: %{y:.1f} %<extra>W = " + str(w) + "</extra>"))
        fig.add_trace(go.Scatter(x=[labels[-1]], y=[100 * exakt[w]["mittel"]], mode="markers", marker=dict(symbol="diamond-open", size=11, color=farbe, line=dict(width=2)),
                                 showlegend=False, hovertemplate="exakt (uniform): %{y:.1f} %<extra>W = " + str(w) + "</extra>"))
    fig.update_xaxes(title_text="mittlere Verweilzeit D (in Ankunftsabständen); Rauten: Modell U exakt", type="category", categoryorder="array", categoryarray=labels)
    fig.update_yaxes(title_text="mittlerer Anteil c_W/n der Container, die passen (%)", range=[0, 102])
    return _base(fig, height=420)
