from octavox.modules.project import SVProject, SVPatch

import json, os, random, yaml

Config=yaml.safe_load(open("octavox/projects/picobass/config.yaml").read())

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
                  instruments=Instruments):
        samples={}
        for k in instruments[key]:
            samples[k]=random.choice(pool[k])
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
                  config=Config["sequencers"]):
        return Slice(samples=Samples.randomise(i=i,
                                               key=key,
                                               pool=pool):
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
                        key,
                        limit,
                        config=Config["sequencers"]):
        if random.random() < limit:
            self["style"]=random.choice(config[key]["styles"])
    
class Slices(list):

    @classmethod
    def randomise(self,
                  key,
                  pool,
                  n=3):
        return Slices([Slice.randomise(i=i,
                                       key=key,
                                       pool=pool)
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
                  key,
                  temperature,
                  pool)
        return Sequencer({"key": key,
                          "pattern": Pattern.randomise(temperature),
                          "slices": Slices.randomise(key=key,
                                                     pool=pool)})

    @init_machine(config=Config["sequencers"])
    def __init__(self, item):
        dict.__init__(self, {"key": item["key"],
                             "pattern": Pattern(item["pattern"]),
                             "slices": Slices(item["slices"])})
                
    def clone(self):
        return Sequencer({"key": self["key"],
                          "pattern": self["pattern"],
                          "slices": self["slices"].clone()})

    def render(self,
               tracks,
               nbeats):
        multiplier=int(nbeats/self["pattern"].size)
        offset=0
        for pat in self["pattern"].expanded:
            slice=self["slices"][pat["i"]]
            q=Q(slice["seed"])            
            fn=getattr(self, slice["style"])
            nsamplebeats=pat["n"]*multiplier
            for i in range(nsamplebeats):
                fn(q, i, tracks, offset, slice["samples"])
            offset+=nsamplebeats

    def apply(fn):
        def wrapped(self, q, i, d,
                    tracks,
                    offset,
                    samples):
            v=fn(self, q, i, d, tracks, offset, samples)
            if v!=None: # explicit because could return zero
                instkey, volume = v
                samplekey=samples[instkey]
                trig={"vel": volume,
                      "i": i+offset}
                trig["mod"]=self.mod
                trig["key"]=samplekey
                tracks.setdefault(self["key"], [])
                tracks[self["key"]].append(trig)
        return wrapped
    
class Sequencers(list):

    @classmethod
    def randomise(self,
                  pool,
                  temperature,
                  config=Config["sequencers"]):
        return Sequencers([Sequencer.randomise(key=key,
                                               pool=pool,
                                               temperature=temperature)
                          for key in config])

    def __init__(self, sequencers):
        list.__init__(self, [Sequencer(seq)
                             for seq in sequencers])

    def clone(self):
        return Sequencers([seq.clone()
                           for seq in self])

class Lfo(dict):

    @classmethod
    def randomise(self, key):
        return Lfo({"key": key,
                    "seed": int(1e8*random.random())})

    @init_machine(config=Config["lfos"])
    def __init__(self, item):
        dict.__init__(self, item)
        
    def clone(self):
        return Lfo(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def render(self, nbeats, tracks):
        q=Q(self["seed"])
        for i in range(nbeats):
            self.sample_hold(q, i, tracks)

    def apply(fn):
        def wrapped(self, q, i, tracks):
            v=fn(self, q, i, tracks)
            if v!=None: # explicit because could return zero
                trig={"mod": self.mod,
                      "ctrl": self.ctrl,
                      "v": v,
                      "i": i}
                tracks.setdefault(self["key"], [])
                tracks[self["key"]].append(trig)
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
        return Lfos([Lfo.randomise(key)
                     for key in config])

    def __init__(self, lfos):
        list.__init__(self, [Lfo(lfo)
                             for lfo in lfos])

    def clone(self):
        return Lfos([lfo.clone()
                     for lfo in self])

class Patch(dict):

    @classmethod
    def randomise(self, pool, temperature):
        return Patch(sequencers=Sequencers.randomise(pool=pool,
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
                slice.randomise_style(seq["key"],
                                      limits["style"])
                slice.randomise_seed(limits["seed"])
        for lfo in self["lfos"]:
            lfo.randomise_seed(limits["seed"])
        return self
    
    def render(self,
               nbeats):
        tracks=SVPatch(nbeats=nbeats)
        for seq in self["sequencers"]:
            if seq["key"] not in self["mutes"]:
                seq.render(nbeats=nbeats,
                           tracks=tracks)
        for lfo in self["lfos"]:
            lfo.render(nbeats=nbeats,
                       tracks=tracks)
        return tracks

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
                      filename,
                      config=Config):
        project=SVProject().render(patches=[patch.render(nbeats=nbeats)
                                            for patch in self],
                                   config=config,
                                   banks=banks)
        with open(filename, 'wb') as f:
            project.write_to(f)
    
if __name__=="__main__":
    pass
