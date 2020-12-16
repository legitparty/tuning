#!/usr/bin/env python3

try:
    from mpmath import *
    mp.dps = 100
    mp.pretty = True
    slow = True
except ImportError:
    mpf = lambda x: float(x)
    from math import log
    slow = False

def comma(p_n, p_d, n, d):
    try:
        return p_n ** n / (p_d ** n * mpf(2) ** d)
    except OverflowError:
        return None

def main():
    from sys import argv
    args = dict(enumerate(argv))

    p_n = mpf(int(args.get(1, "3")))
    p_d = mpf(int(args.get(2, "2")))
    limit = int(args.get(3, "0"))
    target = log(p_n / p_d, 2)
    #print(target)
    lowest_dist = mpf(2.0)

    def candidates():
        n = mpf(1)
        while limit == 0 or n <= limit:
            n += 1
            target_d = n * target
            d1 = int(target_d)
            d2 = d1 + 1
            if d1 > 0:
                yield n, d1
            yield n, d2

    for n, d in candidates():
        r = d / n
        #print(r * 12)
        dist = r / target if r > target else target / r
        if dist < lowest_dist:
            lowest_dist = dist
            print("%r\t%r\t%r" % (int(n), d, comma(p_n, p_d, n, d)))



if __name__ == "__main__":
    main()
