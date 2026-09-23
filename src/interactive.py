"""Interactive terminal tool: enter the parameters and see each step of the result.

Run from the project root:
    python -m src.interactive

Press Ctrl+C during a long factorization to cancel it and return to the menu.
"""

import time

from .factorization import ALGORITHMS
from .number_theory import gcd, is_prime
from .rsa import build_key, decrypt, encrypt, generate_keypair, recover_private_key

ALGORITHM_NAMES = list(ALGORITHMS)

# Above this size Trial Division takes too long in Python, so we warn first.
TRIAL_DIVISION_WARNING_BITS = 56


# --- Input helpers -----------------------------------------------------

def ask_int(prompt, minimum=None, maximum=None, default=None):
    """Ask until the user types a valid integer in [minimum, maximum]."""
    hint = f" [{default}]" if default is not None else ""
    while True:
        text = input(f"{prompt}{hint}: ").strip()
        if not text and default is not None:
            return default
        try:
            value = int(text)
        except ValueError:
            print("  Please enter an integer.")
            continue
        if minimum is not None and value < minimum:
            print(f"  The value must be >= {minimum}.")
        elif maximum is not None and value > maximum:
            print(f"  The value must be <= {maximum}.")
        else:
            return value


def ask_yes_no(prompt, default=True):
    hint = "Y/n" if default else "y/N"
    text = input(f"{prompt} ({hint}): ").strip().lower()
    return default if not text else text.startswith("y")


def ask_algorithms():
    """Let the user pick one algorithm or all of them."""
    print("  Algorithm:")
    for i, name in enumerate(ALGORITHM_NAMES, start=1):
        print(f"    {i}) {name}")
    print(f"    {len(ALGORITHM_NAMES) + 1}) All")
    choice = ask_int("  Choose", 1, len(ALGORITHM_NAMES) + 1, default=len(ALGORITHM_NAMES) + 1)
    if choice == len(ALGORITHM_NAMES) + 1:
        return ALGORITHM_NAMES
    return [ALGORITHM_NAMES[choice - 1]]


def confirm_slow(name, n):
    if name == "Trial Division" and n.bit_length() > TRIAL_DIVISION_WARNING_BITS:
        return ask_yes_no(f"  n has {n.bit_length()} bits, Trial Division may take very long. Run it?",
                          default=False)
    return True


# --- Menu options ------------------------------------------------------

def factor_number():
    """Option 1: factor n with the chosen algorithms."""
    n = ask_int("n (composite number to factor)", minimum=4)
    if is_prime(n):
        print(f"  {n} is prime: it cannot be factored.")
        return
    for name in ask_algorithms():
        if not confirm_slow(name, n):
            continue
        start = time.perf_counter()
        result = ALGORITHMS[name](n)
        elapsed = time.perf_counter() - start
        print(f"\n  == {name} ==")
        print(f"  p = {result.p}, q = {result.q}")
        print(f"  p * q = n -> {result.p * result.q == n}")
        print(f"  {result.iterations} iterations, {elapsed:.6f} s")


def break_rsa():
    """Option 2: the full attack. Factor n, rebuild d and decrypt c."""
    n = ask_int("n (public modulus)", minimum=4, default=3233)
    e = ask_int("e (public exponent)", minimum=2, default=17)
    c = ask_int("c (ciphertext)", minimum=0, maximum=n - 1, default=2790)
    for name in ask_algorithms():
        if not confirm_slow(name, n):
            continue
        start = time.perf_counter()
        try:
            key, result = recover_private_key(n, e, ALGORITHMS[name])
        except ValueError as error:     # e.g. e has no inverse modulo phi(n)
            print(f"  {name}: {error}")
            continue
        elapsed = time.perf_counter() - start
        m = decrypt(c, key.d, n)
        print(f"\n  == {name} ==  ({result.iterations} iterations, {elapsed:.6f} s)")
        print(f"  1. Factor n:      p = {key.p}, q = {key.q}   (p * q = n -> {key.p * key.q == n})")
        print(f"  2. phi(n):        ({key.p} - 1)({key.q} - 1) = {key.phi}")
        print(f"  3. d = e^-1 mod phi(n) = {key.d}   (e * d mod phi = {e * key.d % key.phi})")
        print(f"  4. Private key:   (n, d) = ({n}, {key.d})")
        print(f"  5. m = c^d mod n = {m}")
        print(f"  6. Check m^e mod n = c -> {encrypt(m, e, n) == c}")


def key_from_primes():
    """Option 3: build the private key from p and q (what the key owner does)."""
    p = ask_int("p (prime)", minimum=2)
    q = ask_int("q (prime, different from p)", minimum=2)
    if not (is_prime(p) and is_prime(q)) or p == q:
        print("  p and q must be two different primes.")
        return
    phi = (p - 1) * (q - 1)
    e = ask_int("e (public exponent, gcd(e, phi) = 1)", minimum=2, maximum=phi - 1)
    if gcd(e, phi) != 1:
        print(f"  gcd({e}, {phi}) = {gcd(e, phi)} != 1: e has no inverse, choose another e.")
        return
    key = build_key(p, q, e)
    print(f"\n  n = p * q = {key.n}")
    print(f"  phi(n) = (p - 1)(q - 1) = {key.phi}")
    print(f"  d = e^-1 mod phi(n) = {key.d}")
    print(f"  Public key: (n, e) = ({key.n}, {key.e})")
    print(f"  Private key: (n, d) = ({key.n}, {key.d})")
    if ask_yes_no("  Encrypt a message with this key?"):
        m = ask_int("  m (message)", minimum=0, maximum=key.n - 1)
        c = encrypt(m, key.e, key.n)
        print(f"  c = m^e mod n = {c}")
        print(f"  Check: c^d mod n = {decrypt(c, key.d, key.n)}")


def demo_attack():
    """Option 4: generate a random key, encrypt, then break it as an attacker."""
    bits = ask_int("Modulus size in bits", minimum=8, maximum=128, default=32)
    key = generate_keypair(bits)
    m = ask_int("m (message)", minimum=0, maximum=key.n - 1, default=min(42, key.n - 1))
    c = encrypt(m, key.e, key.n)
    print(f"\n  Victim's public key: n = {key.n}, e = {key.e}")
    print(f"  Ciphertext: c = {c}")
    print("  The attacker only knows (n, e, c)...")
    for name in ask_algorithms():
        if not confirm_slow(name, key.n):
            continue
        start = time.perf_counter()
        recovered, result = recover_private_key(key.n, key.e, ALGORITHMS[name])
        elapsed = time.perf_counter() - start
        found = decrypt(c, recovered.d, key.n)
        print(f"\n  == {name} ==  ({result.iterations} iterations, {elapsed:.6f} s)")
        print(f"  p = {recovered.p}, q = {recovered.q}, d = {recovered.d}")
        print(f"  Recovered message: {found}  (correct -> {found == m})")


def encrypt_decrypt():
    """Option 5: plain RSA with a known key."""
    n = ask_int("n", minimum=2)
    if ask_yes_no("Encrypt? (no = decrypt)"):
        e = ask_int("e", minimum=1)
        m = ask_int("m (message)", minimum=0, maximum=n - 1)
        print(f"  c = m^e mod n = {encrypt(m, e, n)}")
    else:
        d = ask_int("d", minimum=1)
        c = ask_int("c (ciphertext)", minimum=0, maximum=n - 1)
        print(f"  m = c^d mod n = {decrypt(c, d, n)}")


MENU = [
    ("Factor a number", factor_number),
    ("Break an RSA key (n, e, c) and decrypt", break_rsa),
    ("Build the private key from p and q", key_from_primes),
    ("Demo: generate a random key and break it", demo_attack),
    ("Encrypt / decrypt with a known key", encrypt_decrypt),
]


def main():
    print("RSA Factorization Attacks - interactive mode")
    while True:
        print("\n" + "=" * 50)
        for i, (label, _) in enumerate(MENU, start=1):
            print(f"  {i}) {label}")
        print("  0) Exit")
        try:
            choice = ask_int("Option", 0, len(MENU))
            if choice == 0:
                break
            print()
            MENU[choice - 1][1]()
        except KeyboardInterrupt:
            print("\n  Cancelled.")
        except EOFError:                # input closed (e.g. Ctrl+Z / Ctrl+D)
            break
    print("Bye.")


if __name__ == "__main__":
    main()
