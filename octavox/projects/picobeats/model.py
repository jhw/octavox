from octavox.modules.project import SVProject, SVTrigs, SVNoteTrig, SVFXTrig

from octavox.modules.banks import SVSampleKey

from octavox.projects import Q

import octavox.modules.sequences.vitling909 as nineohnine

import json, os, random, yaml

Config=yaml.safe_load(open("octavox/projects/picobeats/config.yaml").read())

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

class Samples(list):

    @classmethod
    def randomise(self,
                  i,
                  tag,
                  pool,
                  fixes,
                  tags=Config["tags"]):
        samples=[]
        for childtag in tags[tag]:
            keyfixes=list(fixes[childtag].values())
            values=keyfixes if i==0 and keyfixes!=[] else pool[childtag]
            samples.append(random.choice(values))
        return Samples(samples)
            
    def __init__(self, items=[]):
        list.__init__(self, [SVSampleKey(item)
                             for item in items])

    def clone(self):
        return Samples(self)

    @property
    def tagmap(self):
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
                          for item in Config["sequencers"]}):
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

    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def randomise_style(self,
                        styles,
                        limit):
        if random.random() < limit:
            self["style"]=random.choice(styles)
    
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

"""
- temporary helper; should be replaced by config.yaml data binding classes
"""
    
def sequencer_id(item):
    return item["mod"]

class Sequencer(dict):
    
    @classmethod
    def randomise(self,
                  item,
                  temperature,
                  pool,
                  fixes):
        return Sequencer({"id": sequencer_id(item),
                          "pattern": Pattern.randomise(temperature),
                          "slices": Slices.randomise(tag=item["tag"],
                                                     pool=pool,
                                                     fixes=fixes)})

    def __init__(self, item,
                 config={sequencer_id(item):item
                         for item in Config["sequencers"]}):
        dict.__init__(self, {"id": item["id"],
                             "pattern": Pattern(item["pattern"]),
                             "slices": Slices(item["slices"])})
        params=config[item["id"]]
        for attr in params:
            setattr(self, attr, params[attr])
                            
    def clone(self):
        return Sequencer({"id": self["id"],
                          "pattern": self["pattern"],
                          "slices": self["slices"].clone()})

    def render(self,
               trigs,
               nbeats,
               density):
        multiplier=int(nbeats/self["pattern"].size)
        offset=0
        for pat in self["pattern"].expanded:
            slice=self["slices"][pat["i"]]
            q=Q(slice["seed"])            
            fn=getattr(self, slice["style"])
            nsamplebeats=pat["n"]*multiplier
            samples=slice["samples"].tagmap
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
                samplekey["tags"].append(self.mod)
                trig=SVNoteTrig(mod=self.mod,
                                vel=volume,
                                i=i+offset,
                                samplekey=samplekey)
                trigs.append(trig)
        return wrapped
    
    @apply
    def fourfloor(self, q, i, d, *args, k="kk"):
        return nineohnine.fourfloor(q, i, d, k)
    @apply
    def electro(self, q, i, d, *args, k="kk"):
        return nineohnine.electro(q, i, d, k)
    @apply
    def triplets(self, q, i, d, *args, k="kk"):
        return nineohnine.triplets(q, i, d, k)
    @apply
    def backbeat(self, q, i, d, *args, k="sn"):
        return nineohnine.backbeat(q, i, d, k)
    @apply
    def skip(self, q, i, d, *args, k="sn"):
        return nineohnine.skip(q, i, d, k)
    @apply
    def offbeats(self, q, i, d, *args, k=["oh", "ch"]):
        return nineohnine.offbeats(q, i, d, k)    
    @apply
    def closed(self, q, i, d, *args, k="ch"):
        return nineohnine.closed(q, i, d, k)
                            
class Sequencers(list):
    
    @classmethod
    def randomise(self,
                  pool,
                  fixes,
                  temperature,
                  config=Config["sequencers"]):
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

"""
- temporary helper; should be replaced by config.yaml data binding classes
"""
    
def lfo_id(item):
    return "%s/%s" % (item["mod"],
                      item["ctrl"])
    
class Lfo(dict):
    
    @classmethod
    def randomise(self, item):
        return Lfo({"id": lfo_id(item),
                    "seed": int(1e8*random.random())})

    def __init__(self, item,
                 config={lfo_id(item):item
                         for item in Config["lfos"]}):
        dict.__init__(self, item)
        params=config[item["id"]]
        for attr in params:
            setattr(self, attr, params[attr])
        
    def clone(self):
        return Lfo(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def render(self, nbeats, trigs):
        q=Q(self["seed"])
        for i in range(nbeats):
            self.sample_hold(q, i, trigs)

    def apply(fn):
        def wrapped(self, q, i, trigs):
            v=fn(self, q, i, trigs)
            if v!=None: # explicit because could return zero
                trig=SVFXTrig(mod=self.mod,
                              ctrl=self.ctrl,
                              value=v,
                              i=i)
                trigs.append(trig)
        return wrapped

    @apply
    def sample_hold(self, q, i, *args):
        if 0 == i % self.step:
            if q.random() < self.live:
                floor, ceil = self.range
                v0=floor+(ceil-floor)*q.random()
                return self.increment*int(0.5+v0/self.increment)
            else:
                return 0.0
                
class Lfos(list):

    @classmethod
    def randomise(self, config=Config["lfos"]):
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

    def mutate(self, limits):
        for seq in self["sequencers"]:
            for slice in seq["slices"]:
                slice.randomise_style(seq.styles,
                                      limits["style"])
                slice.randomise_seed(limits["seed"])
        for lfo in self["lfos"]:
            lfo.randomise_seed(limits["seed"])
        return self
    
    def render(self,
               nbeats,
               mutes=[]):
        trigs=SVTrigs(nbeats=nbeats)
        for seq in self["sequencers"]:
            if seq["id"] not in mutes:
                seq.render(nbeats=nbeats,
                           trigs=trigs,
                           density=self["density"])
        for lfo in self["lfos"]:
            lfo.render(nbeats=nbeats,
                       trigs=trigs)
        return trigs.tracks

class Patches(list):

    def __init__(self, patches=[]):
        list.__init__(self, [Patch(**patch)
                             for patch in patches])

    def render_json(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self,
                               indent=2))

    def render_sunvox(self,
                      banks,
                      nbeats,
                      bpm,
                      filename,
                      config=Config):
        project=SVProject().render(patches=[patch.render(nbeats=nbeats)
                                            for patch in self],
                                   config=config,
                                   banks=banks,
                                   bpm=bpm)
        with open(filename, 'wb') as f:
            project.write_to(f)
    
if __name__=="__main__":
    pass
