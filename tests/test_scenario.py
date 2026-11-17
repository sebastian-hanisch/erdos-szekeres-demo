"""Szenario: Zufall (ganzzahliger SplitMix64, Kopie der geprüften Vorlage), Blockfolgen, Verweilzeit-Modell, Eingabe-Prüfung."""

import hashlib
from pathlib import Path

import pytest

import esz_scenario as S
from esz_rng import SplitMix64

ROOT = Path(__file__).resolve().parent.parent
VORLAGE = ROOT.parent / "sebastianhanisch-website" / "tools" / "templates" / "rng_splitmix64_exact.py"
SHA256_RNG = "d69b2b2fd67c1234cc0d79249676a662a2189d02803eea7d2edfb04b7a505a3f"


def _lf(pfad: Path) -> bytes:
    return pfad.read_bytes().replace(b"\r\n", b"\n")


def test_rng_ist_unveraendert_die_geprueft_vorlage():
    """`esz_rng.py` ist eine wörtliche Kopie der Vorlage (test_copies): Hash fest, und gleich der Vorlage, wo sie vorliegt (nicht in der CI)."""
    assert hashlib.sha256(_lf(ROOT / "esz_rng.py")).hexdigest() == SHA256_RNG
    if VORLAGE.exists():
        assert _lf(VORLAGE) == _lf(ROOT / "esz_rng.py")


def test_splitmix64_bekannte_werte():
    """SplitMix64 mit Zufalls-Seed 0: die ersten drei Ausgaben der Referenzimplementierung (Vigna), von Hand als Hexwerte notiert."""
    r = SplitMix64(0)
    assert [r.next_u64() for _ in range(3)] == [0xE220A8397B1DCDAF, 0x6E789E6AA1B965F4, 0x06C45D188009454F]


def test_below_ist_im_bereich_und_shuffle_ist_permutation():
    r = SplitMix64(5)
    assert all(0 <= r.below(7) < 7 for _ in range(200))
    liste = list(range(10))
    r.shuffle(liste)
    assert sorted(liste) == list(range(10))


def test_zufallsfolge_ist_reproduzierbar_und_feste_werte():
    assert S.zufallsfolge(5, 49) == (2, 5, 1, 4, 3)
    assert S.zufallsfolge(20, 2024) == tuple(int(x) for x in "3 19 1 14 20 7 8 4 18 6 13 15 16 17 5 11 12 10 9 2".split())


def test_zufallsfolge_ist_gleichverteilt_im_band():
    """Erste Position der Zufallsfolge n = 4 über 2400 Zufalls-Seeds: jeder Rang etwa 600 mal (Standardabweichung etwa 21)."""
    zaehler = [0] * 5
    for s in range(2400):
        zaehler[S.zufallsfolge(4, s)[0]] += 1
    assert all(abs(z - 600) < 100 for z in zaehler[1:])


@pytest.mark.parametrize("a,b", [(1, 1), (2, 3), (3, 3), (4, 2)])
def test_blockfolge_ist_permutation(a, b):
    assert sorted(S.blockfolge(a, b)) == list(range(1, a * b + 1))


def test_ziehungen_sind_praefix_der_laengeren_reihe():
    assert S.ziehungen_v(6, 4, 9) == S.ziehungen_v(6, 9, 9)[:4]


def test_exponentialziehungen_haben_mittel_nahe_1():
    z = S.ziehungen_v(10, 400, 3)
    mittel = sum(sum(e) for e in z) / 4000
    assert abs(mittel - 1.0) < 0.06          # Standardfehler 0,016


def test_d_text():
    assert S.d_text(0.5) == "0,5" and S.d_text(16.0) == "16" and S.d_text(S.D_UNENDLICH) == "∞ (uniform)"
