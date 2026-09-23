"""Textbook RSA: key generation, encryption, decryption and private key recovery."""

import random
from dataclasses import dataclass

from .number_theory import gcd, mod_inverse, mod_pow, random_prime

# Common public exponents, tried in order. Small moduli need a small e (e < phi).
PUBLIC_EXPONENTS = (65537, 257, 17, 5, 3)


@dataclass(frozen=True)
class RSAKey:
    n: int
    e: int
    d: int
    p: int
    q: int

    @property
    def phi(self):
        return (self.p - 1) * (self.q - 1)


def choose_public_exponent(phi):
    """First exponent from PUBLIC_EXPONENTS with 1 < e < phi and gcd(e, phi) = 1."""
    for e in PUBLIC_EXPONENTS:
        if e < phi and gcd(e, phi) == 1:
            return e
    raise ValueError(f"no valid public exponent for phi = {phi}")


def build_key(p, q, e=None):
    """Build the full key from p and q: n = pq, phi = (p-1)(q-1), d = e^-1 mod phi."""
    phi = (p - 1) * (q - 1)
    if e is None:
        e = choose_public_exponent(phi)
    d = mod_inverse(e, phi)
    return RSAKey(n=p * q, e=e, d=d, p=p, q=q)


def generate_keypair(bits, rng=random):
    """RSA key whose modulus n has exactly `bits` bits (two primes of ~bits/2 bits)."""
    if bits < 6:
        raise ValueError("use at least 6 bits for the modulus")
    half = bits // 2
    while True:
        p = random_prime(half, rng)
        q = random_prime(bits - half, rng)
        if p == q:
            continue
        try:
            return build_key(p, q)
        except ValueError:              # no valid e for this phi: pick new primes
            continue


def encrypt(m, e, n):
    """c = m^e mod n."""
    if not 0 <= m < n:
        raise ValueError("message must satisfy 0 <= m < n")
    return mod_pow(m, e, n)


def decrypt(c, d, n):
    """m = c^d mod n."""
    return mod_pow(c, d, n)


def recover_private_key(n, e, factor):
    """Attack: factor n with `factor`, then rebuild d exactly like the key owner.

    Returns (key, factor_result).
    """
    result = factor(n)
    if result.p * result.q != n:
        raise ValueError("factorization is wrong: p * q != n")
    key = build_key(result.p, result.q, e)
    return key, result
