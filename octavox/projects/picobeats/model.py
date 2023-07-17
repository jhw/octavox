from rv.modules.echo import Echo as RVEcho
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.modules.sampler import SVSampler
from octavox.modules.project import SVProject

import octavox.modules.patterns.vitling909 as vitling

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

SequencerConfig=yaml.safe_load("""
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
    - note that sample keys are different from sequencer keys (oh/ch vs ht), so patches should contain unrestricted set
    """
    
    @classmethod
    def randomise(self, pool):
        return Samples(pool.randomise())

    def __init__(self, obj):
        dict.__init__(self, obj)

    def clone(self):
        return Samples(self)
        
class BeatMachine:

    def __init__(self, mod, key, samples, volume=1):
        self.mod=mod
        self.key=key
        self.samples=samples
        self.volume=volume

    def generate(self, style, q, n, notes, offset):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i, notes, offset)

    def handle(fn):
        def wrapped(self, q, i, notes, offset, **kwargs):
            v=fn(self, q, i, notes, offset, **kwargs)
            if v!=None: # explicit because could return zero
                samplekey, volume = v
                trig={"mod": self.mod,
                      "key": self.samples[samplekey],
                      "vel": self.volume*volume,
                      "i": i+offset}
                notes.setdefault(self.key, [])
                notes[self.key].append(trig)
        return wrapped
    
    @handle
    def fourfloor(self, q, i, notes, offset, k=Kick):
        return vitling.fourfloor(q, i, k)
    @handle
    def electro(self, q, i, notes, offset, k=Kick):
        return vitling.electro(q, i, k)
    @handle
    def triplets(self, q, i, notes, offset, k=Kick):
        return vitling.triplets(q, i, k)
    @handle
    def backbeat(self, q, i, notes, offset, k=Snare):
        return vitling.backbeat(q, i, k)
    @handle
    def skip(self, q, i, notes, offset, k=Snare):
        return vitling.skip(q, i, k)
    @handle
    def offbeats(self, q, i, notes, offset,
                 ko=OpenHat,
                 kc=ClosedHat):
        return vitling.offbeats(q, i, ko, kc)    
    @handle
    def closed(self, q, i, notes, offset, k=ClosedHat):
        return vitling.closed(q, i, k)

class SampleAndHoldMachine:

    def __init__(self, key, range, mod, ctrl, increment, step):
        self.key=key
        self.range=range
        self.mod=mod
        self.ctrl=ctrl
        self.increment=increment
        self.step=step
    
    def generate(self, q, n, notes, style="sample_hold"):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i, notes)

    def handle(fn):
        def wrapped(self, q, i, notes, **kwargs):
            v=fn(self, q, i, notes, **kwargs)
            if v!=None: # explicit because could return zero
                trig={"mod": self.mod,
                      "ctrl": self.ctrl,
                      "v": v,
                      "i": i}
                notes.setdefault(self.key, [])
                notes[self.key].append(trig)
        return wrapped

    @handle
    def sample_hold(self, q, i, notes):
        if 0 == i % self.step:
            floor, ceil = self.range
            v0=floor+(ceil-floor)*q.random()
            return self.increment*int(0.5+v0/self.increment)
            
class Sequencer(dict):

    def __init__(self, item):
        dict.__init__(self, item)

    def clone(self):
        return Sequencer(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def randomise_style(self, limit, config=SequencerConfig):
        styles=config[self["key"]]["styles"]
        if random.random() < limit:
            self["style"]=random.choice(styles)

    def render(self, nbeats, machine, notes, offset):
        machine.generate(n=nbeats,
                         q=Q(self["seed"]),
                         style=self["style"],
                         notes=notes,
                         offset=offset)
    
class Sequencers(list):

    @classmethod
    def randomise(self, config=SequencerConfig):
        def init_seed(key):
            return int(1e8*random.random())
        def init_style(key):
            styles=config[key]["styles"]
            return random.choice(styles)
        return Sequencers([{"key": key,
                            "seed": init_seed(key),
                            "style": init_style(key)}
                           for key in config])

    def __init__(self, sequencers):
        list.__init__(self, [Sequencer(sequencer)
                             for sequencer in sequencers])

    def clone(self):
        return Sequencers(self)

class Lfo(dict):

    def __init__(self, item):
        dict.__init__(self, item)

    def clone(self):
        return Lfo(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def render(self, nbeats, machine, notes):
        machine.generate(n=nbeats,
                         q=Q(self["seed"]),
                         notes=notes)
    
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
                     sequencers=Sequencers.randomise())
    
    def __init__(self, samples, sequencers):
        dict.__init__(self, {"samples": Samples(samples),
                             "sequencers": Sequencers(sequencers)})

    def clone(self):
        return Slice(samples=self["samples"].clone(),
                     sequencers=self["sequencers"].clone())

    @property
    def sequencer_map(self):
        return {sequencer["key"]:sequencer
                for sequencer in self["sequencers"]}
     
    def render_sequencer(self, mod, notes, key, nbeats, offset):
        machine=BeatMachine(mod=mod,
                            key=key,
                            samples=self["samples"])
        sequencer=self.sequencer_map[key]
        sequencer.render(nbeats=nbeats,
                         machine=machine,
                         notes=notes,
                         offset=offset)

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
    def randomise(self, slicetemp, patterns=Breakbeats, config=SequencerConfig):
        return PatternMap({key:patterns.randomise(slicetemp)
                           for key in config})
    
    def __init__(self, item={}):
        dict.__init__(self, {k: Pattern(v)
                             for k, v in item.items()})

    def clone(self):
        return PatternMap(item=self)
        
class Tracks(dict):

    @classmethod
    def randomise(self, pool, slicetemp):
        return Tracks(slices=Slices.randomise(pool),
                      patterns=PatternMap.randomise(slicetemp),
                      lfos=Lfos.randomise())
        
    def __init__(self, slices, patterns, lfos):
        dict.__init__(self, {"slices": Slices(slices),
                             "patterns": PatternMap(patterns),
                             "lfos": Lfos(lfos)})

    def clone(self):
        return Tracks(slices=self["slices"].clone(),
                      patterns=self["patterns"].clone(),
                      lfos=self["lfos"].clone())

    def randomise_pattern(self, limit, slicetemp, patterns=Breakbeats, config=SequencerConfig):
        for key in config:
            if random.random() < limit:
                self["patterns"][key]=patterns.randomise(slicetemp)

    def shuffle_slices(self, limit):
        if random.random() < limit:
            random.shuffle(self["slices"])
            
    def render_sequencers(self, notes, nbeats, mutes,
                        config=SequencerConfig):
        for key, item in config.items():
            if key not in mutes:
                pattern=self["patterns"][key]
                multiplier=int(nbeats/pattern.size)
                offset=0
                for pat in pattern.expanded:
                    slice=self["slices"][pat["i"]]
                    nsamplebeats=pat["n"]*multiplier
                    slice.render_sequencer(mod=item["mod"],
                                           notes=notes,
                                           key=key,
                                           nbeats=nsamplebeats,
                                           offset=offset)
                    offset+=nsamplebeats

    @property
    def lfo_map(self):
        return {lfo["key"]:lfo
                for lfo in self["lfos"]}

    def render_lfos(self, notes, nbeats,
                    config=LfoConfig):
        for key, item in config.items():
            machine=SampleAndHoldMachine(mod=item["mod"],
                                         ctrl=item["ctrl"],
                                         range=item["range"],
                                         increment=item["increment"],
                                         step=item["step"],
                                         key=key)
            lfo=self.lfo_map[key]
            lfo.render(nbeats=nbeats,
                       machine=machine,
                       notes=notes)

                    
    def render(self, nbeats, mutes):
        notes={}
        self.render_sequencers(notes=notes,
                               nbeats=nbeats,
                               mutes=mutes)
        self.render_lfos(notes=notes,
                         nbeats=nbeats)
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
            for sequencer in slice["sequencers"]:
                sequencer.randomise_style(limits["style"])
                sequencer.randomise_seed(limits["seed"])
        for lfo in self["tracks"]["lfos"]:
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
