# Lab 4: RSA Factorization Attacks

This project breaks small RSA keys by factoring the modulus n = pq. It uses three algorithms:

- **Trial Division**: tries odd divisors up to √n.
- **Fermat**: writes n as a² − b² = (a − b)(a + b).
- **Pollard's Rho**: iterates f(x) = x² + c (mod n) and uses d = gcd(|x − y|, n) to find a factor.

With p and q, the program rebuilds the private key (φ(n) = (p − 1)(q − 1), d = e⁻¹ mod φ(n)) and decrypts the ciphertext.

All the math is written from scratch. No library is used to factor n, and p and q are never written in the code. The only external libraries are `pytest` (tests) and `matplotlib` (plots).

---

## Requirements

- Python 3.10 or newer
- `pip`

## Installation

Run these commands from the project root.

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Activate it:

   ```bash
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Windows (cmd)
   .venv\Scripts\activate.bat

   # Linux / macOS
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

> Run every command in this guide from the project root. The code runs as modules (`python -m ...`).

---

## 1. Tests (Exercise 5)

```bash
pytest
```

There are 92 tests, and all of them must pass before you run the experiments. Use `pytest -v` to see each test.

| File | What it checks |
|---|---|
| `tests/test_number_theory.py` | gcd, extended Euclid, modular inverse, integer square root, perfect squares, modular power, primality |
| `tests/test_factorization.py` | The three algorithms on known and random moduli, p · q = n, prime inputs rejected, iteration counts |
| `tests/test_rsa.py` | Lab key recovery (d = 2753, m = 65), encryption and decryption |
| `tests/test_results_io.py` | Saving and loading the JSON result files |

## 2. Private key recovery (Exercise 4)

```bash
python -m src.main
```

It uses the lab values n = 3233, e = 17 and c = 2790. Each algorithm factors n, rebuilds d, decrypts c and checks that mᵉ mod n = c.

Expected result: p = 53, q = 61, φ(n) = 3120, d = 2753, **m = 65**.

To try other values:

```bash
python -m src.main --n 8051 --e 7 --c 42
```

Output: `results/key_recovery.json`

## 3. Benchmark (Exercise 6)

```bash
python -m experiments.benchmark
```

It creates RSA moduli of 16, 24, 32, 40 and 48 bits. Then it factors each one with the three algorithms, 3 times each, and reports the average time. The seed is fixed, so every run uses the same moduli.

| Option | Default | Meaning |
|---|---|---|
| `--bits` | `16 24 32 40 48` | Modulus sizes |
| `--repeats` | `3` | Runs per algorithm and modulus |
| `--seed` | `2026` | Random seed |
| `--out` | `results` | Output folder |

Example: `python -m experiments.benchmark --bits 20 30 40 --repeats 5`

> Trial Division grows with √n, so it gets about 16 times slower every 8 bits. Above ~50 bits it takes minutes.

Output: `results/benchmark.json`

## 4. Fermat analysis (Exercise 7)

```bash
python -m experiments.fermat_distance
```

All moduli have the same size. Only the distance |p − q| changes. For each case it records |p − q|, the number of iterations and the time.

| Option | Default | Meaning |
|---|---|---|
| `--bits` | `40` | Size of every modulus |
| `--ratios` | `1 2 4 8` | q/p ratios (1 = close primes) |
| `--repeats` | `3` | Runs per case |
| `--out` | `results` | Output folder |

To run only the two cases the lab asks for (close and far): `python -m experiments.fermat_distance --ratios 1 4`

Output: `results/fermat_distance.json`

## 5. Figures

```bash
python -m experiments.plot_results --formats png pdf
```

This script only reads the JSON files. It never runs the algorithms, so you can redraw the figures without measuring again. If a JSON file is missing, it skips that figure.

| Figure | What it shows |
|---|---|
| `benchmark_time` | Average time vs modulus size |
| `benchmark_iterations` | Iterations vs modulus size, with the √n/2 reference line |
| `fermat_distance` | Fermat iterations and time for each \|p − q\| |

Output: `results/figures/` (PNG, plus PDF when `--formats` includes `pdf`)

## 6. Interactive mode

```bash
python -m src.interactive
```

A menu that asks for the values and shows each step of the result:

1. Factor a number.
2. Break an RSA key (n, e, c) and decrypt it. Press Enter to use the lab values.
3. Build the private key from p and q.
4. Demo: create a random key, encrypt a message and break it.
5. Encrypt or decrypt with a known key.

Press **Ctrl+C** to stop a long factorization and go back to the menu.

## 7. Report

The final report is `report/main.pdf`.

---

## Run everything

```bash
pytest
python -m src.main
python -m experiments.benchmark
python -m experiments.fermat_distance
python -m experiments.plot_results --formats png pdf
```

## Result files

Each JSON file has three parts:

- `machine`: date, operating system, processor and Python version. This shows that every run used the same computer.
- `parameters`: the options used in the run.
- `results`: the data, with every measured time (`times_s`), the average and the standard deviation.

Running an experiment again replaces its JSON file.

---

## Project structure

```
rsa-modular-ways/
├── src/
│   ├── number_theory.py    # gcd, extended_gcd, mod_inverse, mod_pow, isqrt, is_prime, random_prime
│   ├── factorization.py    # trial_division, fermat, pollard_rho
│   ├── rsa.py              # key generation, encrypt, decrypt, recover_private_key
│   ├── results_io.py       # save and load JSON results
│   ├── main.py             # Exercise 4
│   └── interactive.py      # interactive menu
├── experiments/
│   ├── benchmark.py        # Exercise 6
│   ├── fermat_distance.py  # Exercise 7
│   └── plot_results.py     # figures from the JSON files
├── tests/                  # Exercise 5
├── results/                # JSON files and figures
├── main.pdf                # final report
├── requirements.txt
├── pytest.ini
└── README.md
```

## Where each algorithm is in the code

| Algorithm | Function | Key lines |
|---|---|---|
| Trial Division | `src/factorization.py` → `trial_division` | `while i * i <= n` and `i += 2` (skips even numbers) |
| Fermat | `src/factorization.py` → `fermat` | starts at a = ⌈√n⌉ and adds 2a + 1 to b² until it is a perfect square |
| Pollard's Rho | `src/factorization.py` → `pollard_rho` | `x` moves 1 step, `y` moves 2 steps, `d = gcd(abs(x - y), n)`, restarts with c + 1 if d = n |
| Key recovery | `src/rsa.py` → `recover_private_key` | factor n → φ(n) → d = e⁻¹ mod φ(n) |
