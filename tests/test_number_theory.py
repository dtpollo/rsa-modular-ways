import random

import pytest

from src.number_theory import (
    extended_gcd, gcd, is_perfect_square, is_prime, isqrt,
    mod_inverse, mod_pow, next_prime, random_prime,
)


# --- GCD ---------------------------------------------------------------

@pytest.mark.parametrize("a, b, expected", [
    (48, 18, 6), (18, 48, 6), (17, 3120, 1), (21, 35, 7),
    (7, 0, 7), (0, 7, 7), (-48, 18, 6),
])
def test_gcd(a, b, expected):
    assert gcd(a, b) == expected


def test_extended_gcd_bezout_identity():
    for a, b in [(17, 3120), (48, 18), (240, 46), (1, 1)]:
        g, s, t = extended_gcd(a, b)
        assert g == gcd(a, b)
        assert a * s + b * t == g


# --- Modular inverse ---------------------------------------------------

@pytest.mark.parametrize("a, m, expected", [
    (17, 3120, 2753),   # the lab key
    (3, 11, 4),
    (7, 20, 3),
])
def test_mod_inverse(a, m, expected):
    assert mod_inverse(a, m) == expected
    assert a * expected % m == 1


def test_mod_inverse_does_not_exist():
    with pytest.raises(ValueError):
        mod_inverse(6, 9)               # gcd(6, 9) = 3


# --- Integer square root -----------------------------------------------

@pytest.mark.parametrize("n, expected", [
    (0, 0), (1, 1), (2, 1), (3, 1), (4, 2), (50, 7), (3233, 56), (3249, 57),
])
def test_isqrt(n, expected):
    assert isqrt(n) == expected


def test_isqrt_large_numbers():
    rng = random.Random(1)
    for _ in range(200):
        n = rng.getrandbits(200)
        r = isqrt(n)
        assert r * r <= n < (r + 1) ** 2


def test_isqrt_negative():
    with pytest.raises(ValueError):
        isqrt(-1)


def test_is_perfect_square():
    squares = {k * k for k in range(200)}
    for n in range(200 * 200):
        assert is_perfect_square(n) == (n in squares)


# --- Modular exponentiation and primes ---------------------------------

def test_mod_pow_matches_builtin():
    rng = random.Random(2)
    for _ in range(200):
        base, exp, mod = rng.getrandbits(64), rng.getrandbits(32), rng.getrandbits(48) + 1
        assert mod_pow(base, exp, mod) == pow(base, exp, mod)


def test_is_prime_matches_sieve():
    limit = 10_000
    sieve = [True] * limit
    sieve[0] = sieve[1] = False
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(sieve[i * i::i])
    for n in range(limit):
        assert is_prime(n) == sieve[n]


def test_is_prime_carmichael_numbers():
    for n in (561, 1105, 1729, 2465, 2821, 6601):
        assert not is_prime(n)


def test_next_prime():
    assert next_prime(1) == 2
    assert next_prime(13) == 17
    assert next_prime(60) == 61


@pytest.mark.parametrize("bits", [3, 8, 16, 24, 32])
def test_random_prime_has_exact_size(bits):
    rng = random.Random(bits)
    p = random_prime(bits, rng)
    assert is_prime(p)
    assert p.bit_length() == bits
