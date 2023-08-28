from octavox import load_yaml

from octavox.modules.model import SVNoteTrig, SVFXTrig

from octavox.modules.pools import SVSample

from octavox.projects import Q

import random

Patterns=load_yaml("projects/euclidbeats/patterns.yaml")

class Sequencer(dict):
    
    @classmethod
    def randomise(self,
                  machine,
                  pool,
                  patterns=Patterns):
        return Sequencer({"name": machine["name"],                          
                          "class": machine["class"],
                          "pattern": random.choice(patterns),
                          "sample": random.choice(pool.filter_tag(machine["params"]["tag"]))})

    def __init__(self, machine):
        dict.__init__(self, {"name": machine["name"],
                             "class": machine["class"],
                             "pattern" machine["pattern"],
                             "sample": machine["sample"]})
                            
    def clone(self):
        return Sequencer({"name": self["name"],
                          "class": self["class"],
                          "pattern": self["pattern"],
                          "sample": self["sample"]})

    def render(self, nbeats):
        q=Q(self["seed"])
        for i in range(nbeats):
            v=None
            if v!=None: # explicit because could return zero
                sample, volume = None, None
                yield SVNoteTrig(mod=self["name"],
                                 vel=volume,
                                 i=i,
                                 sample=sample)
    
if __name__=="__main__":
    pass
