"""Exercise 4: recover the RSA private key from (n, e) and decrypt c.

Run from the project root:
    python -m src.main                       # lab values n=3233, e=17, c=2790
    python -m src.main --n 8051 --e 7 --c 42 # any other small modulus

Results are also saved in results/key_recovery.json.
"""

import argparse
import time
from pathlib import Path

from .factorization import ALGORITHMS
from .results_io import RESULTS_DIR, save_json
from .rsa import decrypt, encrypt, recover_private_key

# Public values given by the lab. p and q are NOT stored: they are recovered.
LAB_N, LAB_E, LAB_C = 3233, 17, 2790


def attack(n, e, c):
    """Break (n, e) with each algorithm and decrypt c. Returns one dict per algorithm."""
    print(f"Public key: n = {n}, e = {e}   Ciphertext: c = {c}\n")
    results = []
    for name, factor in ALGORITHMS.items():
        start = time.perf_counter()
        key, result = recover_private_key(n, e, factor)
        elapsed = time.perf_counter() - start
        m = decrypt(c, key.d, n)
        ok = encrypt(m, e, n) == c      # check: m^e mod n = c

        print(f"== {name} ==")
        print(f"  factors:     p = {key.p}, q = {key.q}  ({result.iterations} iterations)")
        print(f"  check:       p * q = {key.p * key.q} = n -> {key.p * key.q == n}")
        print(f"  phi(n):      ({key.p} - 1)({key.q} - 1) = {key.phi}")
        print(f"  private key: (n, d) = ({n}, {key.d})")
        print(f"  message:     m = c^d mod n = {m}")
        print(f"  check:       m^e mod n = c -> {ok}\n")

        results.append({
            "algorithm": name, "p": key.p, "q": key.q,
            "iterations": result.iterations, "time_s": elapsed,
            "phi": key.phi, "d": key.d, "m": m,
            "pq_equals_n": key.p * key.q == n, "reencrypt_matches_c": ok,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Break small RSA keys by factoring n.")
    parser.add_argument("--n", type=int, default=LAB_N, help="RSA modulus")
    parser.add_argument("--e", type=int, default=LAB_E, help="public exponent")
    parser.add_argument("--c", type=int, default=LAB_C, help="ciphertext")
    parser.add_argument("--out", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    results = attack(args.n, args.e, args.c)
    path = save_json("key_recovery", {"n": args.n, "e": args.e, "c": args.c}, results, args.out)
    print(f"Results saved in {path}")


if __name__ == "__main__":
    main()
