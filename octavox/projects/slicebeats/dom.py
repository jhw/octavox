from octavox.projects.slicebeats.project import SVProject

import copy, json, os, random, yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

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
# ht:
#   generator: vitling
#   styles:
#   - offbeats
#   - closed
""")

SVDrum, Drum, Sampler = "svdrum", "Drum", "Sampler"

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

def hungarorise(text):
    return "".join([tok.capitalize()
                    for tok in text.split("_")])

class SampleKey:

    def __init__(self, value):
        self.value=value

    def expand(self):
        tokens=self.value.split(":")
        name, id = tokens[0], int(tokens[1])
        if tokens[0]==SVDrum:
            return {"mod": Drum,
                    "id": id}
        else:
            return {"mod": Sampler,
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
    
    def __init__(self, key, samples, offset=0, volume=1):
        self.key=key
        self.samples={k: SampleKey(v).expand()
                      for k, v in samples.items()}
        self.offset=offset
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

class Machine(dict):

    def __init__(self, items):
        dict.__init__(self, items)

    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def randomise_style(self, limit, config=MachineConfig):
        if random.random() < limit:
            styles=config[self["key"]]["styles"]
            self["style"]=random.choice(styles)

    def render(self, notes, nbeats, generator):
        generator.generate(notes=notes,
                           n=nbeats,
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
        return Machines([{"seed": init_seed(key),
                          "style": init_style(key),
                          "key": key}
                         for key in config])

    def __init__(self, machines):
        list.__init__(self, [Machine(machine)
                             for machine in machines])

class Slice(dict):

    @classmethod
    def randomise(self, randomisers):
        return Slice(samples=Samples.randomise(randomisers),
                     machines=Machines.randomise())
    
    def __init__(self, samples, machines):
        dict.__init__(self, {"samples": Samples(samples),
                             "machines": Machines(machines)})

    def render(self, config, notes, nbeats, offset):
        def vitling_kwargs(self, key, offset, volume=1):
            return {"key": key,
                    "samples": self["samples"],
                    "offset": offset,
                    "volume": volume}
        machines={machine["key"]: machine
                  for machine in self["machines"]}
        for key in config:
            genkey=config[key]["generator"]
            genkwargsfn=eval("%s_kwargs" % genkey)
            genkwargs=genkwargsfn(self, key, offset)
            genclass=eval(hungarorise("%s_generator" % genkey))
            generator=genclass(**genkwargs)
            machine=machines[key]
            machine.render(notes, nbeats, generator)
            
class Slices(list):

    @classmethod
    def randomise(self, randomisers, n=4):
        return Slices([Slice.randomise(randomisers)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])
        
class Tracks(dict):

    Patterns=[[0],
              [0, 1],
              [0, 0, 0, 1],
              [0, 1, 0, 2],
              [0, 1, 2, 3]]

    @classmethod
    def randomise(self, randomisers):
        return Tracks(slices=Slices.randomise(randomisers),
                      pattern=random.choice(self.Patterns))
        
    def __init__(self, slices, pattern):
        dict.__init__(self, {"slices": Slices(slices),
                             "pattern": pattern})

    def randomise_pattern(self, limit):
        if random.random() < limit:
            self["pattern"]=random.choice(self.Patterns)

    def render(self, struct, nbeats, config=MachineConfig):
        notes={}
        for i_offset, i_slice in enumerate(self["pattern"]):
            offset=i_offset*nbeats
            slice=self["slices"][i_slice]
            slice.render(config, notes, nbeats, offset)                         
        struct["tracks"]+=list(notes.values())
                
    @property
    def n_slices(self):
        return len(self["pattern"])

class Patch(dict):

    @classmethod
    def randomise(self, randomisers, controllers):
        return Patch(tracks=Tracks.randomise(randomisers))
    
    def __init__(self, tracks):
        dict.__init__(self, {"tracks": Tracks(**tracks)})

    def clone(self):
        return copy.deepcopy(self)

    def render(self, nbeats):
        struct={"n": nbeats,
                "tracks": []}
        nslices=self["tracks"].n_slices
        nslicebeats=int(nbeats/nslices)
        self["tracks"].render(struct, nslicebeats)
        return struct
        
class Patches(list):

    @classmethod
    def randomise(self, randomisers, controllers, n):
        return Patches([Patch.randomise(randomisers,
                                        controllers)
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
    
    def render(self, filestub, banks, nbeats):
        for path in ["tmp",
                     "tmp/slicebeats",
                     "tmp/slicebeats/projects",
                     "tmp/slicebeats/patches"]:
            if not os.path.exists(path):
                os.makedirs(path)
        project=SVProject().render(banks,
                                   [patch.render(nbeats=nbeats)
                                   for patch in self])        
        projfile="tmp/slicebeats/projects/%s.sunvox" % filestub
        with open(projfile, 'wb') as f:
            project.write_to(f)
        patchfile="tmp/slicebeats/patches/%s.yaml" % filestub
        with open(patchfile, 'w') as f:
            f.write(self.to_yaml())
    
if __name__=="__main__":
    pass
