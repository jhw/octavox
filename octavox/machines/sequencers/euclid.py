from octavox.core.model import SVNoteTrig, SVFXTrig

from octavox.core.pools import SVSample

from octavox.machines import Q, random_seed

from octavox.machines.sequencers import SampleSequencer, random_samples

import copy

"""
- https://raw.githubusercontent.com/brianhouse/bjorklund/master/__init__.py
"""

def bjorklund(steps, pulses, **kwargs):
    steps = int(steps)
    pulses = int(pulses)
    if pulses > steps:
        raise ValueError    
    pattern = []    
    counts = []
    remainders = []
    divisor = steps - pulses
    remainders.append(pulses)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level = level + 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)    
    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)         
        else:
            for i in range(0, counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)    
    build(level)
    i = pattern.index(1)
    pattern = pattern[i:] + pattern[0:i]
    return pattern
            
class EuclidSequencer(SampleSequencer):
    
    @classmethod
    def initialise(self,
                   machine,
                   pool):
        return EuclidSequencer({"name": machine["name"],
                                "class": machine["class"],
                                "params": machine["params"],
                                "samples": random_samples(pool=pool,
                                                          tag=machine["params"]["tag"],
                                                          n=machine["params"]["nsamples"]),
                                "seeds": {k:random_seed()
                                          for k in "sample|trig|pattern|volume".split("|")}})

    def __init__(self, machine):
        SampleSequencer.__init__(self, machine)
                            
    def clone(self):
        return EuclidSequencer({"name": self["name"],
                                "class": self["class"],
                                "params": copy.deepcopy(self["params"]),
                                "samples": [sample.clone()
                                            for sample in self["samples"]],
                                "seeds": dict(self["seeds"])})

    def random_pattern(self, q):
        pulses, steps = q["pattern"].choice(self.patterns)[:2] # because some of Tidal euclid rhythms have 3 parameters
        return bjorklund(pulses=pulses,
                         steps=steps)

    """
    - for the moment it's either/or in terms of sample/pattern switching
    """
    
    def render(self, nbeats, density):
        q={k:Q(v) for k, v in self["seeds"].items()}
        sample, pattern = (self.random_sample(q),
                           self.random_pattern(q))
        for i in range(nbeats):
            if self.switch_sample(q, i):
                sample=self.random_sample(q)
            elif self.switch_pattern(q, i):
                pattern=self.random_pattern(q)
            beat=bool(pattern[i % len(pattern)])
            if q["trig"].random() < (self.density*density) and beat:
                volume=self.volume(q["volume"], i)
                yield SVNoteTrig(mod=self["name"],
                                 sample=sample,
                                 vel=volume,
                                 i=i)

    def volume(self, q, i, n=5, var=0.1, drift=0.1):
        for j in range(n+1):
            k=2**(n-j)
            if 0 == i % k:
                sigma=q.gauss(0, var)
                return 1-max(0, min(1, j*drift+sigma))
                
if __name__=="__main__":
    pass
