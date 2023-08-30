from octavox import load_yaml

from octavox.modules.model import SVNoteTrig, SVFXTrig

from octavox.modules.pools import SVSample

from octavox.projects import Q

from octavox.projects.euclidbeats.bjorklund import bjorklund

import random

Patterns=load_yaml("projects/euclidbeats/patterns.yaml")

NSamples=4

class Sequencer(dict):
    
    @classmethod
    def randomise(self,
                  machine,
                  pool,
                  patterns=Patterns):
        def random_samples(pool, tag, n=NSamples):            
            samples=pool.filter_tag(tag)
            if samples==[]:
                samples=pool
            return [random.choice(samples)
                    for i in range(n)]
        def random_pattern(patterns=Patterns):
            return random.choice(patterns)
        def random_seed():
            return int(1e8*random.random())
        samples=random_samples(pool=pool,
                               tag=machine["params"]["tag"])
        seeds={"note": random_seed(),
               "trig": random_seed(),
               "volume": random_seed()}
        return Sequencer({"name": machine["name"],                          
                          "class": machine["class"],
                          "params": machine["params"],
                          "pattern": random_pattern(),
                          "samples": samples,
                          "seeds": seeds})

    def __init__(self, machine):
        dict.__init__(self, machine)
        for k, v in machine["params"].items():
            setattr(self, k, v)
                            
    def clone(self):
        return Sequencer(self)

    def render(self, nbeats, density):
        q={k:Q(v) for k, v in self["seeds"].items()}
        sample=q["note"].choice(self["samples"])
        notes=bjorklund(pulses=self["pattern"][0],
                        steps=self["pattern"][1])
        for i in range(nbeats):
            if (0 == i % self.modulation["note"]["step"] and
                q["trig"].random() < self.modulation["note"]["threshold"]):
                sample=q["note"].choice(self["samples"])
            note=notes[i % len(notes)]
            if q["trig"].random() < density and note: # 0|1
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
