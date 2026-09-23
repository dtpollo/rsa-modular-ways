"""Draw the report figures from the JSON files in results/.

It only reads saved results, it never runs the algorithms. Run the
experiments first, then:
    python -m experiments.plot_results
    python -m experiments.plot_results --formats png pdf   # PDF for LaTeX

Figures are saved in results/figures/.
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                   # draw to files, no window needed
import matplotlib.pyplot as plt

from src.results_io import RESULTS_DIR, load_json

MARKERS = {"Trial Division": "o", "Fermat": "s", "Pollard's Rho": "^"}


def save(fig, out_dir, name, formats):
    for fmt in formats:
        path = out_dir / f"{name}.{fmt}"
        fig.savefig(path, dpi=200, bbox_inches="tight")
        print(f"  {path}")
    plt.close(fig)


def plot_benchmark_time(data, out_dir, formats):
    """Mean time vs modulus size, one line per algorithm (error bars = stdev)."""
    results = data["results"]
    bits = [entry["bits"] for entry in results]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in results[0]["algorithms"]:
        means = [entry["algorithms"][name]["mean_s"] for entry in results]
        stdevs = [entry["algorithms"][name]["stdev_s"] for entry in results]
        ax.errorbar(bits, means, yerr=stdevs, marker=MARKERS.get(name, "o"),
                    capsize=3, label=name)
    ax.set_yscale("log")                # times differ by orders of magnitude
    ax.set_xticks(bits)
    ax.set_xlabel("Modulus size (bits)")
    ax.set_ylabel("Mean time (s, log scale)")
    ax.set_title(f"Factorization time ({data['parameters']['repeats']} repeats per point)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    save(fig, out_dir, "benchmark_time", formats)


def plot_benchmark_iterations(data, out_dir, formats):
    """Iterations vs modulus size: the cost without depending on the computer speed."""
    results = data["results"]
    bits = [entry["bits"] for entry in results]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in results[0]["algorithms"]:
        iterations = [max(entry["algorithms"][name]["iterations"], 1) for entry in results]
        ax.plot(bits, iterations, marker=MARKERS.get(name, "o"), label=name)
    # Reference curve sqrt(n) / 2: the worst case of Trial Division (odd divisors only).
    ax.plot(bits, [2 ** (b / 2) / 2 for b in bits], "k--", alpha=0.5, label=r"$\sqrt{n}/2$")
    ax.set_yscale("log")
    ax.set_xticks(bits)
    ax.set_xlabel("Modulus size (bits)")
    ax.set_ylabel("Iterations (log scale)")
    ax.set_title("Iterations needed to factor n")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    save(fig, out_dir, "benchmark_iterations", formats)


def plot_fermat_distance(data, out_dir, formats):
    """Fermat iterations and time for each |p - q| case (same modulus size)."""
    results = data["results"]
    # Short labels: case on the first line, |p - q| on the second.
    labels = [("close" if row["ratio"] == 1 else f"q/p≈{row['ratio']}") + f"\n{row['distance']:,}"
              for row in results]
    iterations = [row["iterations"] for row in results]
    times = [row["mean_s"] for row in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.3))
    for ax, values, ylabel, fmt in [
        (ax1, iterations, "Fermat iterations (log scale)", "{:,}"),
        (ax2, times, "Mean time (s, log scale)", "{:.2e}"),
    ]:
        bars = ax.bar(labels, values, color="tab:orange")
        ax.bar_label(bars, labels=[fmt.format(v) for v in values], fontsize=8)
        ax.set_yscale("log")
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Case and |p - q|")
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(True, axis="y", which="both", alpha=0.3)
    fig.suptitle(f"Fermat factorization vs |p - q| ({data['parameters']['bits']}-bit moduli)")
    fig.tight_layout()
    save(fig, out_dir, "fermat_distance", formats)


PLOTS = {
    "benchmark.json": [plot_benchmark_time, plot_benchmark_iterations],
    "fermat_distance.json": [plot_fermat_distance],
}


def main():
    parser = argparse.ArgumentParser(description="Plot the saved experiment results.")
    parser.add_argument("--results", type=Path, default=RESULTS_DIR, help="folder with the JSON files")
    parser.add_argument("--formats", nargs="+", default=["png"], help="e.g. png pdf svg")
    args = parser.parse_args()

    out_dir = args.results / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    for filename, plot_functions in PLOTS.items():
        path = args.results / filename
        if not path.exists():
            print(f"Skipping {filename}: file not found (run the experiment first)")
            continue
        data = load_json(path)
        print(f"{filename}:")
        for plot in plot_functions:
            plot(data, out_dir, args.formats)


if __name__ == "__main__":
    main()
