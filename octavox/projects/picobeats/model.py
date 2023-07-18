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
- key: kk
  mod: KKSampler
  styles:
  - fourfloor
  - electro
  - triplets
- key: sn
  mod: SNSampler
  styles:
  - backbeat
  - skip
- key: ht
  mod: HTSampler
  styles:
  - offbeats
  - closed
""")

LfoConfig=yaml.safe_load("""
- key: ec0
  mod: Echo
  ctrl: wet
  range: [0, 1]
  increment: 0.25
  step: 4
- key: ec1
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
        
class Track(dict):

    """
    - should Track() be used here, as is also used by contstructor?
    """
       
    @classmethod
    def randomise(self, params):
        return Track({"key": params["key"],
                      "seed": int(1e8*random.random()),
                      "style": random.choice(params["styles"])})

    """
    - volume, pattern, samples, slices
    """
    
    def __init__(self, item,
                 config={params["key"]: params
                         for params in TrackConfig},
                 volume=1):
        dict.__init__(self, item)
        for attr in params[item["key"]]:
            if attr!="key":
                setattr(self, attr, params[attr])
        self.volume=1
                
    def clone(self):
        return Track(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def randomise_style(self, limit,
                        config={params["key"]: params
                                for params in TrackConfig}):
        styles=config[self["key"]]["styles"]
        if random.random() < limit:
            self["style"]=random.choice(styles)

    """
    - START MACHINE CODE
    """

    def generate(self, style, q, n, notes, offset, samples):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i, notes, offset, samples)

    def apply(fn):
        def wrapped(self, q, i, notes, offset, samples):
            v=fn(self, q, i, notes, offset, samples)
            if v!=None: # explicit because could return zero
                samplekey, volume = v
                trig={"mod": self.mod,
                      "key": samples[samplekey],
                      "vel": self.volume*volume,
                      "i": i+offset}
                notes.setdefault(self.key, [])
                notes[self.key].append(trig)
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

    """
    - END MACHINE CODE
    """

    """
    - render needs to iterate over slices
    - possibly using old tracks render_sequencer code
    """
    
    def render(self, nbeats, params, notes, samples, offset=0):
        BeatMachine(**params).generate(n=nbeats,
                                       q=Q(self["seed"]),
                                       style=self["style"],
                                       notes=notes,
                                       offset=offset,
                                       samples=samples)
    
class Tracks(list):

    @classmethod
    def randomise(self, config=TrackConfig):
        return Tracks([Track.randomise(params)
                       for params in config])

    def __init__(self, tracks):
        list.__init__(self, [Track(track)
                             for track in tracks])

    def clone(self):
        return Tracks(self)

class Lfo(dict):

    """
    - should Lfo() be used here, as is also used by contstructor?
    """

    @classmethod
    def randomise(self, params):
        return Lfo({"key": params["key"],
                    "seed": int(1e8*random.random())})
    
    def __init__(self, item):
        dict.__init__(self, item)

    def __init__(self, item, config={params["key"]: params
                                     for params in LfoConfig}):
        dict.__init__(self, item)
        for attr in params[item["key"]]:
            if attr!="key":
                setattr(self, attr, params[attr])
        
    def clone(self):
        return Lfo(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    """
    - START MACHINE CODE
    """

    def generate(self, q, n, notes):
        for i in range(n):
            self.sample_hold(q, i, notes)

    def apply(fn):
        def wrapped(self, q, i, notes):
            v=fn(self, q, i, notes)
            if v!=None: # explicit because could return zero
                trig={"mod": self.mod,
                      "ctrl": self.ctrl,
                      "v": v,
                      "i": i}
                notes.setdefault(self.key, [])
                notes[self.key].append(trig)
        return wrapped

    @apply
    def sample_hold(self, q, i, *args):
        if 0 == i % self.step:
            floor, ceil = self.range
            v0=floor+(ceil-floor)*q.random()
            return self.increment*int(0.5+v0/self.increment)
    
    """
    - END MACHINE CODE
    """
        
            
    def render(self, params, nbeats, notes):
        SampleAndHoldMachine(**params).generate(n=nbeats,
                                                q=Q(self["seed"]),
                                                notes=notes)    
class Lfos(list):

    @classmethod
    def randomise(self, config=LfoConfig):
        return Lfos([Lfo.randomise(params)
                     for params in config])

    def __init__(self, lfos):
        list.__init__(self, [Lfo(lfo)
                             for lfo in lfos])

    def clone(self):
        return Lfos(self)

class Patch(dict):

    @classmethod
    def randomise(self, pool):
        return Patch(tracks=Tracks.randomise(pool),
                     lfos=Lfos.randomise())
        
    def __init__(self, tracks, lfos):
        dict.__init__(self, {"tracks": Tracks(tracks),
                             "lfos": Lfos(lfos)})
        
    def clone(self):
        return Patch(tracks=self["tracks"].clone(),
                    lfos=self["lfos"].clone())

    def render_tracks(self, notes, nbeats,
                      config={params["key"]:params
                              for params in TrackConfig}):
        for track in self["tracks"]:
            track.render(params=config[track["key"]],
                         nbeats=nbeats,
                         notes=notes)
                    
    def render_lfos(self, notes, nbeats,
                    config={params["key"]:params
                            for params in LfoConfig}):
        for lfo in self["lfos"]:
            lfo.render(params=config[lfo["key"]],
                       nbeats=nbeats,
                       notes=notes)

    """
    def render(self, nbeats):
        return {"n": nbeats,
                "tracks": list(self["tracks"].render(nbeats=nbeats,
                                                     mutes=self["mutes"]).values())}
    """
                                
    def render(self, nbeats, mutes):
        notes={}
        self.render_tracks(notes=notes,
                           nbeats=nbeats)
        self.render_lfos(notes=notes,
                         nbeats=nbeats)
        return notes

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
