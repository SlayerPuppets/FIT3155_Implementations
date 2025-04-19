import random

def modexp(base: int, exponent: int, modulus: int) -> int:
    """
    Efficient modular exponentiation by repeated squaring.
    Returns (base ** exponent) % modulus.
    """
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
    return result

def is_prime(n: int, k: int = 5) -> bool:
    """
    Miller–Rabin probabilistic primality test.
    Test n for primality using k random bases.
    Returns True if n is probably prime, False if composite.
    """
    if n < 2:
        return False
    # Check small primes first
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # Write n-1 as d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # Witness loop
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = modexp(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_primes(count: int) -> list[int]:
    """
    Generate the first `count` prime numbers using the
    Miller–Rabin test as the primality oracle.
    """
    primes = []
    candidate = 2
    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes

if __name__ == "__main__":
    # Generate the first 10,000 primes
    first_10000_primes = generate_primes(10000)
    # (The list is now in `first_10000_primes`, but we don't print it here.)


print(first_10000_primes)  