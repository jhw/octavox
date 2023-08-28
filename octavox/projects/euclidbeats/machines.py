from octavox import load_yaml

from octavox.modules.model import SVNoteTrig, SVFXTrig

from octavox.modules.pools import SVSample

from octavox.projects import Q

from octavox.projects.euclidbeats.bjorklund import bjorklund

import random

Patterns=load_yaml("projects/euclidbeats/patterns.yaml")

class Sequencer(dict):
    
    @classmethod
    def randomise(self,
                  machine,
                  pool,
                  patterns=Patterns):
        def random_sample(pool, tag):            
            samples=pool.filter_tag(tag)
            if samples==[]:
                samples=pool
            return random.choice(samples)
        def random_pattern(patterns=Patterns):
            return random.choice(patterns)
        def random_seed():
            return int(1e8*random.random())
        sample=random_sample(pool=pool,
                             tag=machine["params"]["tag"])
        return Sequencer({"name": machine["name"],                          
                          "class": machine["class"],
                          "pattern": random_pattern(),
                          "sample": sample,
                          "seed": random_seed()})

    def __init__(self, machine):
        dict.__init__(self, machine)
                            
    def clone(self):
        return Sequencer(self)

    def render(self, nbeats, density):
        notes=bjorklund(steps=self["pattern"][1],
                        pulses=self["pattern"][0])
        q=Q(self["seed"])
        for i in range(nbeats):
            note=notes[i % len(notes)]
            if q.random() < density and note: # 0|1
                volume=self.volume(q, i)
                yield SVNoteTrig(mod=self["name"],
                                 sample=self["sample"],
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
