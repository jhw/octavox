from rv.modules.echo import Echo as RVEcho
from rv.modules.eq import Eq as RVEqualiser
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.modules.sampler import SVSampler
from octavox.modules.project import SVProject

from octavox.projects.samplebeats.utils import *

import json, math, os, yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

ModConfig=yaml.safe_load("""
modules:
  - name: KKSampler
    classname: SVSampler
  - name: SNSampler
    classname: SVSampler
  - name: HTSampler
    classname: SVSampler
  - name: KKEqualiser
    classname: RVEqualiser
  - name: SNEqualiser
    classname: RVEqualiser
  - name: HTEqualiser
    classname: RVEqualiser
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
    - KKEqualiser
  - - SNSampler
    - SNEqualiser
  - - HTSampler
    - HTEqualiser
  - - KKEqualiser
    - Echo
  - - SNEqualiser
    - Echo
  - - HTEqualiser
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
ec:
  generator: sample_hold
  styles:
  - sample_hold
""")

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
    def randomise(self, randomiser):
        return Samples(randomiser.randomise())

    def __init__(self, obj):
        dict.__init__(self, obj)

    def clone(self):
        return Samples(self)

"""
- https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
"""
        
class VitlingGenerator:

    def __init__(self, key, offset, samples, volume=1):
        self.key=key
        self.offset=offset
        self.samples=samples
        self.volume=volume

    def generate(self, notes, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(notes, q, i)

    def add(self, notes, q, k, i, v):
        notes.setdefault(k, [])
        samplekey, volume = v
        trig={"mod": "%sSampler" % k.upper(),              
              "key": self.samples[samplekey],
              "vel": self.volume*volume,
              "i": i+self.offset}
        notes[k].append(trig)

    def fourfloor(self, notes, q, i, k=Kick):
        if i % 4 == 0:
            self.add(notes, q, self.key, i, (k, 0.9))
        elif i % 2 == 0 and q.random() < 0.1:
            self.add(notes, q, self.key, i, (k, 0.6))

    def electro(self, notes, q, i, k=Kick):
        if i == 0:
            self.add(notes, q, self.key, i, (k, 1))
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5) or
              q.random() < 0.05):
            self.add(notes, q, self.key, i, (k, 0.9*q.random()))

    def triplets(self, notes, q, i, k=Kick):
        if i % 16  in [0, 3, 6, 9, 14]:
           self.add(notes, q, self.key, i, (k, 1))
           
    def backbeat(self, notes, q, i, k=Snare):
        if i % 8 == 4:
            self.add(notes, q, self.key, i, (k, 1))

    def skip(self, notes, q, i, k=Snare):
        if i % 8 in [3, 6]:
            self.add(notes, q, self.key, i, (k, 0.6+0.4*q.random()))
        elif i % 2 == 0 and q.random() < 0.2:
            self.add(notes, q, self.key, i, (k, 0.4+0.2*q.random()))
        elif q.random() < 0.1:
            self.add(notes, q, self.key, i, (k, 0.2+0.2*q.random()))

    def offbeats(self, notes, q, i,
                 ko=OpenHat,
                 kc=ClosedHat):
        if i % 4 == 2:
            self.add(notes, q, self.key, i, (ko, 0.4))
        elif q.random() < 0.3:
            k=ko if q.random() < 0.5 else kc
            self.add(notes, q, self.key, i, (kc, 0.2*q.random()))

    def closed(self, notes, q, i, k=ClosedHat):
        if i % 2 == 0:
            self.add(notes, q, self.key, i, (k, 0.4))
        elif q.random() < 0.5:
            self.add(notes, q, self.key, i, (k, 0.3*q.random()))

class SampleHoldGenerator:

    def __init__(self, key, offset, ranges,
                 mod="Echo",
                 inc=0.25,
                 step=4):
        self.key=key
        self.offset=offset
        self.ranges=ranges
        self.mod=mod
        self.inc=inc
        self.step=step
    
    def generate(self, notes, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(notes, q, i)

    def add(self, notes, k, i, v):
        notes.setdefault(k, [])
        trig={"mod": self.mod,
              "ctrl": k,
              "v": v,
              "i": i+self.offset}
        notes[k].append(trig)

    def sample_hold(self, notes, q, i):
        if 0 == i % self.step:
            for ctrl in "wet|feedback".split("|"):
                floor, ceil = self.ranges[ctrl]
                v0=floor+(ceil-floor)*q.random()
                v=self.inc*int(0.5+v0/self.inc)
                self.add(notes, ctrl, i, v)
            
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

    def render(self, notes, nbeats, generator):
        generator.generate(notes=notes,
                           n=nbeats,
                           q=Q(self["seed"]),
                           style=self["style"])
    
class Machines(list):

    @classmethod
    def randomise(self, keys, config=MachineConfig):
        def init_seed(key):
            return int(1e8*random.random())
        def init_style(key):
            styles=config[key]["styles"]
            return random.choice(styles)
        return Machines([{"key": key,
                          "seed": init_seed(key),
                          "style": init_style(key)}
                         for key in keys])

    def __init__(self, machines):
        list.__init__(self, [Machine(machine)
                             for machine in machines])

    def clone(self):
        return Machines(self)
        
class Slice(dict):

    @classmethod
    def randomise(self, keys, randomiser):
        return Slice(samples=Samples.randomise(randomiser),
                     machines=Machines.randomise(keys))
    
    def __init__(self, samples, machines):
        dict.__init__(self, {"samples": Samples(samples),
                             "machines": Machines(machines)})

    def clone(self):
        return Slice(samples=self["samples"].clone(),
                     machines=self["machines"].clone())
        
    def generator_kwargs(fn):
        def wrapped(self, key, offset):
            resp=fn(self, key, offset)
            resp.update({"key": key,
                         "offset": offset})
            return resp
        return wrapped

    @generator_kwargs
    def vitling_kwargs(self, key, offset):
        return {"samples": self["samples"]}

    @generator_kwargs
    def sample_hold_kwargs(self, key, offset):
        return {"ranges": {"wet": [0, 1],
                           "feedback": [0, 1]}}
            
    def render(self, notes, key, genkey, nbeats, offset):
        genkwargsfn=getattr(self, "%s_kwargs" % genkey)
        genkwargs=genkwargsfn(key, offset)
        genclass=eval(hungarorise("%s_generator" % genkey))
        generator=genclass(**genkwargs)
        machine={machine["key"]:machine
                 for machine in self["machines"]}[key]
        machine.render(notes, nbeats, generator)
            
class Slices(list):

    @classmethod
    def randomise(self, keys, randomiser, n=4):
        return Slices([Slice.randomise(keys, randomiser)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])

    def clone(self):
        return Slices(self)

    def shuffle_samples(self, limit):
        if random.random() < limit:
            samples=sorted([slice["samples"]
                            for slice in self],
                           key=lambda x: random.random())
            for slice, sampleset in zip(self, samples):
                slice["samples"]=sampleset
    
class PatternMap(dict):

    @classmethod
    def randomise(self, keys, slicetemp, patterns=Breakbeats):
        return PatternMap({key:patterns.randomise(slicetemp)
                           for key in keys})
    
    def __init__(self, item={}):
        dict.__init__(self, {k: Pattern(v)
                             for k, v in item.items()})

    def clone(self):
        return PatternMap(item=self)
        
class Tracks(dict):

    @classmethod
    def randomise(self, keys, mutes,  randomiser, slicetemp):
        return Tracks(keys=keys,
                      mutes=mutes,
                      slices=Slices.randomise(keys, randomiser),
                      patterns=PatternMap.randomise(keys, slicetemp))
        
    def __init__(self, keys, mutes, slices, patterns):
        dict.__init__(self, {"keys": keys,
                             "mutes": mutes,
                             "slices": Slices(slices),
                             "patterns": PatternMap(patterns)})

    def clone(self):
        return Tracks(keys=list(self["keys"]),
                      mutes=list(self["mutes"]),
                      slices=self["slices"].clone(),
                      patterns=self["patterns"].clone())

    def randomise_pattern(self, limit, slicetemp, patterns=Breakbeats):
        for key in self["keys"]:
            if random.random() < limit:
                self["patterns"][key]=patterns.randomise(slicetemp)

    def randomise_mutes(self, limit):
        self["mutes"]=[key for key in self["keys"]
                       if random.random() < limit
                       and key!="ec"]
                
    @property
    def renderkeys(self):
        return sorted([key for key in self["keys"]
                       if key not in self["mutes"]])
                
    def render(self, nbeats, config=MachineConfig):
        notes={}
        for key in self.renderkeys:
            genkey=config[key]["generator"]
            pattern=self["patterns"][key]
            multiplier=int(nbeats/pattern.size)
            offset=0
            for item in pattern.expanded:
                slice=self["slices"][item["i"]]
                nsamplebeats=item["n"]*multiplier
                slice.render(notes, key, genkey, nsamplebeats, offset)
                offset+=nsamplebeats
        return notes
                
class Patch(dict):

    @classmethod
    def randomise(self, keys, mutes, randomiser, slicetemp):
        return Patch(tracks=Tracks.randomise(keys,
                                             mutes,
                                             randomiser,
                                             slicetemp))
    
    def __init__(self, tracks):
        dict.__init__(self, {"tracks": Tracks(**tracks)})

    def clone(self):
        return Patch(tracks=self["tracks"].clone())

    def mutate(self, limits, slicetemp):
        self["tracks"].randomise_pattern(limits["pat"], slicetemp)
        self["tracks"].randomise_mutes(limits["mute"])
        self["tracks"]["slices"].shuffle_samples(limits["samples"])
        for slice in self["tracks"]["slices"]:
            for machine in slice["machines"]:
                machine.randomise_style(limits["style"])
                machine.randomise_seed(limits["seed"])
    
    def render(self, nbeats):
        struct={"n": nbeats,
               "tracks": []}
        struct["tracks"]+=list(self["tracks"].render(nbeats).values())
        return struct
        
class Patches(list):

    @classmethod
    def randomise(self, randomiser, slicetemp, n,
                  keys= "kk|sn|ht|ec".split("|"),
                  mutes=[]):
        return Patches([Patch.randomise(keys,
                                        mutes,
                                        randomiser,
                                        slicetemp)
                        for i in range(n)])
    
    def __init__(self, patches):
        list.__init__(self, [Patch(**patch)
                             for patch in patches])

    def sample_keys(self, nbeats):
        samplekeys={}
        for patch in self:
            for track in patch.render(nbeats)["tracks"]:
                for trig in track:
                    if "key" in trig:
                        key=trig["mod"][:2].lower() # change?
                        samplekeys.setdefault(key, set())
                        samplekeys[key].add(trig["key"])
        def sorter(key):
            tokens=key.split(":")
            return "%s%03d" % (tokens[0], int(tokens[1]))
        return {k:sorted(list(v),
                         key=sorter)
                for k, v in samplekeys.items()}

    def render(self, banks, nbeats, filename,
               nbreaks=0,
               modconfig=ModConfig):
        for path in ["tmp",
                     "tmp/samplebeats",
                     "tmp/samplebeats/projects",
                     "tmp/samplebeats/patches"]:
            if not os.path.exists(path):
                os.makedirs(path)
        samplekeys=self.sample_keys(nbeats)
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
        projfile="tmp/samplebeats/projects/%s.sunvox" % filename
        with open(projfile, 'wb') as f:
            project.write_to(f)
        patchfile="tmp/samplebeats/patches/%s.json" % filename
        with open(patchfile, 'w') as f:
            f.write(json.dumps(self,
                               indent=2))
    
if __name__=="__main__":
    pass
