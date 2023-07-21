from rv.modules.echo import Echo as RVEcho
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.modules.sampler import SVSampler
from octavox.modules.project import SVProject

import octavox.modules.patterns.vitling909 as vitling

import json, os, random, yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

InstrumentMapping={Kick: [Kick],
                   Snare: [Snare],
                   Hats: [OpenHat, ClosedHat]}

ModConfig=yaml.safe_load("""
modules:
  - name: KKSampler
    classname: SVSampler
  - name: SNSampler
    classname: SVSampler
  - name: HTSampler
    classname: SVSampler
  - name: Echo
    classname: RVEcho
    defaults:
      dry: 256
      wet: 256
      delay: 192
  - name: Distortion
    classname: RVDistortion
    defaults:
      power: 64
  - name: Reverb
    classname: RVReverb
    defaults:
      wet: 4
links:
  - - KKSampler
    - Echo
  - - SNSampler
    - Echo
  - - HTSampler
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
  mod: KKSampler
  styles:
  - fourfloor
  - electro
  - triplets
sn:
  mod: SNSampler
  styles:
  - backbeat
  - skip
ht: 
  mod: HTSampler
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

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

class Pattern(str):

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

Patterns=[Pattern(pat)
          for pat in ["0",
                      "0|0|1|0",
                      "3x0|1",
                      "0|1|0|1",
                      "0|1|0|2"]]

class Samples(dict):

    @classmethod
    def randomise(self, key, pool, mapping=InstrumentMapping):
        return Samples({k:v for k, v in pool.randomise().items()
                        if k in mapping[key]})

    def __init__(self, obj):
        dict.__init__(self, obj)

    def clone(self):
        return Samples(self)

class Slice(dict):

    @classmethod
    def randomise(self, key, pool,
                  config=SequenceConfig):
        return Slice(samples=Samples.randomise(key, pool),
                     seed=int(1e8*random.random()),
                     style=random.choice(config[key]["styles"]))
    
    def __init__(self, samples, seed, style):
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

    def randomise_style(self, key, limit,
                        config=SequenceConfig):
        if random.random() < limit:
            self["style"]=random.choice(config[key]["styles"])
    
class Slices(list):

    @classmethod
    def randomise(self, key, pool, n=3):
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
    def randomise(self, key, pool, patterns=Patterns):
        return Sequence({"key": key,
                         "pattern": random.choice(patterns),
                         "slices": Slices.randomise(key,
                                                    pool)})

    @init_machine(config=SequenceConfig)
    def __init__(self, item,
                 volume=1):
        dict.__init__(self, {"key": item["key"],
                             "pattern": Pattern(item["pattern"]),
                             "slices": Slices(item["slices"])})
        self.volume=1
                
    def clone(self):
        return Sequence({"key": self["key"],
                         "pattern": self["pattern"],
                         "slices": self["slices"].clone()})

    def randomise_pattern(self, limit, patterns=Patterns):
        if random.random() < limit:
            self["pattern"]=random.choice(patterns)

    def shuffle_slices(self, limit):
        if random.random() < limit:
            random.shuffle(self["slices"])

    def render(self, notes, nbeats):
        multiplier=int(nbeats/self["pattern"].size)
        offset=0
        for pat in self["pattern"].expanded:
            slice=self["slices"][pat["i"]]
            q=Q(slice["seed"])            
            fn=getattr(self, slice["style"])
            nsamplebeats=pat["n"]*multiplier
            for i in range(nsamplebeats):
                fn(q, i, notes, offset, slice["samples"])
            offset+=nsamplebeats

    def apply(fn):
        def wrapped(self, q, i, notes, offset, samples):
            v=fn(self, q, i, notes, offset, samples)
            if v!=None: # explicit because could return zero
                samplekey, volume = v
                trig={"mod": self.mod,
                      "key": samples[samplekey],
                      "vel": self.volume*volume,
                      "i": i+offset}
                notes.setdefault(self["key"], [])
                notes[self["key"]].append(trig)
        return wrapped
    
    @apply
    def fourfloor(self, q, i, *args, k=Kick):
        return vitling.fourfloor(q, i, k)
    @apply
    def electro(self, q, i, *args, k=Kick):
        return vitling.electro(q, i, k)
    @apply
    def triplets(self, q, i, *args, k=Kick):
        return vitling.triplets(q, i, k)
    @apply
    def backbeat(self, q, i, *args, k=Snare):
        return vitling.backbeat(q, i, k)
    @apply
    def skip(self, q, i, *args, k=Snare):
        return vitling.skip(q, i, k)
    @apply
    def offbeats(self, q, i, *args,
                 ko=OpenHat,
                 kc=ClosedHat):
        return vitling.offbeats(q, i, ko, kc)    
    @apply
    def closed(self, q, i, *args, k=ClosedHat):
        return vitling.closed(q, i, k)
                            
class Sequences(list):

    @classmethod
    def randomise(self, pool, config=SequenceConfig):
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

    def render(self, nbeats, notes):
        q=Q(self["seed"])
        for i in range(nbeats):
            self.sample_hold(q, i, notes)

    def apply(fn):
        def wrapped(self, q, i, notes):
            v=fn(self, q, i, notes)
            if v!=None: # explicit because could return zero
                trig={"mod": self.mod,
                      "ctrl": self.ctrl,
                      "v": v,
                      "i": i}
                notes.setdefault(self["key"], [])
                notes[self["key"]].append(trig)
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
        
    def __init__(self, sequences, lfos, mutes):
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
    
    def render_sequences(self, notes, nbeats,
                         config=SequenceConfig):
        for sequence in self["sequences"]:
            if sequence["key"] not in self["mutes"]:
                sequence.render(nbeats=nbeats,
                                notes=notes)
                    
    def render_lfos(self, notes, nbeats,
                    config=LfoConfig):
        for lfo in self["lfos"]:
            lfo.render(nbeats=nbeats,
                       notes=notes)

    def render(self, nbeats):
        notes={}
        self.render_sequences(notes=notes,
                              nbeats=nbeats)
        self.render_lfos(notes=notes,
                         nbeats=nbeats)
        return [notes[key]
                for key in sorted(notes.keys())]

class Patches(list):

    @classmethod
    def randomise(self, pool, n):
        return Patches([Patch.randomise(pool)
                        for i in range(n)])
    
    def __init__(self, patches):
        list.__init__(self, [Patch(**patch)
                             for patch in patches])

    """
    - unfortunately track needs to be rendered before samples can be filtered
    - because not all samples are used post- rendering, and there are limited sample slots
    - also because patches may share samples
    """
        
    def filter_samples(self, nbeats):
        samplekeys={}
        for patch in self:
            for track in patch.render(nbeats):
                for trig in track:
                    if "key" in trig:
                        key=trig["mod"][:2].lower()
                        samplekeys.setdefault(key, set()) # NB set()
                        samplekeys[key].add(tuple(trig["key"])) # NB tuple()
        return {k:list(v)
                for k, v in samplekeys.items()}

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
    def render_sunvox(self, banks, nbeats, filename,
                      nbreaks=0,
                      modconfig=ModConfig):
        samplekeys=self.filter_samples(nbeats)
        for mod in modconfig["modules"]:
            klass=eval(mod["classname"])
            if "Sampler" in mod["name"]:
                key=mod["name"][:2].lower() # change?
                kwargs={"samplekeys": samplekeys[key],
                        "banks": banks}
            else:
                kwargs={}
            mod["instance"]=klass(**kwargs)
        project=SVProject().render(patches=self,
                                   modconfig=modconfig,
                                   banks=banks,
                                   nbeats=nbeats,
                                   nbreaks=nbreaks)
        projfile="tmp/picobeats/sunvox/%s.sunvox" % filename
        with open(projfile, 'wb') as f:
            project.write_to(f)
    
if __name__=="__main__":
    pass
