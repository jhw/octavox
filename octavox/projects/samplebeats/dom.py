from rv.modules.drumsynth import DrumSynth as RVDrumSynth
from rv.modules.echo import Echo as RVEcho
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.modules.sampler import SVSampler
from octavox.modules.renderer import SVProject

import copy, json, math, os, random, yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

ModConfig=yaml.safe_load("""
modules:
  - name: Sampler
    # class: RVSampler
    class: SVSampler
    position:
      x: -3
      y: -1
  - name: Drum
    class: RVDrumSynth
    position:
      x: -3
      y: 1
  - name: Echo
    class: RVEcho
    position:
      x: -3
    defaults:
      dry: 128
      wet: 128
      delay: 192
  - name: Distortion
    class: RVDistortion
    position:
      x: -2
    defaults:
      power: 64
  - name: Reverb
    class: RVReverb
    position:
      x: -1
    defaults:
      wet: 4
links:
  - - Sampler
    - Echo
  - - Drum
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

class Pattern(list):

    @classmethod
    def initialise(self, pattern):
        def parse_chunk(chunk):
            tokens=[int(tok)
                    for tok in chunk.split("x")]
            if len(tokens)==1:
                tokens=[1, tokens[0]]
            return {k:v for k, v in zip("ni", tokens)}
        return Pattern([parse_chunk(chunk)
                        for chunk in pattern.split("|")])
        
    def __init__(self, items=[]):
        list.__init__(self, items)

    @property
    def size(self):
        return sum([item["n"]
                    for item in self])

class Patterns(list):

    def __init__(self, items=[]):
        list.__init__(self, items)

    def randomise(self, slicetemp):
        n=1+math.floor(slicetemp*len(self))
        return random.choice(self[:n])  
        
SlicePatterns=Patterns([Pattern.initialise(pat)
                        for pat in ["0",
                                    "0|1",
                                    "3x0|1",
                                    "0|1|0|1",
                                    "0|1|0|2",
                                    "0|1|2|3"]])

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

def hungarorise(text):
    return "".join([tok.capitalize()
                    for tok in text.split("_")])

class SampleKey:

    Drum, SVDrum, Sampler = "Drum", "svdrum", "Sampler"
    
    def __init__(self, value):
        self.value=value

    def expand(self):
        tokens=self.value.split(":")
        name, id = tokens[0], int(tokens[1])
        if tokens[0]==self.SVDrum:
            return {"mod": self.Drum,
                    "id": id}
        else:
            return {"mod": self.Sampler,
                    "key": {"bank": name,
                            "id": id}}

class Samples(dict):

    @classmethod
    def randomise(self, randomisers):
        return Samples(randomisers["samples"].randomise())

    def __init__(self, obj):
        dict.__init__(self, obj)

    def randomise_samples(self, samples):
        for key in self.keys():
            self[key]=random.choice(samples[key])

"""
- https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
"""
        
class VitlingGenerator:
    
    def __init__(self, key, offset, samples, volume=1):
        self.key=key
        self.offset=offset
        self.samples={k: SampleKey(v).expand()
                      for k, v in samples.items()}
        self.volume=volume

    def generate(self, notes, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(notes, q, i)
        
    def add(self, notes, k, i, v):
        samplekey, volume = v
        trig=dict(self.samples[samplekey])
        trig["vel"]=self.volume*volume
        trig["i"]=i+self.offset
        notes.setdefault(k, [])
        notes[k].append(trig)

    def fourfloor(self, notes, q, i, k=Kick):
        if i % 4 == 0:
            self.add(notes, self.key, i, (k, 0.9))
        elif i % 2 == 0 and q.random() < 0.1:
            self.add(notes, self.key, i, (k, 0.6))

    def electro(self, notes, q, i, k=Kick):
        if i == 0:
            self.add(notes, self.key, i, (k, 1))
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5) or
              q.random() < 0.05):
            self.add(notes, self.key, i, (k, 0.9*q.random()))

    def triplets(self, notes, q, i, k=Kick):
        if i % 16  in [0, 3, 6, 9, 14]:
           self.add(notes, self.key, i, (k, 1))
           
    def backbeat(self, notes, q, i, k=Snare):
        if i % 8 == 4:
            self.add(notes, self.key, i, (k, 1))

    def skip(self, notes, q, i, k=Snare):
        if i % 8 in [3, 6]:
            self.add(notes, self.key, i, (k, 0.6+0.4*q.random()))
        elif i % 2 == 0 and q.random() < 0.2:
            self.add(notes, self.key, i, (k, 0.4+0.2*q.random()))
        elif q.random() < 0.1:
            self.add(notes, self.key, i, (k, 0.2+0.2*q.random()))

    def offbeats(self, notes, q, i,
                 ko=OpenHat,
                 kc=ClosedHat):
        if i % 4 == 2:
            self.add(notes, self.key, i, (ko, 0.4))
        elif q.random() < 0.3:
            k=ko if q.random() < 0.5 else kc
            self.add(notes, self.key, i, (kc, 0.2*q.random()))

    def closed(self, notes, q, i, k=ClosedHat):
        if i % 2 == 0:
            self.add(notes, self.key, i, (k, 0.4))
        elif q.random() < 0.5:
            self.add(notes, self.key, i, (k, 0.3*q.random()))

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
        trig={"mod": self.mod,
              "ctrl": k,
              "v": v,
              "i": i+self.offset}
        notes.setdefault(k, [])
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

class Slice(dict):

    @classmethod
    def randomise(self, keys, randomisers):
        return Slice(samples=Samples.randomise(randomisers),
                     machines=Machines.randomise(keys))
    
    def __init__(self, samples, machines):
        dict.__init__(self, {"samples": Samples(samples),
                             "machines": Machines(machines)})

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
        return {"ranges": {"wet": [0, 0.75],
                           "feedback": [0.25, 0.75]}}
            
    def render(self, key, genkey, notes, nbeats, offset):
        genkwargsfn=getattr(self, "%s_kwargs" % genkey)
        genkwargs=genkwargsfn(key, offset)
        genclass=eval(hungarorise("%s_generator" % genkey))
        generator=genclass(**genkwargs)
        machine={machine["key"]:machine
                 for machine in self["machines"]}[key]
        machine.render(notes, nbeats, generator)
            
class Slices(list):

    @classmethod
    def randomise(self, keys, randomisers, n=4):
        return Slices([Slice.randomise(keys, randomisers)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])
        
class PatternMap(dict):

    @classmethod
    def randomise(self, keys, slicetemp, patterns=SlicePatterns):
        return PatternMap({key:patterns.randomise(slicetemp)
                           for key in keys})
    
    def __init__(self, item={}):
        dict.__init__(self, {k: Pattern(v)
                             for k, v in item.items()})
    
class Tracks(dict):

    @classmethod
    def randomise(self, keys, randomisers, slicetemp):
        return Tracks(slices=Slices.randomise(keys, randomisers),
                      patterns=PatternMap.randomise(keys, slicetemp))
        
    def __init__(self, slices, patterns):
        dict.__init__(self, {"slices": Slices(slices),
                             "patterns": PatternMap(patterns)})

    def randomise_pattern(self, limit, slicetemp, patterns=SlicePatterns):
        for key in self["patterns"]:
            if random.random() < limit:
                self["patterns"][key]=patterns.randomise(slicetemp)

    def render(self, patch, nbeats, config=MachineConfig):
        notes={}
        for key in sorted(self["patterns"]):
            genkey=config[key]["generator"]
            pattern=self["patterns"][key]
            multiplier=int(nbeats/pattern.size)
            offset=0
            for item in pattern:
                slice=self["slices"][item["i"]]
                nsamplebeats=item["n"]*multiplier
                slice.render(key, genkey, notes, nsamplebeats, offset)
                offset+=nsamplebeats
        patch["tracks"]+=list(notes.values())
                
class Patch(dict):

    @classmethod
    def randomise(self, keys, randomisers, slicetemp):
        return Patch(tracks=Tracks.randomise(keys, randomisers, slicetemp))
    
    def __init__(self, tracks):
        dict.__init__(self, {"tracks": Tracks(**tracks)})

    def clone(self):
        return copy.deepcopy(self)

    def render(self, nbeats):
        patch={"n": nbeats,
               "tracks": []}
        self["tracks"].render(patch, nbeats)
        return patch
        
class Patches(list):

    @classmethod
    def randomise(self, keys, randomisers, slicetemp, n):
        return Patches([Patch.randomise(keys,
                                        randomisers,
                                        slicetemp)
                        for i in range(n)])
    
    def __init__(self, patches):
        list.__init__(self, [Patch(**patch)
                             for patch in patches])

    def filter_samples(self, I):
        samples={}
        for i in I:
            for slice in self[i]["tracks"]["slices"]:
                for k, v in slice["samples"].items():
                    samples.setdefault(k, set())
                    samples[k].add(v)
        return {k:list(v)
                for k, v in samples.items()}
        
    """
    - json dumps/loads to remove classes which yaml won't render by default
    """
    
    def to_yaml(self):
        return yaml.safe_dump(json.loads(json.dumps(self)), 
                              default_flow_style=False)
    
    def render(self, banks, nbeats, filestub,
               nbreaks=0,
               modconfig=ModConfig):
        for path in ["tmp",
                     "tmp/samplebeats",
                     "tmp/samplebeats/projects",
                     "tmp/samplebeats/patches"]:
            if not os.path.exists(path):
                os.makedirs(path)
        patches=[patch.render(nbeats=nbeats)
                 for patch in self]
        modclasses={mod["class"]:eval(mod["class"])
                    for mod in modconfig["modules"]}
        project=SVProject().render(patches=patches,
                                   modconfig=modconfig,
                                   modclasses=modclasses,
                                   banks=banks,
                                   nbreaks=nbreaks)
        projfile="tmp/samplebeats/projects/%s.sunvox" % filestub
        with open(projfile, 'wb') as f:
            project.write_to(f)
        patchfile="tmp/samplebeats/patches/%s.yaml" % filestub
        with open(patchfile, 'w') as f:
            f.write(self.to_yaml())
    
if __name__=="__main__":
    pass
