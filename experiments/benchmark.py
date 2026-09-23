"""Exercise 6: time the three algorithms on RSA moduli of different bit sizes.

Run from the project root:
    python -m experiments.benchmark
    python -m experiments.benchmark --bits 16 24 32 40 --repeats 5

Results are saved in results/benchmark.json (plot them with plot_results.py).

Note: Trial Division grows like sqrt(n), so every +8 bits makes it ~16x slower.
In Python, more than ~50 bits takes minutes.
"""

import argparse
import random
import statistics
import time
from pathlib import Path

from src.factorization import ALGORITHMS
from src.results_io import RESULTS_DIR, save_json
from src.rsa import generate_keypair

DEFAULT_BITS = [16, 24, 32, 40, 48]


def time_algorithm(factor, n, repeats):
    """Run `factor(n)` several times and keep every measured time."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = factor(n)
        times.append(time.perf_counter() - start)
        assert result.p * result.q == n, "wrong factorization"
    return {
        "iterations": result.iterations,
        "times_s": times,
        "mean_s": statistics.mean(times),
        "stdev_s": statistics.stdev(times) if repeats > 1 else 0.0,
    }


def run(bits_list, repeats, seed):
    """One entry per modulus, with the measurements of each algorithm inside."""
    rng = random.Random(seed)           # fixed seed: same moduli every run
    results = []
    for bits in bits_list:
        key = generate_keypair(bits, rng)
        p, q = sorted((key.p, key.q))
        entry = {"bits": bits, "n": key.n, "p": p, "q": q,
                 "distance": q - p, "algorithms": {}}
        for name, factor in ALGORITHMS.items():
            measure = time_algorithm(factor, key.n, repeats)
            entry["algorithms"][name] = measure
            print(f"{bits:>3} bits  {name:<15} {measure['mean_s']:.6f} s"
                  f"  ({measure['iterations']} iterations)")
        results.append(entry)
    return results


def print_table(results):
    """Same layout as the table in the lab statement."""
    names = list(ALGORITHMS)
    print(f"\n{'Bits':>4}  {'n':>16}  " + "  ".join(f"{name:>15}" for name in names))
    for entry in results:
        times = "  ".join(f"{entry['algorithms'][name]['mean_s']:>13.6f} s" for name in names)
        print(f"{entry['bits']:>4}  {entry['n']:>16}  {times}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark the factorization algorithms.")
    parser.add_argument("--bits", type=int, nargs="+", default=DEFAULT_BITS)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    results = run(args.bits, args.repeats, args.seed)
    print_table(results)
    parameters = {"bits": args.bits, "repeats": args.repeats, "seed": args.seed}
    path = save_json("benchmark", parameters, results, args.out)
    print(f"\nResults saved in {path}")


if __name__ == "__main__":
    main()
