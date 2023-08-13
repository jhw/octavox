from octavox.modules.banks import SVSampleKey

from octavox.modules.project import SVProject, SVTrigs, SVNoteTrig, SVFXTrig

from octavox.projects import Q

import random, yaml

SeqConfig=yaml.safe_load("""
- name: KickSampler
  tag: kk
  styles:
  - fourfloor
  - electro
  - triplets
- name: SnareSampler
  tag: sn
  styles:
  - backbeat
  - skip
- name: HatSampler
  tag: ht
  styles:
  - offbeats
  - closed
""")

LfoConfig=yaml.safe_load("""
- name: Echo/wet
  style: sample_hold
  range: [0, 1]
  increment: 0.25
  step: 4
  live: 0.66666
  multiplier: 32768
- name: Echo/feedback
  style: sample_hold
  range: [0, 1]
  increment: 0.25
  step: 4
  live: 1.0
  multiplier: 32768
""")

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
            filtered=fixes.filter(childtag).samplekeys
            if i==0 and filtered!=[]:
                values=filtered
            else:
                filtered=pool.filter(childtag).samplekeys
                values=filtered if filtered!=[] else pool.samplekeys
            sample=random.choice(values)
            samples.append(sample)
        return Samples(samples)
            
    def __init__(self, items=[]):
        list.__init__(self, [SVSampleKey(item)
                             for item in items])

    def clone(self):
        return Samples(self)

    @property
    def tagged_map(self):
        samples={}
        for samplekey in self:
            for tag in samplekey["tags"]:
                samples[tag]=samplekey
        return samples

class Slice(dict):

    @classmethod
    def randomise(self,
                  i,
                  tag,
                  pool,
                  fixes,
                  config={item["tag"]:item
                          for item in SeqConfig}):
        return Slice(samples=Samples.randomise(i=i,
                                               tag=tag,
                                               pool=pool,
                                               fixes=fixes),
                     seed=int(1e8*random.random()),
                     style=random.choice(config[tag]["styles"]))
    
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
                  tag,
                  pool,
                  fixes,
                  n=3):
        return Slices([Slice.randomise(i=i,
                                       tag=tag,
                                       pool=pool,
                                       fixes=fixes)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])

    def clone(self):
        return Slices(self)

class Sequencer(dict):
    
    @classmethod
    def randomise(self,
                  item,
                  temperature,
                  pool,
                  fixes):
        return Sequencer({"name": item["name"],
                          "pattern": Pattern.randomise(temperature),
                          "slices": Slices.randomise(tag=item["tag"],
                                                     pool=pool,
                                                     fixes=fixes)})

    def __init__(self, item,
                 config={item["name"]:item
                         for item in SeqConfig}):
        dict.__init__(self, {"name": item["name"],
                             "pattern": Pattern(item["pattern"]),
                             "slices": Slices(item["slices"])})
        params=config[item["name"]]
        for attr in params:
            setattr(self, attr, params[attr])
                            
    def clone(self):
        return Sequencer({"name": self["name"],
                          "pattern": self["pattern"],
                          "slices": self["slices"].clone()})

    @property
    def mod(self):
        return self["name"]
    
    def render(self,
               trigs,
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
                fn(q, i, density, trigs, offset, samples)
            offset+=nsamplebeats

    def apply(fn):
        def wrapped(self, q, i, d,
                    trigs,
                    offset,
                    samples):
            v=fn(self, q, i, d, trigs, offset, samples)
            if v!=None: # explicit because could return zero
                tag, volume = v
                samplekey=samples[tag].clone()
                trig=SVNoteTrig(mod=self.mod,
                                vel=volume,
                                i=i+offset,
                                samplekey=samplekey)
                trigs.append(trig)
        return wrapped

    """
    - https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
    """
    
    @apply
    def fourfloor(self, q, i, d, *args, k="kk"):
        if i % 4 == 0 and q.random() < d:
            return (k, 0.9)
        elif i % 2 == 0 and q.random() < 0.1*d:
            return (k, 0.6)

    @apply
    def electro(self, q, i, d, *args, k="kk"):
        if i == 0 and q.random() < d:
            return (k, 1)
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5*d) or
              q.random() < 0.05*d):
            return (k, 0.9*q.random())

    @apply
    def triplets(self, q, i, d, *args, k="kk"):
        if i % 16  in [0, 3, 6, 9, 14] and q.random() < d:
            return (k, 1)

    @apply
    def backbeat(self, q, i, d, *args, k="sn"):
        if i % 8 == 4 and q.random() < d:
            return (k, 1)

    @apply
    def skip(self, q, i, d, *args, k="sn"):
        if i % 8 in [3, 6] and q.random() < d:
            return (k, 0.6+0.4*q.random())
        elif i % 2 == 0 and q.random() < 0.2*d:
            return (k, 0.4+0.2*q.random())
        elif q.random() < 0.1*d:
            return (k, 0.2+0.2*q.random())

    @apply
    def offbeats(self, q, i, d, *args, k=["oh", "ch"]):
        if i % 4 == 2 and q.random() < d:
            return (k[0], 0.4)
        elif q.random() < 0.3*d:
            k = k[0] if q.random() < 0.5 else k[1]
            return (k, 0.2*q.random())
    
    @apply
    def closed(self, q, i, d, *args, k="ch"):
        if i % 2 == 0 and q.random() < d:
            return (k, 0.4)
        elif q.random() < 0.5*d:
            return (k, 0.3*q.random())
                            
class Sequencers(list):
    
    @classmethod
    def randomise(self,
                  pool,
                  fixes,
                  temperature,
                  config=SeqConfig):
        return Sequencers([Sequencer.randomise(item=item,
                                               pool=pool,
                                               fixes=fixes,
                                               temperature=temperature)
                          for item in config])

    def __init__(self, sequencers):
        list.__init__(self, [Sequencer(seq)
                             for seq in sequencers])

    def clone(self):
        return Sequencers([seq.clone()
                           for seq in self])

class Lfo(dict):
    
    @classmethod
    def randomise(self, item):
        return Lfo({"name": item["name"],
                    "seed": int(1e8*random.random())})

    def __init__(self, item,
                 config={item["name"]:item
                         for item in LfoConfig}):
        dict.__init__(self, item)
        params=config[item["name"]]
        for attr in params:
            setattr(self, attr, params[attr])

    def clone(self):
        return Lfo(self)
                    
    @property
    def mod(self):
        return self["name"].split("/")[0]

    @property
    def ctrl(self):
        return self["name"].split("/")[1]
            
    def render(self, nbeats, density, trigs):
        q=Q(self["seed"])
        for i in range(nbeats):
            fn=getattr(self, self.style)
            fn(q, i, density, trigs)

    def apply(fn):
        def wrapped(self, q, i, d, trigs):
            v=fn(self, q, i, d, trigs)
            if v!=None: # explicit because could return zero
                trig=SVFXTrig(mod=self.mod,
                              ctrl=self.ctrl,
                              value=v*self.multiplier,
                              i=i)
                trigs.append(trig)
        return wrapped

    @apply
    def sample_hold(self, q, i, d, *args):
        if 0 == i % self.step:
            if q.random() < self.live:
                floor, ceil = self.range
                v=floor+(ceil-floor)*q.random()
                return self.increment*int(0.5+v/self.increment)
            else:
                return 0.0
                
class Lfos(list):

    @classmethod
    def randomise(self, config=LfoConfig):
        return Lfos([Lfo.randomise(item)
                     for item in config])

    def __init__(self, lfos):
        list.__init__(self, [Lfo(lfo)
                             for lfo in lfos])

    def clone(self):
        return Lfos([lfo.clone()
                     for lfo in self])

class Patch(dict):

    @classmethod
    def randomise(self, pool, fixes, temperature, density):
        return Patch(sequencers=Sequencers.randomise(pool=pool,
                                                     fixes=fixes,
                                                     temperature=temperature),
                     lfos=Lfos.randomise(),
                     density=density)
        
    def __init__(self,
                 sequencers,
                 lfos,
                 density):
        dict.__init__(self, {"sequencers": Sequencers(sequencers),
                             "lfos": Lfos(lfos),
                             "density": density})
        
    def clone(self):
        return Patch(sequencers=self["sequencers"].clone(),
                     lfos=self["lfos"].clone(),
                     density=self["density"])
    
    def render(self,
               nbeats,
               mutes=[]):
        trigs=SVTrigs(nbeats=nbeats)
        for seq in self["sequencers"]:
            if seq["name"] not in mutes:
                seq.render(nbeats=nbeats,
                           trigs=trigs,
                           density=self["density"])
        for lfo in self["lfos"]:
            lfo.render(nbeats=nbeats,
                       trigs=trigs,
                       density=self["density"])
        return trigs.tracks

if __name__=="__main__":
    pass
