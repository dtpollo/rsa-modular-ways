import random

import pytest

from src.factorization import ALGORITHMS
from src.rsa import build_key, decrypt, encrypt, generate_keypair, recover_private_key

ALGORITHM_FUNCS = list(ALGORITHMS.values())
ALGORITHM_IDS = list(ALGORITHMS)

LAB_N, LAB_E, LAB_C = 3233, 17, 2790


@pytest.mark.parametrize("factor", ALGORITHM_FUNCS, ids=ALGORITHM_IDS)
def test_lab_key_recovery(factor):
    """Exercise 4: factor n, rebuild d and decrypt c."""
    key, _ = recover_private_key(LAB_N, LAB_E, factor)
    assert {key.p, key.q} == {61, 53}   # expected factors from the lab statement
    assert key.phi == 3120
    assert key.d == 2753
    m = decrypt(LAB_C, key.d, LAB_N)
    assert m == 65
    assert encrypt(m, LAB_E, LAB_N) == LAB_C


def test_hand_example():
    key = build_key(3, 11, 7)           # Apunte 1: n = 33, phi = 20, d = 3
    assert (key.n, key.d) == (33, 3)
    assert encrypt(5, key.e, key.n) == 14
    assert decrypt(14, key.d, key.n) == 5


@pytest.mark.parametrize("bits", [16, 24, 32, 48, 64])
def test_encrypt_decrypt_consistency(bits):
    rng = random.Random(bits)
    key = generate_keypair(bits, rng)
    assert key.n.bit_length() == bits
    assert key.e * key.d % key.phi == 1
    for m in [0, 1, 2, key.n - 1] + [rng.randrange(key.n) for _ in range(20)]:
        assert decrypt(encrypt(m, key.e, key.n), key.d, key.n) == m


@pytest.mark.parametrize("factor", ALGORITHM_FUNCS, ids=ALGORITHM_IDS)
def test_recovered_key_decrypts_random_messages(factor):
    rng = random.Random(7)
    original = generate_keypair(28, rng)
    recovered, _ = recover_private_key(original.n, original.e, factor)
    assert recovered.d == original.d
    m = rng.randrange(original.n)
    assert decrypt(encrypt(m, original.e, original.n), recovered.d, original.n) == m


def test_message_out_of_range():
    with pytest.raises(ValueError):
        encrypt(3233, LAB_E, LAB_N)
