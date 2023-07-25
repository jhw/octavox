from octavox.modules.project import SVProject, SVPatch, Output

import octavox.modules.patterns.vitling909 as vitling

import json, os, random, yaml

ModConfig=yaml.safe_load("""
modules:
  - name: KickSampler
    class: octavox.modules.sampler.SVSampler
    key: kk
  - name: SnareSampler
    class: octavox.modules.sampler.SVSampler
    key: sn    
  - name: HatSampler
    class: octavox.modules.sampler.SVSampler
    key: ht
  - name: KickDrum
    class: rv.modules.drumsynth.DrumSynth
  - name: SnareDrum
    class: rv.modules.drumsynth.DrumSynth
  - name: HatDrum
    class: rv.modules.drumsynth.DrumSynth
  - name: Echo
    class: rv.modules.echo.Echo
    defaults:
      dry: 256
      wet: 256
      delay: 192
  - name: Distortion
    class: rv.modules.distortion.Distortion
    defaults:
      power: 64
  - name: Reverb
    class: rv.modules.reverb.Reverb
    defaults:
      wet: 4
links:
  - - KickSampler
    - Echo
  - - SnareSampler
    - Echo
  - - HatSampler
    - Echo
  - - KickDrum
    - Echo
  - - SnareDrum
    - Echo
  - - HatDrum
    - Echo
  - - Echo
    - Distortion
  - - Distortion
    - Reverb
  - - Reverb
    - Output
""")

SequenceConfig=yaml.safe_load("""
kk:
  mod: KickSampler
  styles:
  - fourfloor
  - electro
  - triplets
sn:
  mod: SnareSampler
  styles:
  - backbeat
  - skip
ht: 
  mod: HatSampler
  styles:
  - offbeats
  - closed
""")

LfoConfig=yaml.safe_load("""
ec0:
  mod: Echo
  ctrl: wet
  range: [0, 1]
  increment: 0.25
  step: 4
ec1:
  mod: Echo
  ctrl: feedback
  range: [0, 1]
  increment: 0.25
  step: 4
""")

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

InstrumentMapping={Kick: [Kick],
                   Snare: [Snare],
                   Hats: [OpenHat, ClosedHat]}

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
    def randomise(self, patterns=Patterns):
        return Pattern(random.choice(patterns))
    
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
                  config=SequenceConfig):
        return Slice(samples=Samples.randomise(key, pool),
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
                        config=SequenceConfig):
        if random.random() < limit:
            self["style"]=random.choice(config[key]["styles"])
    
class Slices(list):

    @classmethod
    def randomise(self,
                  key,
                  pool,
                  n=3):
        return Slices([Slice.randomise(key, pool)
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

class Sequence(dict):

    @classmethod
    def randomise(self,
                  key,
                  pool):
        return Sequence({"key": key,
                         "pattern": Pattern.randomise(),
                         "slices": Slices.randomise(key,
                                                    pool)})

    @init_machine(config=SequenceConfig)
    def __init__(self, item,
                 volume=1):
        dict.__init__(self, {"key": item["key"],
                             "pattern": Pattern(item["pattern"]),
                             "slices": Slices(item["slices"])})
        self.volume=volume
                
    def clone(self):
        return Sequence({"key": self["key"],
                         "pattern": self["pattern"],
                         "slices": self["slices"].clone()})

    def randomise_pattern(self, limit):
        if random.random() < limit:
            self["pattern"]=Pattern.randomise()

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
                samplekey, volume = v
                trig={"mod": self.mod,
                      "key": samples[samplekey],
                      "vel": self.volume*volume,
                      "i": i+offset}
                tracks.setdefault(self["key"], [])
                tracks[self["key"]].append(trig)
        return wrapped
    
    @apply
    def fourfloor(self, q, i, d, *args, k=Kick):
        return vitling.fourfloor(q, i, d, k)
    @apply
    def electro(self, q, i, d, *args, k=Kick):
        return vitling.electro(q, i, d, k)
    @apply
    def triplets(self, q, i, d, *args, k=Kick):
        return vitling.triplets(q, i, d, k)
    @apply
    def backbeat(self, q, i, d, *args, k=Snare):
        return vitling.backbeat(q, i, d, k)
    @apply
    def skip(self, q, i, d, *args, k=Snare):
        return vitling.skip(q, i, d, k)
    @apply
    def offbeats(self, q, i, d, *args,
                 ko=OpenHat,
                 kc=ClosedHat):
        return vitling.offbeats(q, i, d, ko, kc)    
    @apply
    def closed(self, q, i, d, *args, k=ClosedHat):
        return vitling.closed(q, i, d, k)
                            
class Sequences(list):

    @classmethod
    def randomise(self,
                  pool,
                  config=SequenceConfig):
        return Sequences([Sequence.randomise(key, pool)
                          for key in config])

    def __init__(self, sequences):
        list.__init__(self, [Sequence(sequence)
                             for sequence in sequences])

    def clone(self):
        return Sequences([sequence.clone()
                          for sequence in self])

class Lfo(dict):

    @classmethod
    def randomise(self, key):
        return Lfo({"key": key,
                    "seed": int(1e8*random.random())})

    @init_machine(config=LfoConfig)
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
            floor, ceil = self.range
            v0=floor+(ceil-floor)*q.random()
            return self.increment*int(0.5+v0/self.increment)
                
class Lfos(list):

    @classmethod
    def randomise(self, config=LfoConfig):
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
    def randomise(self, pool):
        return Patch(sequences=Sequences.randomise(pool),
                     lfos=Lfos.randomise(),
                     mutes=[])
        
    def __init__(self,
                 sequences,
                 lfos,
                 mutes):
        dict.__init__(self, {"sequences": Sequences(sequences),
                             "lfos": Lfos(lfos),
                             "mutes": mutes})
        
    def clone(self):
        return Patch(sequences=self["sequences"].clone(),
                     lfos=self["lfos"].clone(),
                     mutes=list(self["mutes"]))

    def mutate(self, limits):
        for sequence in self["sequences"]:
            sequence.randomise_pattern(limits["pat"])
            sequence.shuffle_slices(limits["slices"])
            for slice in sequence["slices"]:
                slice.randomise_style(sequence["key"],
                                      limits["style"])
                slice.randomise_seed(limits["seed"])
        for lfo in self["lfos"]:
            lfo.randomise_seed(limits["seed"])
        return self
    
    def render_sequences(self,
                         tracks,
                         nbeats,
                         density,
                         config=SequenceConfig):
        for sequence in self["sequences"]:
            if sequence["key"] not in self["mutes"]:
                sequence.render(nbeats=nbeats,
                                tracks=tracks,
                                density=density)
                    
    def render_lfos(self,
                    tracks,
                    nbeats,
                    config=LfoConfig):
        for lfo in self["lfos"]:
            lfo.render(nbeats=nbeats,
                       tracks=tracks)

    def render(self,
               nbeats,
               density):
        tracks=SVPatch(nbeats=nbeats)
        self.render_sequences(tracks=tracks,
                              nbeats=nbeats,
                              density=density)
        self.render_lfos(tracks=tracks,
                         nbeats=nbeats)
        return tracks

class Patches(list):

    @classmethod
    def randomise(self, pool, n):
        return Patches([Patch.randomise(pool)
                        for i in range(n)])
    
    def __init__(self, patches):
        list.__init__(self, [Patch(**patch)
                             for patch in patches])

    def validate_config(self,
                        modconfig=ModConfig,
                        seqconfig=SequenceConfig,
                        lfoconfig=LfoConfig):
        def validate_sampler_keys():
            modkeys=[mod["key"] for mod in modconfig["modules"]
                     if "key" in mod]
            for key in modkeys:
                if key not in seqconfig:
                    raise RuntimeError("key %s missing from sequence config" % key)
                for key in seqconfig:
                    if key not in modkeys:
                        raise RuntimeError("key %s missing from module config" % key)
        def validate_links():
            modnames=[Output]+[mod["name"] for mod in modconfig["modules"]]
            for links in modconfig["links"]:
                for modname in links:
                    if modname not in modnames:
                        raise RuntimeError("unknown module %s in links" % modname)
        validate_sampler_keys()
        validate_links()
                    
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
                      modconfig=ModConfig):
        project=SVProject().render(patches=[patch.render(nbeats=nbeats,
                                                         density=density)
                                            for patch in self],
                                   modconfig=modconfig,
                                   banks=banks,
                                   nbreaks=nbreaks)
        projfile="tmp/picobeats/sunvox/%s.sunvox" % filename
        with open(projfile, 'wb') as f:
            project.write_to(f)
    
if __name__=="__main__":
    pass
