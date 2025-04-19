def modexp(base: int, exponent: int, mod: int) -> int:
    """
    Compute (base**exponent) % mod efficiently using the
    “square‑and‑multiply” (repeated squaring) method.
    """
    result = 1
    base = base % mod                # reduce base modulo mod upfront

    while exponent > 0:
        # If the low bit of exponent is 1, multiply result by current base
        if exponent & 1:
            result = (result * base) % mod

        # Square the base for the next bit of the exponent
        base = (base * base) % mod

        # Shift exponent right by 1 bit (i.e. floor-divide by 2)
        exponent >>= 1

    return result


print(modexp(7, 330, 13))   # outputs: 12
