"""Eigenschaftstests (metamorph, ORACLE-PLAYBOOK §5.2): Aussagen, die für Kapazität, LIS und LDS gelten müssen, ohne dass man das Ergebnis kennt.

Je Eigenschaft 25 bis 40 Zufallsinstanzen mit festem Zufalls-Seed (aus dem ganzzahligen SplitMix64), dazu Randfälle."""

import esz_algorithm as A
import esz_scenario as S

SEEDS = range(40)


def _folgen(n_von=3, n_bis=14, anzahl=40):
    for s in range(anzahl):
        n = n_von + s % (n_bis - n_von + 1)
        yield S.zufallsfolge(n, 1000 + s)


def test_umbenennen_der_raenge_ohne_ordnungsaenderung_aendert_nichts():
    """Werte 3, 8, 20 statt 1, 2, 3 (gleiche Ordnung): gleiche Form, gleiche Kapazität."""
    for p in _folgen():
        q = tuple(10 * x + 3 for x in p)
        assert A.standardisiere(q) == p
        assert A.form(q) == A.form(p)
        for w in (1, 2, 3):
            assert A.kapazitaet_fluss(q, w)[0] == A.kapazitaet_fluss(p, w)[0]


def test_spiegeln_der_folge_vertauscht_fallende_und_wachsende_stapel():
    """Rückwärts gelesen wird eine fallende Teilfolge zur wachsenden: Kapazität der Spiegelfolge bei wachsenden Stapeln = Kapazität der Folge bei fallenden."""
    for p in _folgen():
        r = tuple(reversed(p))
        for w in (1, 2, 3, 4):
            assert A.kapazitaet_fluss(r, w, fallend=False)[0] == A.kapazitaet_fluss(p, w, fallend=True)[0]


def test_komplement_vertauscht_lis_und_lds():
    """Rang ↦ n + 1 − Rang kehrt die Ordnung um: LIS und LDS tauschen, die Form wird transponiert."""
    for p in _folgen():
        n = len(p)
        q = tuple(n + 1 - x for x in p)
        assert (A.lis(q), A.lds(q)) == (A.lds(p), A.lis(p))
        assert A.form(q) == A.konjugiert(A.form(p))


def test_inverse_folge_hat_dieselbe_form():
    for p in _folgen(3, 12):
        inv = [0] * len(p)
        for i, x in enumerate(p):
            inv[x - 1] = i + 1
        assert A.form(tuple(inv)) == A.form(p)


def test_kapazitaet_waechst_mit_w_zuwachs_faellt_und_ist_n_ab_lis():
    for p in _folgen():
        n = len(p)
        c = [0] + [A.kapazitaet_fluss(p, w)[0] for w in range(1, n + 1)]
        zuwachs = [c[i + 1] - c[i] for i in range(n)]
        assert all(zuwachs[i] >= zuwachs[i + 1] for i in range(n - 1)), p     # Zuwachs je weiterem Stapel nie wachsend
        assert all(zuwachs[i] >= 0 for i in range(n))
        li = A.lis(p)
        assert c[li] == n and (li == 1 or c[li - 1] < n)                       # c_W = n genau ab W = LIS


def test_kapazitaet_hoechstens_n_und_hoechstens_summe_der_hoehen():
    for p in _folgen(3, 10, 30):
        n = len(p)
        for w in (1, 2, 3):
            assert A.kapazitaet_fluss(p, w)[0] <= n
            for h in (1, 2):
                assert A.kapazitaet_hoehe(p, w, h) <= w * h


def test_anhaengen_eines_containers_erhoeht_die_kapazitaet_um_hoechstens_1():
    """Ein neuer Container (beliebiger Rang, die übrigen rücken nach) ändert c_W um 0 oder 1, nie darüber, nie nach unten."""
    for p in _folgen(2, 12, 40):
        n = len(p)
        for r in (1, (n + 1) // 2, n + 1):
            q = tuple(x + 1 if x >= r else x for x in p) + (r,)
            for w in (1, 2, 3):
                d = A.kapazitaet_fluss(q, w)[0] - A.kapazitaet_fluss(p, w)[0]
                assert d in (0, 1), (p, r, w)


def test_es_produkt_bei_jeder_zufallsfolge_mindestens_n():
    for p in _folgen(1, 40, 40):
        assert A.lis(p) * A.lds(p) >= len(p)


def test_verschieben_aller_raenge_um_eine_konstante_aendert_nichts():
    for p in _folgen():
        q = tuple(x + 100 for x in p)
        assert A.kapazitaet_fluss(q, 2)[0] == A.kapazitaet_fluss(p, 2)[0]
        assert A.form(q) == A.form(p)


def test_garantie_gilt_bei_jeder_zufallsfolge():
    for p in _folgen(2, 25, 40):
        n, li = len(p), A.lis(p)
        for w in (1, 2, 3, 4):
            assert A.kapazitaet_fluss(p, w)[0] * li >= min(n * li, w * n)


def test_zufallsfolge_ist_eine_permutation_und_haengt_nur_am_zufalls_seed():
    for s in SEEDS:
        f = S.zufallsfolge(15, s)
        assert sorted(f) == list(range(1, 16))
        assert f == S.zufallsfolge(15, s)
    assert S.zufallsfolge(15, 1) != S.zufallsfolge(15, 2)
