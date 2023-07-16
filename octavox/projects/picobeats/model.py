from rv.modules.echo import Echo as RVEcho
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.modules.sampler import SVSampler
from octavox.modules.project import SVProject

import json, math, os, random, yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

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

MachineConfig=yaml.safe_load("""
kk:
  generator: vitling
  styles:
  - fourfloor
  - electro
  - triplets
sn:
  generator: vitling
  styles:
  - backbeat
  - skip
ht:
  generator: vitling
  styles:
  - offbeats
  - closed
""")

LfoConfig=yaml.safe_load("""
ec:
  generator: sample_hold
""")

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

def hungarorise(text):
    return "".join([tok.capitalize()
                    for tok in text.split("_")])

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

class Patterns(list):

    def __init__(self, items=[]):
        list.__init__(self, items)

    def randomise(self, slicetemp):
        n=1+math.floor(slicetemp*len(self))
        return random.choice(self[:n])  
        
Breakbeats=Patterns([Pattern(pat)
                     for pat in ["0",
                                 "3x0|1",
                                 "0|1|0|1",
                                 "0|1|0|2",
                                 "0|1|2|3"]])

class Samples(dict):

    """
    - note that sample keys are different from machine keys (oh/ch vs ht), so patches should contain unrestricted set
    """
    
    @classmethod
    def randomise(self, pool):
        return Samples(pool.randomise())

    def __init__(self, obj):
        dict.__init__(self, obj)

    def clone(self):
        return Samples(self)

"""
- https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
"""
        
class VitlingGenerator:

    def __init__(self, key, offset, samples, notes, volume=1):
        self.key=key
        self.offset=offset
        self.samples=samples
        self.notes=notes
        self.volume=volume

    def generate(self, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)

    def handle(fn):
        def wrapped(self, q, i, **kwargs):
            v=fn(self, q, i, **kwargs)
            if v:
                samplekey, volume = v
                trig={"mod": "%sSampler" % self.key.upper(),              
                      "key": self.samples[samplekey],
                      "vel": self.volume*volume,
                      "i": i+self.offset}
                self.notes.setdefault(self.key, [])
                self.notes[self.key].append(trig)
        return wrapped
    
    @handle
    def fourfloor(self, q, i, k=Kick):
        if i % 4 == 0:
            return (k, 0.9)
        elif i % 2 == 0 and q.random() < 0.1:
            return (k, 0.6)

    @handle
    def electro(self, q, i, k=Kick):
        if i == 0:
            return (k, 1)
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5) or
              q.random() < 0.05):
            return (k, 0.9*q.random())

    @handle
    def triplets(self, q, i, k=Kick):
        if i % 16  in [0, 3, 6, 9, 14]:
            return (k, 1)

    @handle
    def backbeat(self, q, i, k=Snare):
        if i % 8 == 4:
            return (k, 1)

    @handle
    def skip(self, q, i, k=Snare):
        if i % 8 in [3, 6]:
            return (k, 0.6+0.4*q.random())
        elif i % 2 == 0 and q.random() < 0.2:
            return (k, 0.4+0.2*q.random())
        elif q.random() < 0.1:
            return (k, 0.2+0.2*q.random())

    @handle
    def offbeats(self, q, i,
                 ko=OpenHat,
                 kc=ClosedHat):
        if i % 4 == 2:
            return (ko, 0.4)
        elif q.random() < 0.3:
            k=ko if q.random() < 0.5 else kc
            return (kc, 0.2*q.random())

    @handle
    def closed(self, q, i, k=ClosedHat):
        if i % 2 == 0:
            return (k, 0.4)
        elif q.random() < 0.5:
            return (k, 0.3*q.random())

class SampleHoldGenerator:

    def __init__(self, key, offset, range, notes,
                 mod="Echo",
                 inc=0.25,
                 step=4):
        self.key=key
        self.offset=offset
        self.range=range
        self.notes=notes
        self.mod=mod
        self.inc=inc
        self.step=step
    
    def generate(self, q, n, style="sample_hold"):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)

    def handle(fn):
        def wrapped(self, q, i, k="wet", **kwargs):
            v=fn(self, q, i, **kwargs)
            if v:
                trig={"mod": self.mod,
                      "ctrl": k,
                      "v": v,
                      "i": i+self.offset}
                self.notes.setdefault(self.key, [])
                self.notes[self.key].append(trig)
        return wrapped

    @handle
    def sample_hold(self, q, i):
        if 0 == i % self.step:
            floor, ceil = self.range
            v0=floor+(ceil-floor)*q.random()
            return self.inc*int(0.5+v0/self.inc)
            
class Machine(dict):

    def __init__(self, item):
        dict.__init__(self, item)

    def clone(self):
        return Machine(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def randomise_style(self, limit, config=MachineConfig):
        styles=config[self["key"]]["styles"]
        if random.random() < limit:
            self["style"]=random.choice(styles)

    def render(self, nbeats, generator):
        generator.generate(n=nbeats,
                           q=Q(self["seed"]),
                           style=self["style"])
    
class Machines(list):

    @classmethod
    def randomise(self, config=MachineConfig):
        def init_seed(key):
            return int(1e8*random.random())
        def init_style(key):
            styles=config[key]["styles"]
            return random.choice(styles)
        return Machines([{"key": key,
                          "seed": init_seed(key),
                          "style": init_style(key)}
                         for key in config])

    def __init__(self, machines):
        list.__init__(self, [Machine(machine)
                             for machine in machines])

    def clone(self):
        return Machines(self)

class Lfo(dict):

    def __init__(self, item):
        dict.__init__(self, item)

    def clone(self):
        return Lfo(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def render(self, nbeats, generator):
        generator.generate(n=nbeats,
                           q=Q(self["seed"]))
    
class Lfos(list):

    @classmethod
    def randomise(self, config=LfoConfig):
        def init_seed(key):
            return int(1e8*random.random())
        return Lfos([{"key": key,
                      "seed": init_seed(key)}
                     for key in config])

    def __init__(self, lfos):
        list.__init__(self, [Lfo(lfo)
                             for lfo in lfos])

    def clone(self):
        return Lfos(self)

        
class Slice(dict):

    @classmethod
    def randomise(self, pool):
        return Slice(samples=Samples.randomise(pool),
                     machines=Machines.randomise(),
                     lfos=Lfos.randomise())
    
    def __init__(self, samples, machines, lfos):
        dict.__init__(self, {"samples": Samples(samples),
                             "machines": Machines(machines),
                             "lfos": Lfos(lfos)})

    def clone(self):
        return Slice(samples=self["samples"].clone(),
                     machines=self["machines"].clone(),
                     lfos=self["lfos"].clone())
        
    def render_machine(self, notes, key, generator, nbeats, offset):
        genkwargs={"key": key,
                   "offset": offset,
                   "notes": notes,
                   "samples": self["samples"]}
        genkey=generator["generator"]
        genclass=eval(hungarorise("%s_generator" % genkey))
        geninstance=genclass(**genkwargs)
        machine={machine["key"]:machine
                 for machine in self["machines"]}[key]
        machine.render(nbeats, geninstance)

    def render_lfo(self, notes, key, generator, nbeats, offset):
        genkwargs={"key": key,
                   "offset": offset,
                   "notes": notes,
                   "range": [0, 1]}
        genkey=generator["generator"]
        genclass=eval(hungarorise("%s_generator" % genkey))
        geninstance=genclass(**genkwargs)
        lfo={lfo["key"]:lfo
             for lfo in self["lfos"]}[key]
        lfo.render(nbeats, geninstance)
            
class Slices(list):

    @classmethod
    def randomise(self, pool, n=4):
        return Slices([Slice.randomise(pool)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])

    def clone(self):
        return Slices(self)
    
class PatternMap(dict):

    @classmethod
    def randomise(self, slicetemp, patterns=Breakbeats, keys="kk|sn|ht|ec".split("|")):
        return PatternMap({key:patterns.randomise(slicetemp)
                           for key in keys})
    
    def __init__(self, item={}):
        dict.__init__(self, {k: Pattern(v)
                             for k, v in item.items()})

    def clone(self):
        return PatternMap(item=self)
        
class Tracks(dict):

    @classmethod
    def randomise(self, pool, slicetemp):
        return Tracks(slices=Slices.randomise(pool),
                      patterns=PatternMap.randomise(slicetemp))
        
    def __init__(self, slices, patterns):
        dict.__init__(self, {"slices": Slices(slices),
                             "patterns": PatternMap(patterns)})

    def clone(self):
        return Tracks(slices=self["slices"].clone(),
                      patterns=self["patterns"].clone())

    def randomise_pattern(self, limit, slicetemp, patterns=Breakbeats):
        for key in "kk|sn|ht".split("|"):
            if random.random() < limit:
                self["patterns"][key]=patterns.randomise(slicetemp)

    def shuffle_slices(self, limit):
        if random.random() < limit:
            random.shuffle(self["slices"])

    def render_machines(self, notes, nbeats, mutes,
                        config=MachineConfig):
        for key, generator in config.items():
            if key not in mutes:
                pattern=self["patterns"][key]
                multiplier=int(nbeats/pattern.size)
                offset=0
                for item in pattern.expanded:
                    slice=self["slices"][item["i"]]
                    nsamplebeats=item["n"]*multiplier
                    slice.render_machine(notes, key, generator, nsamplebeats, offset)
                    offset+=nsamplebeats

    def render_lfos(self, notes, nbeats,
                    config=LfoConfig):
        for key, generator in config.items():
            pattern=self["patterns"][key]
            multiplier=int(nbeats/pattern.size)
            offset=0
            for item in pattern.expanded:
                slice=self["slices"][item["i"]]
                nsamplebeats=item["n"]*multiplier
                slice.render_lfo(notes, key, generator, nsamplebeats, offset)
                offset+=nsamplebeats
                    
    def render(self, nbeats, mutes):
        notes={}
        self.render_machines(notes, nbeats, mutes)
        self.render_lfos(notes, nbeats)
        return notes

"""
- mutes is an empty list by default, overrideable at runtime by cli
"""
    
class Patch(dict):

    @classmethod
    def randomise(self, pool, slicetemp):
        return Patch(tracks=Tracks.randomise(pool,
                                             slicetemp))
    
    def __init__(self, tracks, mutes=[]):
        dict.__init__(self, {"tracks": Tracks(**tracks),
                             "mutes": mutes})

    def clone(self):
        return Patch(tracks=self["tracks"].clone(),
                     mutes=list(self["mutes"]))

    def mutate(self, limits, slicetemp):
        self["tracks"].randomise_pattern(limits["pat"], slicetemp)
        self["tracks"].shuffle_slices(limits["slices"])
        for slice in self["tracks"]["slices"]:
            for machine in slice["machines"]:
                machine.randomise_style(limits["style"])
                machine.randomise_seed(limits["seed"])
            for lfo in slice["lfos"]:
                lfo.randomise_seed(limits["seed"])
        return self
    
    def render(self, nbeats):
        return {"n": nbeats,
                "tracks": list(self["tracks"].render(nbeats=nbeats,
                                                     mutes=self["mutes"]).values())}
        
class Patches(list):

    @classmethod
    def randomise(self, pool, slicetemp, n):
        return Patches([Patch.randomise(pool,
                                        slicetemp)
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
            for track in patch.render(nbeats)["tracks"]:
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
