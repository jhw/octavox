from octavox.modules.project import SVProject, SVPatch

import octavox.modules.sequences.vitling909 as vitling

import json, os, random, yaml

Config=yaml.safe_load(open("octavox/projects/picobeats/config.yaml").read())

InstrumentMapping={"kk": ["kk"],
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
                  key,
                  pool,
                  mapping=InstrumentMapping):
        return Samples({k:v for k, v in pool.randomise().items()
                        if k in mapping[key]})

    def __init__(self, obj):
        dict.__init__(self, obj)

    def clone(self):
        return Samples(self)

class Slice(dict):

    @classmethod
    def randomise(self,
                  key,
                  pool,
                  config=Config["sequencers"]):
        return Slice(samples=Samples.randomise(key=key,
                                               pool=pool),
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
        return Slices([Slice.randomise(key=key,
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

def Mixer(instkey, samplekey):
    modname, _ = samplekey
    # return 0.8 if instkey=="kk" and modname=="svdrum" else 1.0
    return 1.0
    
class Sequencer(dict):

    @classmethod
    def randomise(self,
                  key,
                  temperature,
                  pool):
        return Sequencer({"key": key,
                          "pattern": Pattern.randomise(temperature),
                          "slices": Slices.randomise(key=key,
                                                     pool=pool)})

    @init_machine(config=Config["sequencers"])
    def __init__(self, item,
                 mixer=Mixer):
        dict.__init__(self, {"key": item["key"],
                             "pattern": Pattern(item["pattern"]),
                             "slices": Slices(item["slices"])})
        self.mixer=mixer
                
    def clone(self):
        return Sequencer({"key": self["key"],
                          "pattern": self["pattern"],
                          "slices": self["slices"].clone()})

    def randomise_pattern(self, temperature, limit):
        if random.random() < limit:
            self["pattern"]=Pattern.randomise(temperature)

    def shuffle_slices(self, limit):
        if random.random() < limit:
            random.shuffle(self["slices"])

    def render(self,
               tracks,
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
                fn(q, i, density, tracks, offset, slice["samples"])
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
                volume=self.mixer(instkey, samplekey)
                trig={"vel": volume,
                      "i": i+offset}
                if samplekey[0]!="svdrum":
                    trig["mod"]=self.mod
                    trig["key"]=samplekey
                else:
                    trig["mod"]=self.mod.replace("Sampler", "Drum")
                    trig["id"]=samplekey[1]
                tracks.setdefault(self["key"], [])
                tracks[self["key"]].append(trig)
        return wrapped
    
    @apply
    def fourfloor(self, q, i, d, *args, k="kk"):
        return vitling.fourfloor(q, i, d, k)
    @apply
    def electro(self, q, i, d, *args, k="kk"):
        return vitling.electro(q, i, d, k)
    @apply
    def triplets(self, q, i, d, *args, k="kk"):
        return vitling.triplets(q, i, d, k)
    @apply
    def backbeat(self, q, i, d, *args, k="sn"):
        return vitling.backbeat(q, i, d, k)
    @apply
    def skip(self, q, i, d, *args, k="sn"):
        return vitling.skip(q, i, d, k)
    @apply
    def offbeats(self, q, i, d, *args, k=["oh", "ch"]):
        return vitling.offbeats(q, i, d, k)    
    @apply
    def closed(self, q, i, d, *args, k="ch"):
        return vitling.closed(q, i, d, k)
                            
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
        list.__init__(self, [Sequencer(sequencer)
                             for sequencer in sequencers])

    def clone(self):
        return Sequencers([sequencer.clone()
                           for sequencer in self])

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

"""
- mutes has to be a Patch state variable (and not something passed from cli like nbeats) as it needs to be applied locally to each patch, and not globally
"""
    
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
                             "mutes": mutes})
        
    def clone(self):
        return Patch(sequencers=self["sequencers"].clone(),
                     lfos=self["lfos"].clone(),
                     mutes=list(self["mutes"]))

    def mutate(self, temperature, limits):
        for sequencer in self["sequencers"]:
            sequencer.randomise_pattern(temperature=temperature,
                                        limit=limits["pat"])
            sequencer.shuffle_slices(limits["slices"])
            for slice in sequencer["slices"]:
                slice.randomise_style(sequencer["key"],
                                      limits["style"])
                slice.randomise_seed(limits["seed"])
        for lfo in self["lfos"]:
            lfo.randomise_seed(limits["seed"])
        return self
    
    def render_sequencers(self,
                          tracks,
                          nbeats,
                          density,
                          config=Config["sequencers"]):
        for sequencer in self["sequencers"]:
            if sequencer["key"] not in self["mutes"]:
                sequencer.render(nbeats=nbeats,
                                 tracks=tracks,
                                 density=density)
                
    def render_lfos(self,
                    tracks,
                    nbeats,
                    config=Config["lfos"]):
        for lfo in self["lfos"]:
            lfo.render(nbeats=nbeats,
                       tracks=tracks)

    def render(self,
               nbeats,
               density):
        tracks=SVPatch(nbeats=nbeats)
        self.render_sequencers(tracks=tracks,
                               nbeats=nbeats,
                               density=density)
        self.render_lfos(tracks=tracks,
                         nbeats=nbeats)
        return tracks

class Patches(list):

    @classmethod
    def randomise(self, pool, temperature, n):
        return Patches([Patch.randomise(pool=pool,
                                        temperature=temperature)
                        for i in range(n)])
    
    def __init__(self, patches):
        list.__init__(self, [Patch(**patch)
                             for patch in patches])

    def init_paths(paths):
        def decorator(fn):
            def wrapped(*args, **kwargs):
                for path in paths:
                    if not os.path.exists(path):
                        os.makedirs(path)
                return fn(*args, **kwargs)
            return wrapped
        return decorator

    @init_paths(["tmp/picobeats/json"])
    def render_json(self, filename):
        projfile="tmp/picobeats/json/%s.json" % filename
        with open(projfile, 'w') as f:
            f.write(json.dumps(self,
                               indent=2))

    @init_paths(["tmp/picobeats/sunvox"])
    def render_sunvox(self,
                      banks,
                      nbeats,
                      density,
                      filename,
                      nbreaks=0,
                      config=Config):
        project=SVProject().render(patches=[patch.render(nbeats=nbeats,
                                                         density=density)
                                            for patch in self],
                                   config=config,
                                   banks=banks,
                                   nbreaks=nbreaks)
        projfile="tmp/picobeats/sunvox/%s.sunvox" % filename
        with open(projfile, 'wb') as f:
            project.write_to(f)
    
if __name__=="__main__":
    pass
