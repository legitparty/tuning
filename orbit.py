#!/usr/bin/env python3

from mpmath import *

def main():
    mp.dps = 100
    mp.pretty = True

    i = 1
    j = 0
    n = mpf(1)
    n_d = mpf(1)
    d = mpf(1)
    lowest_i = 0
    lowest_dist = 1.0
    while True:
        n *= 3
        n_d *= 2
        r = n / (n_d * d)
        if r > 2:
            j += 1
            d *= 2
            r = n / (n_d * d)

        dist = abs(r - 1.0)
        if dist < lowest_dist:
            lowest_dist = dist
            print()
            print(i, j, r, dist)

        i += 1


if __name__ == "__main__":
    main()
