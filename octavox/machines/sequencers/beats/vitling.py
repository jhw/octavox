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
    def random_pattern(self, q):
        return q["pattern"].choice(self.patterns)

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

    """
    - https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
    """
    
    def fourfloor(self, q, i, d, k="kk"):
        if i % 4 == 0 and q.random() < d:
            return (k, 0.9)
        elif i % 2 == 0 and q.random() < 0.1*d:
            return (k, 0.6)

    def electro(self, q, i, d, k="kk"):
        if i == 0 and q.random() < d:
            return (k, 1)
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5*d) or
              q.random() < 0.05*d):
            return (k, 0.9*q.random())

    """ 
    - added by me
    """
        
    def triplets(self, q, i, d, k="kk"):
        if i % 16  in [0, 3, 6, 9, 14] and q.random() < d:
            return (k, 1)

    def backbeat(self, q, i, d, k="sn"):
        if i % 8 == 4 and q.random() < d:
            return (k, 1)

    def skip(self, q, i, d, k="sn"):
        if i % 8 in [3, 6] and q.random() < d:
            return (k, 0.6+0.4*q.random())
        elif i % 2 == 0 and q.random() < 0.2*d:
            return (k, 0.4+0.2*q.random())
        elif q.random() < 0.1*d:
            return (k, 0.2+0.2*q.random())

    """
    - simpified to return single sound only
    """
        
    def offbeats(self, q, i, d, k="ht"):
        if i % 4 == 2 and q.random() < d:
            return (k, 0.4)
        elif q.random() < 0.3*d:
            return (k, 0.2*q.random())
    
    def closed(self, q, i, d, k="ht"):
        if i % 2 == 0 and q.random() < d:
            return (k, 0.4)
        elif q.random() < 0.5*d:
            return (k, 0.3*q.random())
                
if __name__=="__main__":
    pass
