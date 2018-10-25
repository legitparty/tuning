#!/usr/bin/env python

from midilib import *

class SampleProgress:
    def __init__(self, sample_rate, channel, second_width = 0.1):
        self.sample_rate = sample_rate
        self.second_width = second_width
        self.sample_pos = 0
        self.second_pos = 0.0
        self.channel = channel
        
    def inc(self):
        self.sample_pos += 1
        #errlog(self.sample_pos)
        
        second_pos = float(self.sample_pos) / self.sample_rate
        if second_pos > self.second_pos + self.second_width:
            self.second_pos = int(second_pos / self.second_width) * self.second_width
            errlog("Generated %.1f seconds on channel %i." % (self.second_pos, self.channel))

def perform(q, filename, sample_rate, sample_depth, sample_packing, channel):

    p = SampleProgress(sample_rate, channel, 0.1)

    
    sampler = SynthSampler(channel, sample_rate, sample_depth, sample_packing)
    zero_sample = sampler.packing.pack(0)
    channels = Channels(filename, sampler)

    i = 0
    while True:
        channels.updateTime(float(i) / sample_rate)
        sample = sampler.sample(i)
        q.put(sample)
        p.inc()
        if not channels.remaining() and not sampler.remaining() and sample == zero_sample:
            break

        i += 1

    q.put(None)
    
    while True:
        q.put(zero_sample)
        p.inc()

if __name__ == '__main__':
    import sys
    midifile = sys.argv[1]
    wavfile = sys.argv[2]
    
    sample_rate = 44100
    #sample_rate = 8000
    #sample_rate = 96000
    sample_depth = 16
    #sample_depth = 32
    sample_packing = "h"
    #sample_packing = "i"

    from multiprocessing import Process, Queue
    from collections import deque
    from midilib import errlog
    from struct import Struct

    left_q = Queue()
    right_q = Queue()

    left_process =  Process(target=perform, args=(left_q, midifile, sample_rate, sample_depth, sample_packing, 0))
    right_process = Process(target=perform, args=(right_q, midifile, sample_rate, sample_depth, sample_packing, 1))
    
    try:
        left_process.start()
        right_process.start()

        out = open(wavfile + ".raw", "wb")
        
        i = 0
        left_finished = False
        right_finished = False
        
        left, right = left_q.get(), right_q.get()
        while not left_finished or not right_finished:
            if left is None:
                left_finished = True
                left = left_q.get()
            
            if right is None:
                right_finished = True
                right = right_q.get()
                    
            out.write(left + right)
            if i % 8192 == 0:
                out.flush()
                errlog("i = %i" % i)
                
            i += 1
            left, right = left_q.get(), right_q.get()
            
        errlog("%r" % ([left, right]))
        out.flush()
        errlog("i = %i" % i)
        out.close()
    except KeyboardInterrupt:
        left_process.terminate()
        right_process.terminate()
    finally:
        left_process.terminate()
        right_process.terminate()
        left_process.join()
        right_process.join()

