from octavox.modules.model import SVNoteTrig, SVFXTrig

from octavox.modules.pools import SVSample

from octavox.projects import Q

import random

class Sequencer(dict):
    
    @classmethod
    def randomise(self,
                  machine,
                  pool):
        return Sequencer({"name": machine["name"],                          
                          "class": machine["class"]})

    def __init__(self, machine):
        dict.__init__(self, {"name": machine["name"],
                             "class": machine["class"]})
                            
    def clone(self):
        return Sequencer({"name": self["name"],
                          "class": self["class"]})

    def render(self, nbeats, density):
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
