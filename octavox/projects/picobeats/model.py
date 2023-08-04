from octavox.modules.project import SVProject, SVTrigs, SVNoteTrig, SVFXTrig

import octavox.modules.sequences.vitling909 as nineohnine

import json, os, random, yaml

Config=yaml.safe_load(open("octavox/projects/picobeats/config.yaml").read())

Instruments={"kk": ["kk"],
             "sn": ["sn"],
             "ht": ["oh", "ch"]}

Patterns=["0",
          "0|0|1|0",
          "3x0|1",
          "0|1|0|1",
          "0|1|0|2"]

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

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

class Samples(dict):

    @classmethod
    def randomise(self,
                  i,
                  key,
                  pool,
                  fixes,
                  instruments=Instruments):
        samples={}
        for k in instruments[key]:
            keyfixes=list(fixes[k].values())
            values=keyfixes if i==0 and keyfixes!=[] else pool[k]
            samples[k]=random.choice(values)
        return Samples(samples)
            
    def __init__(self, obj):
        dict.__init__(self, obj)

    def clone(self):
        return Samples(self)

class Slice(dict):

    @classmethod
    def randomise(self,
                  i,
                  key,
                  pool,
                  fixes,
                  config={item["key"]:item
                          for item in Config["sequencers"]}):
        return Slice(samples=Samples.randomise(i=i,
                                               key=key,
                                               pool=pool,
                                               fixes=fixes),
                     seed=int(1e8*random.random()),
                     style=random.choice(config[key]["styles"]))
    
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
                  key,
                  pool,
                  fixes,
                  n=3):
        return Slices([Slice.randomise(i=i,
                                       key=key,
                                       pool=pool,
                                       fixes=fixes)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])

    def clone(self):
        return Slices(self)

def init_machine(config):
    def decorator(fn):
        def wrapped(self, item, **kwargs):
            fn(self, item, **kwargs)
            params=config[item["key"]]
            for attr in params:
                setattr(self, attr, params[attr])
        return wrapped
    return decorator

class Sequencer(dict):

    @classmethod
    def randomise(self,
                  item,
                  temperature,
                  pool,
                  fixes):
        return Sequencer({"key": item["key"],
                          "pattern": Pattern.randomise(temperature),
                          "slices": Slices.randomise(key=item["key"],
                                                     pool=pool,
                                                     fixes=fixes)})

    @init_machine(config={item["key"]:item
                          for item in Config["sequencers"]})
    def __init__(self, item):
        dict.__init__(self, {"key": item["key"],
                             "pattern": Pattern(item["pattern"]),
                             "slices": Slices(item["slices"])})
                
    def clone(self):
        return Sequencer({"key": self["key"],
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
            for i in range(nsamplebeats):
                fn(q, i, density, trigs, offset, slice["samples"])
            offset+=nsamplebeats

    def apply(fn):
        def wrapped(self, q, i, d,
                    trigs,
                    offset,
                    samples):
            v=fn(self, q, i, d, trigs, offset, samples)
            if v!=None: # explicit because could return zero
                instkey, volume = v
                samplekey=samples[instkey]
                samplekey["mod"]=self.mod
                trig=SVNoteTrig({"vel": volume,
                                 "i": i+offset})
                if samplekey["bank"]!="svdrum":
                    trig["mod"]=self.mod
                    trig["key"]=samplekey
                else:
                    trig["mod"]=self.mod.replace("Sampler", "Drum")
                    trig["id"]=samplekey["id"]
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

class Lfo(dict):

    @classmethod
    def randomise(self, item):
        return Lfo({"key": item["key"],
                    "seed": int(1e8*random.random())})

    @init_machine(config={item["key"]:item
                          for item in Config["lfos"]})
    def __init__(self, item):
        dict.__init__(self, item)
        
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
                trig=SVFXTrig({"mod": self.mod,
                               "ctrl": self.ctrl,
                               "v": v,
                               "i": i})
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
    def randomise(self, pool, fixes, temperature):
        return Patch(sequencers=Sequencers.randomise(pool=pool,
                                                     fixes=fixes,
                                                     temperature=temperature),
                     lfos=Lfos.randomise(),
                     mutes=[])
        
    def __init__(self,
                 sequencers,
                 lfos,
                 mutes):
        dict.__init__(self, {"sequencers": Sequencers(sequencers),
                             "lfos": Lfos(lfos),
                             "mutes": []})
        
    def clone(self):
        return Patch(sequencers=self["sequencers"].clone(),
                     lfos=self["lfos"].clone(),
                     mutes=list(self["mutes"]))

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
               density):
        trigs=SVTrigs(nbeats=nbeats)
        for seq in self["sequencers"]:
            if seq["key"] not in self["mutes"]:
                seq.render(nbeats=nbeats,
                           trigs=trigs,
                           density=density)
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
                      density,
                      filename,
                      config=Config):
        project=SVProject().render(patches=[patch.render(nbeats=nbeats,
                                                         density=density)
                                            for patch in self],
                                   config=config,
                                   banks=banks)
        with open(filename, 'wb') as f:
            project.write_to(f)
    
if __name__=="__main__":
    pass
