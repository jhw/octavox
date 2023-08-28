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
        # samples=pool.filter_tag(machine["params"]["tag"])
        samples=pool
        sample=random.choice(samples)
        # pattern=random.choice(patterns)
        pattern=[random.choice(range(1, 8)),
                 random.choice(range(8, 16))]
        seed=int(1e8*random.random()),
        return Sequencer({"name": machine["name"],                          
                          "class": machine["class"],
                          "pattern": pattern,
                          "sample": sample,
                          "seed": seed})

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
            if note: # 0|1
                volume=self.volume(q, i)
                yield SVNoteTrig(mod=self["name"],
                                 vel=volume,
                                 i=i,
                                 sample=self["sample"])

    def volume(self, q, i, n=5, var=0.1, inc=0.1):
        for j in range(n+1):
            k=2**(n-j)
            if 0 == i % k:
                decay=j*inc
                rand=q.gauss(0, var)
                return 1-max(0, min(1, decay+rand))
                
if __name__=="__main__":
    pass
