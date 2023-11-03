from octavox.core.model import SVNoteTrig, SVFXTrig

from octavox.core.pools import SVSample

from octavox.machines import Q

from octavox.machines.sequencers import SampleSequencer

import copy

class VitlingSequencer(SampleSequencer):
    
    @classmethod
    def initialise(self,
                  machine,
                  pool):
        samples=SampleSequencer.random_samples(pool=pool,
                                               tag=machine["params"]["tag"],
                                               n=machine["params"]["nsamples"])
        seeds={k:SampleSequencer.random_seed()
               for k in "sample|trig|pattern|volume".split("|")}
        return VitlingSequencer({"name": machine["name"],
                                 "class": machine["class"],
                                 "params": machine["params"],
                                 "samples": samples,
                                 "seeds": seeds})

    def __init__(self, machine):
        SampleSequencer.__init__(self, machine)
                            
    def clone(self):
        return VitlingSequencer({"name": self["name"],
                                 "class": self["class"],
                                 "params": copy.deepcopy(self["params"]),
                                 "samples": [sample.clone()
                                             for sample in self["samples"]],
                                 "seeds": dict(self["seeds"])})

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
            beatfn=getattr(self, pattern)
            beat=beatfn(q["trig"], i, self.density)
            if beat!=None: # NB explicit check
                volume=beat
                yield SVNoteTrig(mod=self["name"],
                                 sample=sample,
                                 vel=beat,
                                 i=i)

    """
    - https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
    """

    """
    - fourfloor scaled up to return 1.0 in base case (was 0.9)
    """
    
    def fourfloor(self, q, i, d):
        if i % 4 == 0 and q.random() < d:
            return 1.0
        elif i % 2 == 0 and q.random() < 0.1*d:
            return 0.6

    def electro(self, q, i, d):
        if i == 0 and q.random() < d:
            return 1
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5*d) or
              q.random() < 0.05*d):
            return 0.9*q.random()

    """ 
    - triplets added by me
    """
        
    def triplets(self, q, i, d):
        if i % 16  in [0, 3, 6, 9, 14] and q.random() < d:
            return 1

    def backbeat(self, q, i, d):
        if i % 8 == 4 and q.random() < d:
            return 1

    def skip(self, q, i, d):
        if i % 8 in [3, 6] and q.random() < d:
            return 0.6+0.4*q.random()
        elif i % 2 == 0 and q.random() < 0.2*d:
            return 0.4+0.2*q.random()
        elif q.random() < 0.1*d:
            return 0.2+0.2*q.random()

    """
    - offbeats simpified to return single sound only
    - offbeats and closed scaled up to return 2x original volume
    """
        
    def offbeats(self, q, i, d):
        if i % 4 == 2 and q.random() < d:
            return 0.8
        elif q.random() < 0.3*d:
            return 0.4*q.random()
    
    def closed(self, q, i, d):
        if i % 2 == 0 and q.random() < d:
            return 0.8
        elif q.random() < 0.5*d:
            return 0.6*q.random()
                
if __name__=="__main__":
    pass
