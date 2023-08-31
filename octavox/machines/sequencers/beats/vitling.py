from octavox.core.model import SVNoteTrig, SVFXTrig

from octavox.core.pools import SVSample

from octavox.machines.sequencers.beats import BeatSequencer, mean_revert

from octavox.projects import Q

import yaml

NSamples=4

class VitlingSequencer(BeatSequencer):
    
    @classmethod
    def randomise(self,
                  machine,
                  pool,
                  n=NSamples):
        samples=BeatSequencer.random_samples(pool=pool,
                                             tag=machine["params"]["tag"],
                                             n=n)
        seeds={k:BeatSequencer.random_seed()
               for k in "note|trig|pattern|volume".split("|")}
        return VitlingSequencer({"name": machine["name"],
                                "class": machine["class"],
                                "params": machine["params"],
                                "samples": samples,
                                "seeds": seeds})

    def __init__(self, machine):
        BeatSequencer.__init__(self, machine)
                            
    def clone(self):
        return VitlingSequencer(self)

    @mean_revert(attr="patterns",
                 qattr="trig",
                 modattr="pattern")
    def random_pattern(self, q,
                       patterns=Patterns):
        return bjorklund(**q["pattern"].choice(patterns))

    """
    - for the moment it's either/or in terms of sample/pattern switching
    """
    
    def render(self, nbeats):
        q={k:Q(v) for k, v in self["seeds"].items()}
        sample, pattern = (self.random_sample(q),
                           self.random_pattern(q))
        for i in range(nbeats):
            if self.switch_sample(q, i):
                sample=self.random_sample(q)
            elif self.switch_pattern(q, i):
                pattern=self.random_pattern(q)
            beat=bool(pattern[i % len(pattern)])
            if q["trig"].random() < self.density and beat:
                volume=self.volume(q["volume"], i)
                yield SVNoteTrig(mod=self["name"],
                                 sample=sample,
                                 vel=volume,
                                 i=i)

if __name__=="__main__":
    pass
