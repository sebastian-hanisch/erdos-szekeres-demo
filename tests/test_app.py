"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: laedt app.py mit den
Standardeinstellungen, klickt jeden Preset-Button und faehrt jeden Slider an seine Grenzen und prueft, dass
kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere
st.plotly_chart-Aufrufe ohne eindeutiges key= koennen zufaellig identischen Inhalt rendern und kollidieren)
und `StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max)."""

import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


def _texte(at):
    return " ".join(e.value for kind in ("success", "info", "warning", "error") for e in getattr(at, kind))


def test_every_preset_runs_and_shows_its_verdicts():
    import esz_constants as C

    for name in C.PRESETS:
        at = _fresh_app()
        at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])
        text = _texte(at)
        assert "Schensted-Form" in text and "Verweilzeit-Modell, n = " in text and "gilt in" in text, name


def test_handfolge_zeigt_die_kapazitaeten_3_5_6_im_verdikt():
    assert "in 1 / 2 / 3 Stapeln passen 3 / 5 / 6 Container" in _texte(_fresh_app())


def test_falsche_eingabe_gibt_eine_warnung_statt_eines_fehlers():
    at = _fresh_app()
    at.text_input(key="folge").set_value("1 2 2").run(timeout=TIMEOUT)
    assert not at.exception
    assert any("Doppelte Zahlen" in w.value for w in at.warning)
    at.text_input(key="folge").set_value("").run(timeout=TIMEOUT)
    assert not at.exception and any("leer" in w.value for w in at.warning)


def test_zufallsfolge_knopf_schreibt_eine_permutation_in_das_feld():
    at = _fresh_app()
    knopf = next(b for b in at.button if "Zufallsfolge ziehen" in b.label)
    knopf.click().run(timeout=TIMEOUT)
    assert not at.exception
    zahlen = sorted(int(x) for x in at.text_input(key="folge").value.split())
    assert zahlen == list(range(1, at.slider(key="n_zufall").value + 1))


def test_worst_case_modell_v_am_regler_maximum():
    """n = 40, 1000 Folgen: die größte Rechnung der App (rund 40 000 Exponentialzahlen) läuft ohne Fehler durch (Timeout statt Zeit-Assertion)."""
    at = _fresh_app()
    at.slider(key="n_v").set_value(40)
    at.slider(key="anz_v").set_value(1000)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert "Verweilzeit-Modell, n = 40" in _texte(at) and "1000 Folgen" in _texte(at)


def test_wachsende_stapel_und_grosse_stapelzahl_laufen_ohne_fehler():
    at = _fresh_app()
    at.radio(key="richtung").set_value("wachsend")
    at.slider(key="w1").set_value(8)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    text = _texte(at)
    assert "in 1 / 2 / 3 / 4 Stapeln passen 3 / 5 / 6 / 6 Container" in text and "Mit 8 Stapeln passen alle 6 Container" in text
