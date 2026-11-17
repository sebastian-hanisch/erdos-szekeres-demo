"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): n = 1, n = 2, leere Eingabe, W = 0, W > n, Höhe 0 und 1, a·b = 1,
Grenzen inklusive, Eingaben über der Reglergrenze, Gleichstände."""

import pytest

import esz_algorithm as A
import esz_constants as C
import esz_scenario as S


def test_n_gleich_1_und_2():
    assert A.kapazitaet_fluss((1,), 1) == (1, [[0]])
    assert A.form((1,)) == (1,) and A.lis((1,)) == A.lds((1,)) == 1
    assert A.kapazitaet_fluss((1, 2), 1)[0] == 1 and A.kapazitaet_fluss((2, 1), 1)[0] == 2     # n = 2: aufsteigend braucht zwei Stapel
    assert A.kapazitaet_fluss((1, 2), 2)[0] == 2


def test_leere_folge_und_w_null():
    assert A.kapazitaet_fluss((), 3) == (0, [[], [], []])
    assert A.kapazitaet_fluss((3, 1, 2), 0) == (0, [])
    assert A.kapazitaet_form((2, 1), 0) == 0 and A.lis(()) == 0 and A.form(()) == ()


def test_w_groesser_als_n_ist_n():
    p = (2, 3, 1)
    c, st = A.kapazitaet_fluss(p, 9)
    assert c == 3 and len(st) == 9


def test_hoehe_null_und_eins():
    assert A.kapazitaet_hoehe((3, 2, 1), 2, 0) == 0
    assert A.kapazitaet_hoehe((3, 2, 1), 2, 1) == 2          # H = 1: jeder Stapel nimmt einen Container, also W
    assert A.kapazitaet_hoehe((3, 2, 1), 5, 1) == 3          # genug Stapel: alle drei einzeln


def test_a_mal_b_gleich_1():
    assert A.scharf_anzahl(1, 1) == 1 and A.gleichheitsfaelle(1) == 1
    assert S.blockfolge(1, 1) == (1,)


@pytest.mark.parametrize("text", ["", "   ", "1 2 x", "1 2 2 3", "1.5 2"])
def test_ungueltige_eingaben_werden_abgewiesen(text):
    folge, fehler = S.parse_folge(text)
    assert folge is None and fehler


def test_eingabe_ueber_der_reglergrenze_wird_abgewiesen():
    folge, fehler = S.parse_folge(" ".join(str(i) for i in range(1, 22)))
    assert folge is None and "Höchstens 20" in fehler


def test_eingabe_wird_auf_raenge_abgebildet():
    assert S.parse_folge("10, 30; 20") == ((1, 3, 2), None)
    assert S.parse_wort("2 2 2 2") == ((2, 2, 2, 2), None)
    assert S.parse_wort("")[0] is None


def test_grenzen_sind_inklusive():
    """Genau N_FOLGE_MAX Container sind erlaubt, einer mehr nicht; ebenso WORT_MAX."""
    assert S.parse_folge(" ".join(str(i) for i in range(1, C.N_FOLGE_MAX + 1)))[1] is None
    assert S.parse_folge(" ".join(str(i) for i in range(1, C.N_FOLGE_MAX + 2)))[0] is None
    assert S.parse_wort(" ".join(["1"] * C.WORT_MAX))[1] is None
    assert S.parse_wort(" ".join(["1"] * (C.WORT_MAX + 1)))[0] is None


def test_gleichstand_im_permutationsmodus_wird_abgewiesen_und_im_wortmodus_angenommen():
    assert S.parse_folge("2 2 2 2")[0] is None
    assert S.parse_wort("2 2 2 2")[0] == (2, 2, 2, 2)


def test_alle_raenge_gleich_nur_im_wortmodus():
    p = A.paarungen((7,) * 5)
    assert p["streng_streng"] == 1 and p["streng_schwach"] == 5


def test_zwei_container_beide_reihenfolgen():
    """n = 2: aufsteigend (1, 2) braucht zwei Stapel, absteigend (2, 1) einen."""
    assert [A.kapazitaet_fluss((1, 2), w)[0] for w in (1, 2)] == [1, 2]
    assert [A.kapazitaet_fluss((2, 1), w)[0] for w in (1, 2)] == [2, 2]
