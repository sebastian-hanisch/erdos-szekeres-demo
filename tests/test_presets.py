"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Texte der erzeugten Folgen, Verdikt-Zeile je Preset."""

import esz_algorithm as A
import esz_constants as C
import esz_evaluation as ev
import esz_presets as P
import esz_scenario as S


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.SETTING_SPECS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_valid_for_every_setting():
    for name, preset in C.PRESETS.items():
        for key, spec in P.SETTING_SPECS.items():
            wert = preset[key]
            if spec.kind == "int":
                assert spec.lo <= wert <= spec.hi, (name, key)
            elif spec.kind == "choice":
                assert wert in spec.optionen, (name, key)
            else:
                assert isinstance(wert, str) and len(wert) <= P.TEXT_MAX
        assert S.parse_folge(preset["folge"])[1] is None, name
        assert S.parse_wort(preset["wort"])[1] is None, name


def test_default_preset_equals_the_default_settings():
    erster = next(iter(C.PRESETS.values()))
    assert erster == {key: spec.default for key, spec in P.SETTING_SPECS.items()} == C.STANDARD


def test_presets_are_pairwise_different():
    werte = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(werte)) == len(werte)


def test_setting_specs_and_preset_keys_agree():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS) == set(C.STANDARD)


def test_folgen_der_presets_stammen_aus_dem_ganzzahligen_zufall():
    assert C.FOLGE_ZUFALL_20 == S.folge_text(S.zufallsfolge(20, C.DEFAULT_SEED))
    expo = S.ziehungen_v(20, 1, C.DEFAULT_SEED)[0]
    assert C.FOLGE_FAST_SORTIERT == S.folge_text(S.folge_v(expo, 1.0))
    assert S.zufallsfolge(5, C.SEED_ES_2X2) == (2, 5, 1, 4, 3)


def test_fast_sortiert_hat_lange_wachsende_teilfolge():
    p = S.parse_folge(C.FOLGE_FAST_SORTIERT)[0]
    assert A.lis(p) == 18 and A.lds(p) == 3


def test_verdikt_je_preset_meldet_nur_was_gilt():
    """Je Preset die erwartete Verdikt-Zeile (DEMO-PLAYBOOK §11a Punkt 7): Identität und Umkehrfolge werden nicht als „Garantie scharf“ gelesen."""
    erwartet = {
        "Handfolge n = 6 (Voreinstellung)": ["in 1 / 2 / 3 Stapeln passen 3 / 5 / 6 Container", "draußen bleibt Rang 1", "dieselbe Zahl (5)"],
        "Blockfolge 3 × 3": ["Form (3, 3, 3)", "in 1 / 2 / 3 Stapeln passen 3 / 6 / 9 Container", "passen alle 9 Container"],
        "Falle: Blockfolge 4 5 6 1 2 3": ["in 1 / 2 / 3 Stapeln passen 2 / 4 / 6 Container", "ergäbe 6 statt 4"],
        "Identität (alles wächst)": ["Form (8)", "in 1 / 2 / 3 / 4 Stapeln passen 1 / 2 / 3 / 4 Container", "ergäbe 8 statt 2"],
        "ES 2 × 2": ["Form (2, 2, 1)", "in 1 / 2 Stapeln passen 3 / 5 Container", "passen alle 5 Container", "ergäbe 4 statt 5"],
    }
    for name, teile in erwartet.items():
        p = C.PRESETS[name]
        folge = S.parse_folge(p["folge"])[0]
        _art, text = ev.verdict_kapazitaet(ev.analyse_kapazitaet(folge, p["w1"], p["richtung"]))
        for t in teile:
            assert t in text, (name, t, text)
        assert "scharf" not in text and "Garantie" not in text


def test_verdikt_gleichstaende_preset():
    art, text = ev.verdict_wort(S.parse_wort(C.PRESETS["Gleichstände (2, 2, 2, 2)"]["wort"])[0])
    assert "streng wachsend 1, schwach fallend 4, Produkt 4 ≥ 4" in text and "streng × streng: 1 < 4 (verletzt)" in text and art == "warning"


def test_verdikt_es_preset_gitter_2x2_zeigt_punkt_ausserhalb():
    p = C.PRESETS["ES 2 × 2"]
    e = ev.analyse_es(p["a"], p["b"], p["seed"])
    assert e.beispiel == (2, 5, 1, 4, 3) and e.aussen == ((2, 3),)
