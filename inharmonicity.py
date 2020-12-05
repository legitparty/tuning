# inharmonicity model
# http://daffy.uah.edu/piano/page4/page8/index.html

stretch_interval = ((1.5 ** 12) / (2.0 ** 7)) ** (1.0/7)
stretch_interval
1.0019377369015756

inharmonicity_coefficient_ratio = lambda harmonic, coeff: harmonic * (1.0 + 0.5 * (harmonic ** 2 - 1) * coeff)

stretch_coeff_2 = lambda stretch_interval: (stretch_interval - 1) / 1.5
inharmonicity_coefficient_2nd_harmonic = stretch_coeff_2(stretch_interval)
0.0012918246010504102
inharmonicity_coefficient_ratio(2, stretch_coeff_2(stretch_interval)) / 2
1.0019377369015756

stretch_coeff_3 = lambda stretch_interval: (stretch_interval - 1) / 4
inharmonicity_coefficient_3rd_harmonic = stretch_coeff_3(stretch_interval)
0.0004844342253939038
inharmonicity_coefficient_ratio(3, stretch_coeff_3(stretch_interval)) / 3
1.0019377369015756

pyth_n = lambda v, o: 7 * v - 12 * o
pyth_r = lambda v, o, stretch_interval: (1.5 ** v) / (2.0 * stretch_interval) ** o
pyth   = lambda v, o, stretch_interval: (pyth_n(v, o), pyth_r(v, o, stretch_interval))


def stretch_temperament(stretch_interval):
    return dict([
       pyth(0, 0, stretch_interval), # 0 C
       pyth(1, 0, stretch_interval), # 7 G
       pyth(2, 1, stretch_interval), # 2 D
       pyth(3, 1, stretch_interval), # 9 A
       pyth(4, 2, stretch_interval), # 4 E
       pyth(5, 2, stretch_interval), # 11 B
       pyth(6, 3, stretch_interval), # 6 F#
       pyth(7, 4, stretch_interval), # 1 C#
       pyth(8, 4, stretch_interval), # 8 G#
       pyth(9, 5, stretch_interval), # 3 D#
       pyth(10, 5, stretch_interval), # 10 A#
       pyth(11, 6, stretch_interval), # 5 F
    ])


