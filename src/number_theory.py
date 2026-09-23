"""Number theory helpers used by the factorization algorithms and by RSA."""

import random

# Bases for Miller-Rabin. Testing all of them is deterministic for n < 3.3e24,
# which covers every modulus used in this lab.
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def gcd(a, b):
    """Greatest common divisor with Euclid's algorithm: gcd(a, b) = gcd(b, a mod b)."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """Return (g, s, t) such that a*s + b*t = g = gcd(a, b) (Bezout identity)."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def mod_inverse(a, m):
    """Return x such that a*x = 1 (mod m). It exists only if gcd(a, m) = 1."""
    g, s, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse modulo {m} (gcd = {g})")
    return s % m


def mod_pow(base, exp, mod):
    """Compute base^exp mod m with square-and-multiply (fast modular exponentiation)."""
    if exp < 0:
        raise ValueError("exponent must be non-negative")
    if mod == 1:
        return 0
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:                     # current bit is 1: multiply into the result
            result = result * base % mod
        base = base * base % mod        # square for the next bit
        exp >>= 1
    return result


def isqrt(n):
    """Largest integer k such that k*k <= n (Newton's method, integers only)."""
    if n < 0:
        raise ValueError("square root of a negative number")
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + 1) // 2)    # start above the real root
    while True:
        y = (x + n // x) // 2
        if y >= x:                          # stopped decreasing: x is the answer
            return x
        x = y


def is_perfect_square(n):
    """True if n = k*k for some integer k."""
    if n < 0:
        return False
    # Squares mod 16 can only be 0, 1, 4 or 9: cheap filter before isqrt.
    if n & 15 not in (0, 1, 4, 9):
        return False
    root = isqrt(n)
    return root * root == n


def is_prime(n):
    """Miller-Rabin primality test (deterministic in the range used by this lab)."""
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p

    # Write n - 1 = 2^s * d with d odd.
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for a in SMALL_PRIMES:
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False                    # a proves that n is composite
    return True


def next_prime(n):
    """Smallest prime strictly greater than n."""
    candidate = max(n + 1, 2)
    while not is_prime(candidate):
        candidate += 1
    return candidate


def random_prime(bits, rng=random):
    """Random prime with exactly `bits` bits.

    The two highest bits are set, so the product of two such primes
    has exactly the sum of their bit sizes (useful for RSA moduli).
    """
    if bits < 2:
        raise ValueError("a prime needs at least 2 bits")
    if bits == 2:
        return 3
    top_bits = (1 << (bits - 1)) | (1 << (bits - 2))
    while True:
        candidate = rng.getrandbits(bits) | top_bits | 1    # exact size and odd
        if is_prime(candidate):
            return candidate
