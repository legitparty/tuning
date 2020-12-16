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
        return mpf(p_n) ** mpf(n) / (mpf(p_d) ** mpf(n) * mpf(2) ** mpf(d))
    except OverflowError:
        return None

def main():
    from sys import argv
    args = dict(enumerate(argv))

    if args.get(4, None):
        from math import log as l
        f = lambda x: float(x)
    else:
        f = mpf
        l = log

    p_n = f(int(args.get(1, "3")))
    p_d = f(int(args.get(2, "2")))
    limit = int(args.get(3, "0"))
    target = l(p_n / p_d, 2)
    #print(target)
    lowest_dist = f(2.0)

    def candidates():
        n = f(1)
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
