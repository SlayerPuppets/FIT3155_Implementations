def karatsuba(x: int, y: int) -> int:
    """
    Multiply two nonnegative integers x and y using the
    divide-and-conquer (Karatsuba) algorithm.
    """
    # Base case: if either is small, use direct multiplication
    if x < 10 or y < 10:
        return x * y

    # n = max bit-length of the inputs
    n = max(x.bit_length(), y.bit_length())
    m = n // 2

    # Split x and y into high and low bits
    high_x, low_x = x >> m, x & ((1 << m) - 1)
    high_y, low_y = y >> m, y & ((1 << m) - 1)

    # 3 recursive multiplications
    z0 = karatsuba(low_x,  low_y)
    z1 = karatsuba(high_x, high_y)
    z2 = karatsuba(low_x + high_x, low_y + high_y)

    # Combine according to Karatsuba’s formula
    return (z1 << (2 * m)) + ((z2 - z1 - z0) << m) + z0


# Example usage:
if __name__ == "__main__":
    a = 12345678901234567890
    b = 98765432109876543210
    print(karatsuba(a, b))  # should equal a * b
