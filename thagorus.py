#!/usr/bin/env python3

from math import log, gcd


r      = lambda n, d: (n // gcd(n, d), d // gcd(n, d)) # reduce fraction
lcd    = lambda n, d: r(n, d)[1] # least common denominator
cycles = lambda n   : [(i, lcd(i, n)) for i in range(n) if lcd(i, n) == n] # note coverage in cycles in scale of size n


class Sphere:
  def __init__(self, base = 12):
    self.base = base

    self.cycles = cycles(self.base)

    self.intervals = Intervals(self)


  def interval(self, numerator, denominator = 1.0):
    ratio = float(numerator) / float(denominator)
    return (self.base * log(ratio)) / log(2)

  def ratio(self, note):
    return 2.0 ** (float(note) / self.base)

class Intervals:
  def __init__(self, sphere):
    self.sphere    = sphere
    self.intervals = {}

    harmonic = 2 
    while True:
      harmonic += 1
      interval = Interval(self.sphere, harmonic, harmonic - 1)
      self.add_interval(interval)

      if interval.interval <= 1:
          break

  def get_best(self):
    for i in self.intervals:
      yield self.intervals[i][0]

  def __str__(self):
    s = ""
    for interval in self.get_best():
      s += str(interval) + "\n"

    return s

  @property
  def dissonance(self):
    d = 0.0
    c = 0.0
    for interval in self.get_best():
      c += interval.ratio 
      d += (interval.ratio * abs(interval.offset))

    return d / c

  def add_interval(self, interval):
    if interval.note not in self.intervals:
      self.intervals[interval.note] = []

    self.intervals[interval.note].append(interval)
    self.intervals[interval.note].sort(
      key = lambda interval: interval.distance,
    )
   
  

class Interval:
  def __init__(self, sphere, numerator, denominator):
    self.sphere      = sphere

    self.numerator   = numerator
    self.denominator = denominator
    self.ratio = float(self.numerator) / self.denominator
    self.interval = self.sphere.interval(self.numerator, self.denominator)
    self.note = int(self.interval + 0.5)
    self.note_ratio = 2.0 ** (int(self.note) / float(self.sphere.base))
    self.distance = abs(self.interval - self.note)
    self.offset = (
      440.0 * self.note_ratio
    ) - (
      440.0 * self.ratio
    )

  def __str__(self):
    return "%i\t%i/%i\t%f\t%f" % (
      self.note, 
      self.numerator, 
      self.denominator, 
      self.interval, 
      self.offset
    )

import sys
base = int(sys.argv[1]) if len(sys.argv) > 1 else 24

bases = []
for b in range(2, base + 1):
  bases.append(Sphere(b))

bases.sort(key = lambda sphere: sphere.intervals.dissonance)

for s in bases:
  print("-" * 79)
  print("Base: %i" % s.base)
  print("Cycles: %i" % len(s.cycles))
  print("Dissnonance: %f" % s.intervals.dissonance)
  print()
  print("Note\tratio\tinterval\toffset")
  print(str(s.intervals))
