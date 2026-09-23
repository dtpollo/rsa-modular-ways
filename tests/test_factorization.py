import random

import pytest

from src.factorization import ALGORITHMS, fermat, pollard_rho, trial_division
from src.number_theory import is_prime
from src.rsa import generate_keypair

ALGORITHM_FUNCS = list(ALGORITHMS.values())
ALGORITHM_IDS = list(ALGORITHMS)

# Known composites: RSA-like (two primes), small cases and even numbers.
KNOWN = [
    (3233, 53, 61),     # the lab modulus
    (8051, 83, 97),
    (35, 5, 7),
    (143, 11, 13),
    (141, 3, 47),
    (15, 3, 5),
    (10, 2, 5),
    (1_000_003 * 1_000_033, 1_000_003, 1_000_033),
]


@pytest.mark.parametrize("factor", ALGORITHM_FUNCS, ids=ALGORITHM_IDS)
@pytest.mark.parametrize("n, p, q", KNOWN)
def test_known_factorizations(factor, n, p, q):
    result = factor(n)
    assert (result.p, result.q) == (p, q)
    assert result.p * result.q == n     # factor verification: pq = n


@pytest.mark.parametrize("factor", ALGORITHM_FUNCS, ids=ALGORITHM_IDS)
def test_random_rsa_moduli(factor):
    rng = random.Random(42)
    for bits in (12, 16, 20, 24, 28, 32):
        key = generate_keypair(bits, rng)
        result = factor(key.n)
        assert result.p * result.q == key.n
        assert 1 < result.p <= result.q < key.n
        assert is_prime(result.p) and is_prime(result.q)


@pytest.mark.parametrize("factor", ALGORITHM_FUNCS, ids=ALGORITHM_IDS)
@pytest.mark.parametrize("n", [2, 3, 13, 61, 7919])
def test_prime_input_is_rejected(factor, n):
    with pytest.raises(ValueError):
        factor(n)


def test_trial_division_iterations():
    # 1 check for 2, then odd 3, 5, ..., 53 -> 1 + 26 = 27
    assert trial_division(3233).iterations == 27


def test_fermat_iterations():
    assert fermat(3233).iterations == 1     # 57^2 - 3233 = 16 = 4^2
    assert fermat(143).iterations == 1      # 12^2 - 143 = 1
    assert fermat(141).iterations == 14     # a = 12 ... 25


def test_pollard_rho_iterations():
    # f(x) = x^2 + 1, x0 = 2: gcd(|677 - 871|, 8051) = 97 at step 3
    assert pollard_rho(8051).iterations == 3
    # f(x) = x^2 + 1, x0 = 2: gcd(|5 - 26|, 35) = 7 at step 1
    assert pollard_rho(35).iterations == 1


def test_pollard_rho_restarts_when_d_equals_n():
    # For n = 25 with c = 1 the first attempt gives d = n (x = y = 2),
    # so the algorithm must restart with c = 2.
    result = pollard_rho(25)
    assert (result.p, result.q) == (5, 5)
