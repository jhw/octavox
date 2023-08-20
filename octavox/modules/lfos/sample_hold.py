from octavox.modules.model import SVFXTrig

from octavox.projects import Q

import random

"""
- a Modulator uses params at runtime, hence they need to be part of state
- it's useful to unpack them at initialisation time
"""
        
class SampleHoldModulator(dict):
    
    @classmethod
    def randomise(self,
                  machine,
                  **kwargs):
        return SampleHoldModulator({"name": machine["name"],
                                    "class": machine["class"],
                                    "params": machine["params"],
                                    "seed": int(1e8*random.random())})

    def __init__(self, machine):
        dict.__init__(self, machine)
        for k, v in machine["params"].items():
            setattr(self, k, v)

    def clone(self):
        return SampleHoldModulator(self)
                    
    def render(self, nbeats, density):
        q=Q(self["seed"])
        for i in range(nbeats):
            v=self.sample_hold(q, i, density)
            if v!=None: # explicit because could return zero
                yield SVFXTrig(target=self["name"],
                               value=v*self.multiplier,
                               i=i)

    def sample_hold(self, q, i, d):
        if 0 == i % self.step:
            if q.random() < self.live:
                floor, ceil = self.range
                v=floor+(ceil-floor)*q.random()
                return self.increment*int(0.5+v/self.increment)
            else:
                return 0.0

if __name__=="__main__":
    pass
