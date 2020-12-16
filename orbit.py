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
    lowest_dist = mpf(2)
    while True:
        n *= 3
        n_d *= 2
        r = n / (n_d * d)
        if r > 1.5:
            j += 1
            d *= 2
            r = n / (n_d * d)

        dist = r if r >= 1.0 else mpf(1) / r

        if dist < lowest_dist:
            lowest_dist = dist
            print("%r\t%r\t%r\t%r" % (i, j, r, dist))

        i += 1


if __name__ == "__main__":
    main()
