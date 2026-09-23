"""The three factorization algorithms: Trial Division, Fermat and Pollard's Rho.

Each function receives a composite n and returns FactorResult(p, q, iterations)
with p * q = n and p <= q. `iterations` counts the main loop steps, so the
algorithms can be compared independently of the computer speed.
"""

from dataclasses import dataclass

from .number_theory import gcd, is_perfect_square, is_prime, isqrt


@dataclass(frozen=True)
class FactorResult:
    p: int
    q: int
    iterations: int


def _result(a, b, iterations):
    return FactorResult(min(a, b), max(a, b), iterations)


def _check_composite(n):
    if n < 4:
        raise ValueError("n must be a composite integer >= 4")
    if is_prime(n):
        raise ValueError(f"{n} is prime, it has no non-trivial factors")


def trial_division(n):
    """Exercise 1: try divisors 2, 3, 5, 7, 9, ... up to sqrt(n)."""
    _check_composite(n)
    iterations = 1
    if n % 2 == 0:
        return _result(2, n // 2, iterations)

    i = 3
    while i * i <= n:                   # a factor <= sqrt(n) always exists
        iterations += 1
        if n % i == 0:
            return _result(i, n // i, iterations)
        i += 2                          # skip even candidates
    raise ValueError(f"no factor found for {n}")


def fermat(n):
    """Exercise 2: find n = a^2 - b^2 = (a - b)(a + b)."""
    _check_composite(n)
    if n % 2 == 0:
        # a^2 - b^2 cannot represent n = 2 * odd, so handle even n directly.
        return _result(2, n // 2, 0)

    a = isqrt(n)
    if a * a < n:
        a += 1                          # a = ceil(sqrt(n))
    b2 = a * a - n

    iterations = 0
    while True:
        iterations += 1
        if is_perfect_square(b2):
            b = isqrt(b2)
            return _result(a - b, a + b, iterations)
        # (a + 1)^2 - n = (a^2 - n) + 2a + 1: update b^2 without squaring again.
        b2 += 2 * a + 1
        a += 1


def pollard_rho(n, c=1, x0=2, max_restarts=50):
    """Exercise 3: f(x) = x^2 + c (mod n) with Floyd's cycle detection."""
    _check_composite(n)
    if n % 2 == 0:
        return _result(2, n // 2, 0)

    iterations = 0
    for _ in range(max_restarts):
        x = y = x0
        d = 1
        while d == 1:
            x = (x * x + c) % n         # tortoise: one step
            y = (y * y + c) % n         # hare: two steps
            y = (y * y + c) % n
            # x = y (mod p) for a hidden factor p  =>  p divides gcd(|x - y|, n)
            d = gcd(abs(x - y), n)
            iterations += 1
        if d != n:                      # 1 < d < n: non-trivial factor
            return _result(d, n // d, iterations)
        c += 1                          # d = n: the cycle closed mod n, retry with another c
    raise RuntimeError(f"Pollard's Rho failed after {max_restarts} restarts")


# Shared by the main program, the tests and the experiments.
ALGORITHMS = {
    "Trial Division": trial_division,
    "Fermat": fermat,
    "Pollard's Rho": pollard_rho,
}
