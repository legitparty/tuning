#!/usr/bin/env python

"""
Copyright Ben Woolley 2010.
All rights reserved.
"""

verbose = True

def errlog(s):
    import sys
    if verbose:
        sys.stderr.write(str(s) + "\n")
        sys.stderr.flush()

has_clipped = False
clipping = False
max_v = 1.0

def clipped(v):
    v = abs(v)
    global max_v, clipping, has_clipped
    if v > max_v:
        max_v = v
        clipping = True
    elif clipping:
        clipping = False
        errlog("New peak: " + str(max_v) + ", " + str(1.0/max_v))

        
    if not has_clipped:
        has_clipped = True
        errlog("Clipped!!!\n")



class Second:
    def __init__(self, second = 0.0):
        self.second = float(second)
        
    def set(self, second):
        self.second = float(second)
        
    def get(self):
        return self.second


def db_ratio(db):
    return 10 ** (float(db) / 10)


class Decay:

    def __init__(self, dbps, start_second):
        self.start_second = start_second
        errlog(self.start_second)
        self.dbps = dbps
        self.rate = db_ratio(dbps)
        self.sample_decay = None
        self.sample_volume = 0.0

    def decay(self, second, last_second = None):
        from math import log
        if last_second:
            if self.sample_decay:
                self.sample_volume *= self.sample_decay
                return self.sample_volume
            else:
                self.sample_volume = self.decay(second)
                self.sample_decay = self.decay(second) / self.decay(last_second)
                return self.sample_volume
        else:
            if self.rate != 1.0:
                try:
                    return log(self.rate) / (log(self.rate) * self.rate ** (second - self.start_second.get()))
                except OverflowError:
                    return 0.0
            else:
                return 1.0

class Fade:
    def __init__(self, start_second = None, end_second = None):
        self.start_second = start_second
        self.end_second = end_second or Second()
        
    def set_duration(self, second):
        self.end_second.set(self.start_second.get() + second)
        
    def fade_in(self, second):
        if self.start_second is None:
            return 1.0
        else:
            start = self.start_second.get()
            end = self.end_second.get()
            if second >= end:
                return 1.0
            elif second <= start:
                return 0.0
            else:
                return (second - start) / (end - start)           
        
    def fade_out(self, second):
        if self.start_second is None:
            return 1.0
        else:
            start = self.start_second.get()
            end = self.end_second.get()
            if second >= end:
                return 0.0
            elif second <= start:
                return 1.0
            else:
                return 1.0 - (second - start) / (end - start)           

class BasePartial:
    # public
    
    def frequency(self, second):
        "stub input"
        
        return 0

    def value(self, second, nyquist):
        "result output"
        
        frequency = self.frequency(second)
        return self.wave(second, frequency, self.volume(second, frequency, nyquist)) 

    class Releasing: pass
    class Attacking: pass
    class Reattacking: pass
    class Lifted: pass
    class Pressed: pass

    def __init__(self, intensity = 1.0, decay_rate = 0.0, delay = 0.0, release_floor_db = None):
        from collections import deque
        # public state
        self.ref_count = 1
        self.pending_attack = True
        self.pending_release = False
        self.delay = delay
        self.state = self.Lifted
        
        self.decay_rate = decay_rate
        self.sustain = None
        self.attack_fade = None
        self.release_fade = None
        self.hit_floor = False

        # static properties
        self.intensity = intensity
        if not release_floor_db:
            from math import log
            depth = 16
            release_floor_db = -(log(2 ** (2 * depth)) / log(10)) * 10
        self.floor = db_ratio(release_floor_db)

        # private state
        self.last_cycle = 0.0
        self.last_second = 0.0

    # private

    def lift(self):
        errlog("lift %s %s" % (id(self), self.state))
        self.pending_release = True
        self.ref_count -= 1

    def unlift(self):
        errlog("unlift %s %s" % (id(self), self.state))
        self.pending_attack = True
        self.ref_count += 1

    def actuate(self, frequency, second):
        from collections import deque
        has_attack  = self.pending_attack
        self.pending_attack = False
        has_release = self.pending_release
        self.pending_release = False

        if self.ref_count > 0:
            if has_attack:
                if self.state is self.Lifted:
                    self.hammer_down(frequency, second)
                elif self.state is self.Pressed:
                    self.hammer_up(frequency, second)
                    self.state = self.Reattacking
                elif self.state is self.Releasing:
                    self.state = self.Reattacking
                # else is already attacking
            else:
                if self.state is self.Lifted:
                    # should at least be attacked
                    self.hammer_down(frequency, second)
                # else let hammer actions continue

        elif self.ref_count <= 0:
            if has_release:
                if self.state is self.Pressed:
                    self.hammer_up(frequency, second)
                elif self.state is self.Reattacking:
                    self.state = self.Releasing
                # self.Lifted and self.Releasing are already releasing or released
            else:
                if self.state is self.Pressed:
                    # should at least be released
                    self.hammer_up(frequency, second)
                # else let hammer actions continue

    def hammer_up(self, frequency, second):
        self.state = self.Releasing
        errlog("hammer_up %s %s %s %s" % (frequency, second, id(self), self.state))
        
        self.release_fade = Fade(Second(second + self.delay), Second(second + self.delay + 5.0 / frequency))

    def hammer_down(self, frequency, second):
        self.state = self.Attacking
        errlog("hammer_down %s %s %s %s" % (frequency, second, id(self), self.state))
        
        self.attack_fade = Fade(Second(second + self.delay), Second(second + self.delay + 5.0 / frequency))
        self.sustain = Decay(self.decay_rate, Second(second + self.delay + 1.0 / frequency))
        
    def force(self, frequency, second):
        self.actuate(frequency, second)
    
        if self.state is self.Lifted:
            self.last_cycle = 0
            self.last_second = second
            return 0.0
        elif self.state is self.Pressed:
            return 1.0
        elif self.state is self.Attacking:
            return self.attack(frequency, second)
        elif self.state is self.Releasing:
            return self.release(frequency, second)
        elif self.state is self.Reattacking:
            return self.release(frequency, second)

        
    def attack(self, frequency, second):    
        v = self.attack_fade.fade_in(second)
        if v == 1.0:
            errlog(self.state)
            self.state = self.Pressed
            errlog("pressed %s %s %s %s" % (frequency, second, id(self), self.state))
        return v

    def release(self, frequency, second):            
        v = self.release_fade.fade_out(second)
        if v == 0.0:
            errlog(self.state)
            if self.state is self.Reattacking:
                self.hammer_down(frequency, second)
                errlog("reattacking %s %s %s %s" % (frequency, second, id(self), self.state))
            else:
                self.state = self.Lifted
                errlog("lifted %s %s %s %s" % (frequency, second, id(self), self.state))
                self.last_cycle = 0
                self.last_second = second
        return v

    def cycle(self, second, frequency):
        cycle = self.last_cycle + (second - self.last_second) * frequency
        self.last_cycle = cycle
        self.last_second = second
        return cycle

    def wave(self, second, frequency, volume):
        from math import sin, pi
        
        if volume > self.floor:
            return sin(pi * 2 * self.cycle(second, frequency)) * volume
        else:
            if not self.hit_floor:
                errlog("Dropping partial that hit the floor.")
                self.hit_floor = True
            return 0.0

    def volume(self, second, frequency, nyquist):
        if frequency <= nyquist:
            return self.intensity * self.force(frequency, second) * (self.sustain.decay(second) if self.sustain is not None else 1.0)
        else:
            return 0.0
                

class BaseTone:
    def sum_values(self, second, nyquist):
        v = sum(p.value(second, nyquist) for p in self.partials)
        if v > 1.0:
            clipped(v)
            v = 1.0

        if v < -1.0:
            clipped(v)
            v = -1.0
            
        return v


class BaseSampler:
    def __init__(self, sample_rate = 48000, sample_depth = 16, sample_packing = "h"):
        self.rate = sample_rate
        self.depth = sample_depth
        self.packing = sample_packing
        
        self.nyquist = self.rate / 2
        self.cardinality = 1 << self.depth
        self.bytes = self.depth / 8

    def signed_sample(self, i):
        return int(((self.sum_values(float(i) / self.rate, self.nyquist) + 1) / 2 * (self.cardinality - 1) - (self.cardinality / 2)) + .5)
        
    def sample(self, i):
        import struct
        return struct.pack(self.packing, self.signed_sample(i))
        
class SimplePartial(BasePartial):
    def __init__(self, f, h, v = 1.0, db = 0.0, delay = 0.0):
        if db > 30: db = 30
        #errlog(db)
        BasePartial.__init__(self, v, db, delay)
        self.base_frequency = f
        self.harmonic = h
        
    def updateBaseFrequency(self, f):
        self.base_frequency = f
        
    def updatePan(self, p):
        self.pan = p

    def frequency(self, second):
        return self.base_frequency * self.harmonic

class SquareWave(SimplePartial):
    def wave(self, second, frequency, volume):
        from math import floor
        if volume > 0.0:
            t = self.cycle(second, frequency)
            on = int(t * 2) % 2 == 0
            return volume if on else -volume
        else:
            self.cycle(second, frequency)
            return 0.0

class TriangleWave(SimplePartial):
    def wave(self, second, frequency, volume):
        from math import floor
        if volume > 0.0:
            # not yet implemented -- still a square wave
            t = self.cycle(second, frequency)
            on = int(t * 2) % 2 == 0
            return volume if on else -volume
        else:
            self.cycle(second, frequency)
            return 0.0

class SawtoothWave(SimplePartial):
    def wave(self, second, frequency, volume):
        from math import floor
        if volume > 0.0:
            t = self.cycle(second, frequency)
            return 2.0 * (t - floor(t + 0.5)) * volume
        else:
            self.cycle(second, frequency)
            return 0.0

class SynthProperties:
    def __init__(self, frequency = 256.0, channel_pan = 0.0, attack_volume = 1.0, channel_volume = 1.0):
        self.octave_gain = -0.0

        self.channel_pan = channel_pan
        self.attack_volume = attack_volume
        self.channel_volume = channel_volume
    
       	""""""
        self.odd_only = False
        self.initial_gain = 1.0 / 10
        self.enharmonic_width = 0.02 # 2 cm at 512

        self.max_harmonic = 12
        self.inharmonicity = (frequency - 4) / frequency
        
        self.plucked_harmonic = 7.0
        self.pluck_dampening = 1.0

        self.decay_db = 2.0
        self.harmonic_decay_db = 1.0/4
        self.harmonic_decay_dampening = 4.0
        """
        self.odd_only = True
        self.initial_gain = 1.0 / 5000

        self.enharmonic_width = 0.0
        
        self.max_harmonic = 8
        self.inharmonicity = 0.0

        self.plucked_harmonic = 1000.0
        self.pluck_dampening = 1.0

        self.decay_db = 0.0
        self.harmonic_decay_db = 0.0
        self.harmonic_decay_dampening = 1.5
        """

	self.octave_modulo = False

        self.octave_width = 0.165

        self.frequency_x = 256.0

        from math import log
        self.octave_position = (log(float(frequency) / self.frequency_x) / log(2))

	if self.octave_modulo:
		from math import floor
        	self.attack_dampening = 1 + floor(self.octave_position) / 6
	else:
	        self.attack_dampening = 1 + self.octave_position / 6

        self.gain = self.initial_gain * db_ratio(self.octave_gain * self.octave_position)

        self.position_x = self.octave_position * self.octave_width + self.channel_pan * 4 # meters
        self.position_y = 0.2 # meters
        
        self.ear_distance = 0.02 # meters
        
        self.sound_speed = 343.174 # meters per second
        
        self.left_distance  = ((self.position_x - self.ear_distance / 2) ** 2 + self.position_y ** 2) ** 0.5
        self.right_distance = ((self.position_x + self.ear_distance / 2) ** 2 + self.position_y ** 2) ** 0.5       
        
        self.left_delay  = self.left_distance  / self.sound_speed
        self.right_delay = self.right_distance / self.sound_speed
	    
	self.left_intensity  = 1.0 / self.left_distance  ** 2
	self.right_intensity = 1.0 / self.right_distance ** 2
	
        from math import atan, pi
        self.pan_position = atan(self.octave_position / 20) / pi * 2
        self.left_pan, self.right_pan = self.pan(self.pan_position)

	#self.left_pan  = self.left_pan * self.left_intensity  / 20
	#self.right_pan = self.right_pan * self.right_intensity / 20    
        
        if self.plucked_harmonic:
            # pluck dampening
            self.plucked_volumes = [
                (harmonic, ((self.plucked_harmonic - harmonic) / self.plucked_harmonic) ** self.pluck_dampening)
                for harmonic
                in range(1, int(self.plucked_harmonic))
            ]
        else:
            self.plucked_volumes = [(1000000, 1.0)]
        
    def pan(self, p):
        from math import log, cos, sin, pi
        if p >  1.0: p =  1.0
        if p < -1.0: p = -1.0
        
        if p == -1.0:
            left  = 0.0
            right = 1.0
        else:
            left  = 10.0 ** (2.0 * log(cos(pi * (float(p) / 2 + .5) / 2)))
            right = 10.0 ** (2.0 * log(sin(pi * (float(p) / 2 + .5) / 2)))
            
        return (left, right) 
        
    def harmonic_volume(self, harmonic):
        if self.max_harmonic and harmonic > self.max_harmonic:
            return 0.0
	    
	if self.odd_only and harmonic % 2 != 1:
		return 0.0
	    
        return (
            self.gain
                # attack
                / (harmonic ** self.attack_dampening)
                # pluck dampening
                * sum(tv for th, tv in self.plucked_volumes if harmonic % th)
                # open pipe
                # * ((3 - (harmonic % 2 + 1)) * 1)
        )
    
    def harmonic_decay(self, harmonic):
        return self.decay_db + self.harmonic_decay_db * harmonic * (harmonic ** self.harmonic_decay_dampening)
                
class SynthTone(BaseTone):
    synth_id = 0
    
    def updateFrequency(self, f):
        if f != self.frequency:
            for partial in self.partials:
                #if not partial.state is partial.Pressed:
                partial.updateBaseFrequency(f)

    def updatePan(self, p):
        if p != self.pan:
            for partial in self.partials:
                #if not partial.state is partial.Pressed:
                partial.updatePan(f)
            
    def release(self, end = None):
        for partial in self.partials:
            partial.lift()
            
    def unrelease(self):
        for partial in self.partials:
            partial.unlift()

    def finished(self):
        return self.partials[0].state is BasePartial.Lifted

    def remove(self):
        self.sampler.remove(self)
    
    def __init__(self, sampler, frequency, nyquist, channel, pan = 0.0, start = None, stop = None, properties = None):
        self.sampler = sampler
        self.id = self.synth_id
        SynthTone.synth_id += 1
        
        self.frequency = frequency
        self.pan = pan
        self.nyquist = nyquist
        self.start = start
        self.stop = stop
        self.properties = properties if properties else SynthProperties(frequency, self.pan)
        self.delay = {
            0: self.properties.left_delay,
            1: self.properties.right_delay,
        }[channel]
        self.pan = {
            0: self.properties.left_pan,
            1: self.properties.right_pan,
        }[channel]
        
        self.init_partials()
        
    def init_partials(self):
        self.partials = []
        
        volume = 0.0
        max_partials = int(float(self.nyquist) / self.frequency)
        for harmonic in range(1, max_partials):
            harmonic_frequency = self.frequency * harmonic
            if harmonic % 2 == 0:
                harmonic_frequency -= self.frequency * self.properties.inharmonicity
            
            if harmonic_frequency > self.nyquist:
                break
                
            harmonic_volume = self.properties.harmonic_volume(harmonic) * self.pan
            if harmonic_volume == 0.0:
                continue
                
            volume += harmonic_volume
            
            harmonic_decay = self.properties.harmonic_decay(harmonic)
            errlog("SimplePartial(%s, %s, %s, %s, %s)" % (self.frequency, harmonic, harmonic_volume, harmonic_decay, self.delay)) 
            self.partials.append(SimplePartial(self.frequency, harmonic, harmonic_volume, harmonic_decay, self.delay))
            
class SynthSampler(BaseSampler):
    def __init__(self, channel = 0, sample_rate = 48000, sample_depth = 16, sample_packing = "h"):
        BaseSampler.__init__(self, sample_rate, sample_depth, sample_packing)
        self.channel = channel
        self.tones = {}

    def newTone(self, frequency, pan, start, stop = None, properties = None):
        tone = SynthTone(self, frequency, self.nyquist, self.channel, pan, start, stop, properties)
        self.tones[tone.id] = tone
        return tone
        
    def remove(self, tone):
        if tone.id in self.tones:
            del self.tones[tone.id]
        
    def sum_values(self, seconds, nyquist):
        if self.tones:
            #errlog(sorted(tone.frequency for tone in self.tones.values()))
            v = sum(tone.sum_values(seconds, nyquist) for tone in self.tones.values())
            if v > 1.0:
                clipped(v)
                v = 1.0

            if v < -1.0:
                clipped(v)
                v = -1.0
                
            return v
        else:
            return 0.0

