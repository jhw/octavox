from octavox.modules.model import SVSample, SVNoteTrig, SVFXTrig

from octavox.projects import Q

import random

Patterns=["0",
          "0|0|1|0",
          "3x0|1",
          "0|1|0|1",
          "0|1|0|2"]

class Pattern(str):

    @classmethod
    def randomise(self, temperature, patterns=Patterns):
        n=1+int(temperature*len(patterns))
        return Pattern(random.choice(patterns[:n]))
    
    def __init__(self, value):
        str.__init__(value) # NB no self as first arg

    @property
    def expanded(self):
        def parse_chunk(chunk):
            tokens=[int(tok)
                    for tok in chunk.split("x")]
            if len(tokens)==1:
                tokens=[1, tokens[0]]
            return {k:v for k, v in zip("ni", tokens)}
        return [parse_chunk(chunk)
                for chunk in self.split("|")]
        
    @property
    def size(self):
        return sum([item["n"]
                    for item in self.expanded])

"""
- tempting to thing that Samples could be an instance of SVPool
- but key differences are that it needs serialising to/from JSON and has its own core logic in the form of randomise() and tagged_map()
"""
    
class Samples(list):

    @classmethod
    def randomise(self,
                  i,
                  tag,
                  pool,
                  fixes,
                  mapping={"kk": ["kk"],
                           "sn": ["sn"],
                           "ht": ["oh", "ch"]}):
        samples=[]
        if tag not in mapping:
            raise RuntimeError("tag %s not found in mapping" % tag)
        for childtag in mapping[tag]:
            filtered=fixes.filter(childtag).samples
            if i==0 and filtered!=[]:
                values=filtered
            else:
                filtered=pool.filter(childtag).samples
                values=filtered if filtered!=[] else pool.samples
            sample=random.choice(values).clone()
            sample["tags"]=[childtag] # NB override tags as may come from pool.samples
            samples.append(sample)
        return Samples(samples)
            
    def __init__(self, items=[]):
        list.__init__(self, [SVSample(item)
                             for item in items])

    def clone(self):
        return Samples(self)

    @property
    def tagged_map(self):
        samples={}
        for sample in self:
            for tag in sample["tags"]:
                samples[tag]=sample
        return samples

class Slice(dict):

    @classmethod
    def randomise(self,
                  i,
                  params,
                  pool,
                  fixes):
        samples=Samples.randomise(i=i,
                                  tag=params["tag"],
                                  pool=pool,
                                  fixes=fixes)
        return Slice(samples=samples,
                     seed=int(1e8*random.random()),
                     style=random.choice(params["styles"]))
    
    def __init__(self,
                 samples,
                 seed,
                 style):
        dict.__init__(self, {"samples": Samples(samples),
                             "seed": seed,
                             "style": style})

    def clone(self):
        return Slice(samples=self["samples"].clone(),
                     seed=self["seed"],
                     style=self["style"])

class Slices(list):

    @classmethod
    def randomise(self,
                  params,
                  pool,
                  fixes,
                  n=3):
        return Slices([Slice.randomise(i=i,
                                       params=params,
                                       pool=pool,
                                       fixes=fixes)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])

    def clone(self):
        return Slices(self)

"""
- a Sequencer (currently) only uses params at patch initialisation time (randomise), hence they don't need to be saved in state
"""
    
class Sequencer(dict):
    
    @classmethod
    def randomise(self,
                  machine,
                  temperature,
                  pool,
                  fixes):
        slices=Slices.randomise(params=machine["params"],
                                pool=pool,
                                fixes=fixes)
        return Sequencer({"name": machine["name"],                          
                          "class": machine["class"],
                          "pattern": Pattern.randomise(temperature),
                          "slices": slices})

    def __init__(self, machine):
        dict.__init__(self, {"name": machine["name"],
                             "class": machine["class"],
                             "pattern": Pattern(machine["pattern"]),
                             "slices": Slices(machine["slices"])})
                            
    def clone(self):
        return Sequencer({"name": self["name"],
                          "class": self["class"],
                          "pattern": self["pattern"],
                          "slices": self["slices"].clone()})

    def render(self,
               nbeats,
               density):
        multiplier, offset = int(nbeats/self["pattern"].size), 0
        for pat in self["pattern"].expanded:
            slice=self["slices"][pat["i"]]
            q=Q(slice["seed"])            
            fn=getattr(self, slice["style"])
            nsamplebeats=pat["n"]*multiplier
            samples=slice["samples"].tagged_map
            for i in range(nsamplebeats):
                v=fn(q, i, density)
                if v!=None: # explicit because could return zero
                    tag, volume = v
                    sample=samples[tag].clone()
                    yield SVNoteTrig(mod=self["name"],
                                     vel=volume,
                                     i=i+offset,
                                     sample=sample)
            offset+=nsamplebeats

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

    def offbeats(self, q, i, d, k=["oh", "ch"]):
        if i % 4 == 2 and q.random() < d:
            return (k[0], 0.4)
        elif q.random() < 0.3*d:
            k = k[0] if q.random() < 0.5 else k[1]
            return (k, 0.2*q.random())
    
    def closed(self, q, i, d, k="ch"):
        if i % 2 == 0 and q.random() < d:
            return (k, 0.4)
        elif q.random() < 0.5*d:
            return (k, 0.3*q.random())

if __name__=="__main__":
    pass
