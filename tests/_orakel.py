"""Unabhängige Rechenwege für die Tests (nicht in der App): Brute Force und Definitionen statt der Verfahren der App.

Nichts hier benutzt esz_algorithm: längste Teilfolgen per Doppelschleife, Kapazität per Aufzählung aller Teilmengen bzw. aller Zuordnungen,
Greene-Form per Definition (Vereinigung von k wachsenden Teilfolgen), Hakenformel per Eckenrekursion."""

import math
from functools import lru_cache
from itertools import combinations, product


def lis_dp(a, streng=True) -> int:
    """Längste wachsende Teilfolge per O(n²)-Doppelschleife (streng oder schwach)."""
    n = len(a)
    best = [1] * n
    for i in range(n):
        for j in range(i):
            if (a[j] < a[i]) if streng else (a[j] <= a[i]):
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)


def lds_dp(a, streng=True) -> int:
    n = len(a)
    best = [1] * n
    for i in range(n):
        for j in range(i):
            if (a[j] > a[i]) if streng else (a[j] >= a[i]):
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)


def kap_teilmengen(a, W, fallend=True) -> int:
    """Größte Teilmenge, die sich in W monotone Teilfolgen zerlegen lässt: bei fallenden Stapeln genau die mit längster WACHSENDER Teilfolge <= W
    (Mirsky: Zerlegung in W fallende Folgen gibt es genau dann, wenn es keine wachsende Folge der Länge W + 1 gibt)."""
    n = len(a)
    for k in range(n, 0, -1):
        for idx in combinations(range(n), k):
            teil = [a[i] for i in idx]
            if (lis_dp(teil) if fallend else lds_dp(teil)) <= W:
                return k
    return 0


def kap_zuordnung(a, W, fallend=True) -> int:
    """Jeden Container einem der W Stapel oder „draußen“ zuordnen (alle (W+1)^n Zuordnungen); gültig, wenn jeder Stapel in Ankunftsreihenfolge
    fällt (wächst)."""
    best = 0
    for zu in product(range(W + 1), repeat=len(a)):
        spitzen = [None] * W
        ok = True
        drin = 0
        for x, s in zip(a, zu):
            if s == W:
                continue
            if spitzen[s] is not None and not ((x < spitzen[s]) if fallend else (x > spitzen[s])):
                ok = False
                break
            spitzen[s] = x
            drin += 1
        if ok:
            best = max(best, drin)
    return best


def kap_hoehe_zuordnung(a, W, H) -> int:
    """Wie kap_zuordnung (fallende Stapel), zusätzlich höchstens H Container je Stapel."""
    best = 0
    for zu in product(range(W + 1), repeat=len(a)):
        spitzen = [None] * W
        hoehen = [0] * W
        ok = True
        drin = 0
        for x, s in zip(a, zu):
            if s == W:
                continue
            if (spitzen[s] is not None and not x < spitzen[s]) or hoehen[s] + 1 > H:
                ok = False
                break
            spitzen[s] = x
            hoehen[s] += 1
            drin += 1
        if ok:
            best = max(best, drin)
    return best


def greene_zeilen(a) -> tuple:
    """Form nach der Definition von Greene-Kleitman: λ1 + … + λk = größte Vereinigung von k wachsenden Teilfolgen (Aufzählung aller Teilmengen)."""
    n = len(a)
    summen = []
    for k in range(1, n + 1):
        best = 0
        for m in range(n, 0, -1):
            gefunden = False
            for idx in combinations(range(n), m):
                if lds_dp([a[i] for i in idx]) <= k:      # Zerlegung in k wachsende Folgen <=> keine fallende der Länge k + 1
                    gefunden = True
                    break
            if gefunden:
                best = m
                break
        summen.append(best)
        if best == n:
            break
    return tuple(s - v for s, v in zip(summen, [0] + summen))


@lru_cache(maxsize=None)
def f_ecken(lam) -> int:
    """Zahl der Standard-Tableaux per Eckenrekursion: f(λ) = Summe von f(λ ohne Ecke)."""
    if sum(lam) == 0:
        return 1
    gesamt = 0
    for i in range(len(lam)):
        if lam[i] > 0 and (i + 1 == len(lam) or lam[i] > lam[i + 1]):
            neu = list(lam)
            neu[i] -= 1
            gesamt += f_ecken(tuple(x for x in neu if x > 0))
    return gesamt


def konj(lam) -> tuple:
    return tuple(sum(1 for x in lam if x > j) for j in range(lam[0])) if lam else ()


def paare_dp(a) -> list:
    """(wachsend endend, fallend endend) je Position, Definition per Doppelschleife."""
    n = len(a)
    inc, dec = [1] * n, [1] * n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i]:
                inc[i] = max(inc[i], inc[j] + 1)
            if a[j] > a[i]:
                dec[i] = max(dec[i], dec[j] + 1)
    return list(zip(inc, dec))


def fakultaet(n) -> int:
    return math.factorial(n)
