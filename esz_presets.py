"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio).

Jeder Regler der App steht in SETTING_SPECS (Schlüssel = Widget-Schlüssel = Schlüssel im Preset). Der Zufalls-Seed steht in der Seitenleiste, die
experimentbezogenen Regler stehen im Hauptbereich bei ihrem Experiment (DEMO-PLAYBOOK §2). Ein Preset legt alle Regler fest."""

import random
from dataclasses import dataclass

import streamlit as st

import esz_constants as C
from esz_scenario import folge_text, zufallsfolge


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    kind: str                       # "int", "text" oder "choice"
    default: object
    lo: int | None = None
    hi: int | None = None
    optionen: tuple | None = None


S = C.STANDARD
SETTING_SPECS = {
    "seed": SettingSpec("seed", "int", S["seed"], 0, C.SEED_MAX),
    "folge": SettingSpec("folge", "text", S["folge"]),
    "w1": SettingSpec("w1", "int", S["w1"], C.W1_MIN, C.W1_MAX),
    "richtung": SettingSpec("richtung", "choice", S["richtung"], optionen=C.RICHTUNGEN),
    "n_zufall": SettingSpec("nz", "int", S["n_zufall"], C.N_ZUFALL_MIN, C.N_ZUFALL_MAX),
    "a": SettingSpec("a", "int", S["a"], C.AB_MIN, C.AB_MAX),
    "b": SettingSpec("b", "int", S["b"], C.AB_MIN, C.AB_MAX),
    "wort": SettingSpec("wort", "text", S["wort"]),
    "n_knapp": SettingSpec("nk", "int", S["n_knapp"], C.N_KNAPP_MIN, C.N_KNAPP_MAX),
    "n_g": SettingSpec("ng", "int", S["n_g"], C.N_G_MIN, C.N_G_MAX),
    "w_g": SettingSpec("wg", "int", S["w_g"], C.W_G_MIN, C.W_G_MAX),
    "n_h": SettingSpec("nh", "int", S["n_h"], C.N_H_MIN, C.N_H_MAX),
    "w_h": SettingSpec("wh", "choice", S["w_h"], optionen=C.W_H_OPTIONEN),
    "h_h": SettingSpec("hh", "int", S["h_h"], C.H_H_MIN, C.H_H_MAX),
    "n_v": SettingSpec("nv", "int", S["n_v"], C.N_V_MIN, C.N_V_MAX),
    "anz_v": SettingSpec("av", "int", S["anz_v"], C.ANZ_V_MIN, C.ANZ_V_MAX),
    "d_v": SettingSpec("dv", "choice", S["d_v"], optionen=C.D_OPTIONEN),
    "w_v": SettingSpec("wv", "int", S["w_v"], C.W_V_MIN, C.W_V_MAX),
}
PRESET_KEYS = {k: k for k in SETTING_SPECS}   # Schlüssel im Preset = Widget-Schlüssel
TEXT_MAX = 200


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def _lies(spec, roh):
    """Wert aus der Adresszeile lesen und begrenzen; wirft ValueError bei Unlesbarem."""
    if spec.kind == "int":
        return min(spec.hi, max(spec.lo, int(roh)))
    if spec.kind == "text":
        return str(roh)[:TEXT_MAX]
    for option in spec.optionen:
        if str(option) == str(roh):
            return option
    raise ValueError(roh)


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                st.session_state[state_key] = _lies(spec, qp[spec.url_param])
            except (ValueError, TypeError):
                continue
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key in SETTING_SPECS:
        st.session_state[key] = C.PRESETS[name][key]


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS mit dem Session State (tests/test_layout.py prüft für jeden Regler, dass seine
    Änderung die Markierung aufhebt)."""
    for name, preset in C.PRESETS.items():
        if all(st.session_state.get(key, spec.default) == preset[key] for key, spec in SETTING_SPECS.items()):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden (setzt alle Regler der Seite):")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["seed"] = random.randint(0, C.SEED_MAX)


def zufallsfolge_ziehen():
    """Schreibt eine gleichverteilte Folge (Länge n_zufall, Zufalls-Seed `seed`) in das Feld der Eingabe."""
    st.session_state["folge"] = folge_text(zufallsfolge(int(st.session_state["n_zufall"]), int(st.session_state["seed"])))
