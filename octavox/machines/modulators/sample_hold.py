from octavox.core.model import SVFXTrig

from octavox.machines import Q, random_seed

import copy

"""
- a Modulator uses params at runtime, hence they need to be part of state
- it's useful to unpack them at initialisation time
"""
        
class SampleHoldModulator(dict):
    
    @classmethod
    def initialise(self,
                  machine,
                  **kwargs):
        return SampleHoldModulator({"name": machine["name"],
                                    "class": machine["class"],
                                    "params": machine["params"],
                                    "seeds": {"level": random_seed()}})

    def __init__(self, machine):
        dict.__init__(self, machine)
        for k, v in machine["params"].items():
            setattr(self, k, v)

    def clone(self):
        return SampleHoldModulator({"name": self["name"],
                                    "class": self["class"],
                                    "params": copy.deepcopy(self["params"]),
                                    "seeds": dict(self["seeds"])})
                    
    def render(self, nticks, **kwargs):
        minval, maxval = (int(self.minvalue, 16),
                          int(self.maxvalue, 16))
        q=Q(self["seeds"]["level"])
        for i in range(nticks):
            v=self.sample_hold(q, i)
            if v!=None: # explicit because could return zero
                value=(v*maxval-minval)+minval
                yield SVFXTrig(target=self["name"],
                               value=value,
                               i=i)

    def sample_hold(self, q, i):
        if 0 == i % self.step:
            floor, ceil = self.range
            v=floor+(ceil-floor)*q.random()
            return self.increment*int(0.5+v/self.increment)

if __name__=="__main__":
    pass
