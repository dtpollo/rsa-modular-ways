"""Exercise 7: how the distance |p - q| affects Fermat's factorization.

All moduli are built around the same target value, so they have the same
bit size and only the distance between p and q changes.

Run from the project root:
    python -m experiments.fermat_distance
    python -m experiments.fermat_distance --bits 40 --ratios 1 4

Results are saved in results/fermat_distance.json (plot them with plot_results.py).
"""

import argparse
import statistics
import time
from pathlib import Path

from src.factorization import fermat
from src.number_theory import isqrt, next_prime
from src.results_io import RESULTS_DIR, save_json

# ratio = q / p. 1 means p and q are consecutive primes (close), the rest are far.
DEFAULT_RATIOS = [1, 2, 4, 8]


def make_modulus(bits, ratio):
    """Primes p < q with q/p ~ ratio and n = p*q close to 1.5 * 2^(bits-1)."""
    target = 3 << (bits - 2)            # middle of the range of `bits`-bit numbers
    p = next_prime(isqrt(target // ratio))
    q = next_prime(max(p, target // p))
    return p, q


def ceil_sqrt(n):
    root = isqrt(n)
    return root if root * root == n else root + 1


def predicted_iterations(p, q):
    """Fermat stops at a = (p + q) / 2, starting from ceil(sqrt(n))."""
    return (p + q) // 2 - ceil_sqrt(p * q) + 1


def run(bits, ratios, repeats):
    results = []
    for ratio in ratios:
        p, q = make_modulus(bits, ratio)
        n = p * q
        times = []
        for _ in range(repeats):
            start = time.perf_counter()
            result = fermat(n)
            times.append(time.perf_counter() - start)
        assert (result.p, result.q) == (p, q)
        results.append({
            "case": "close" if ratio == 1 else f"far (q/p~{ratio})",
            "ratio": ratio,
            "bits": n.bit_length(), "n": n, "p": p, "q": q,
            "distance": q - p,
            "iterations": result.iterations,
            "predicted_iterations": predicted_iterations(p, q),
            "times_s": times,
            "mean_s": statistics.mean(times),
        })
    return results


def print_table(results):
    print(f"{'case':<16}{'bits':>5}{'p':>12}{'q':>12}{'|p-q|':>12}{'iterations':>12}{'time (s)':>12}")
    for row in results:
        print(f"{row['case']:<16}{row['bits']:>5}{row['p']:>12}{row['q']:>12}"
              f"{row['distance']:>12}{row['iterations']:>12}{row['mean_s']:>12.6f}")


def main():
    parser = argparse.ArgumentParser(description="Fermat performance vs |p - q|.")
    parser.add_argument("--bits", type=int, default=40, help="size of every modulus")
    parser.add_argument("--ratios", type=int, nargs="+", default=DEFAULT_RATIOS,
                        help="q/p ratios to test (1 = close primes)")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    results = run(args.bits, args.ratios, args.repeats)
    print_table(results)
    parameters = {"bits": args.bits, "ratios": args.ratios, "repeats": args.repeats}
    path = save_json("fermat_distance", parameters, results, args.out)
    print(f"\nResults saved in {path}")


if __name__ == "__main__":
    main()
