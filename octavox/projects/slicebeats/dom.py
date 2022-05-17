from octavox.projects.slicebeats.project import SVProject

import copy, json, os, random, yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

FourFloor, Electro, Triplets, Backbeat, Skip, Offbeats, OffbeatsOpen, OffbeatsClosed, Closed = "fourfloor", "electro", "triplets", "backbeat", "skip", "offbeats", "offbeats_open", "offbeats_closed", "closed"

KickStyles, SnareStyles, HatsStyles = [FourFloor, Electro, Triplets], [Backbeat, Skip], [Offbeats, Closed]

MachineMapping={Kick: "kick",
                Snare: "snare"}

SVDrum, Drum, Sampler = "svdrum", "Drum", "Sampler"

TrigType, FXType = "trig", "fx"
            
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

class Notes(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def expand(self):
        tracks, types = {}, {}
        for i, note in self.items():
            key="%s/%s" % (note["name"],
                           note["type"])
            tracks.setdefault(key, {})
            tracks[key][i]=note
            types[key]=note["type"]
        return [{"notes": v,
                 "type": types[k]}
                for k, v in tracks.items()
                if v!=[]]
    
"""
- https://github.com/beats/acid-banger/blob/main/src/pattern.ts
"""
        
class TrigGenerator(dict):
    
    def __init__(self, key, samples, offset=0, volume=1):
        dict.__init__(self)
        self.key=key
        self.samples={k: SampleKey(v).expand()
                      for k, v in samples.items()}
        self.offset=offset
        self.volume=volume

    def generate(self, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)
        return self
        
    def add(self, k, i, v):
        samplekey, volume = v
        trig=dict(self.samples[samplekey])
        trig["name"]=k
        trig["vel"]=self.volume*volume
        trig["type"]=TrigType
        self[i+self.offset]=trig

    def fourfloor(self, q, i, k=Kick):
        if i % 4 == 0:
            self.add(self.key, i, (k, 0.9))
        elif i % 2 == 0 and q.random() < 0.1:
            self.add(self.key, i, (k, 0.6))

    def electro(self, q, i, k=Kick):
        if i == 0:
            self.add(self.key, i, (k, 1))
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5) or
              q.random() < 0.05):
            self.add(self.key, i, (k, 0.9*q.random()))

    def triplets(self, q, i, k=Kick):
        if i % 16  in [0, 3, 6, 9, 14]:
           self.add(self.key, i, (k, 1))
           
    def backbeat(self, q, i, k=Snare):
        if i % 8 == 4:
            self.add(self.key, i, (k, 1))

    def skip(self, q, i, k=Snare):
        if i % 8 in [3, 6]:
            self.add(self.key, i, (k, 0.6+0.4*q.random()))
        elif i % 2 == 0 and q.random() < 0.2:
            self.add(self.key, i, (k, 0.4+0.2*q.random()))
        elif q.random() < 0.1:
            self.add(self.key, i, (k, 0.2+0.2*q.random()))

    """
    - offbeats_open/closed must pre- define random variables to ensure they always remain in sync
    - ie don't nest one call to `q.random()` inside another
    """
            
    def offbeats_open(self, q, i, k=OpenHat):
        q0, q1 = q.random(), q.random()
        if i % 4 == 2:
            self.add(self.key, i, (k, 0.4))
        elif q0 < 0.15:
            self.add(self.key, i, (k, 0.2*q1))

    def offbeats_closed(self, q, i, k=ClosedHat):
        q0, q1 = q.random(), q.random()
        if 0.15 < q0 < 0.3:
            self.add(self.key, i, (k, 0.2*q1))

    def closed(self, q, i, k=ClosedHat):
        if i % 2 == 0:
            self.add(self.key, i, (k, 0.4))
        elif q.random() < 0.5:
            self.add(self.key, i, (k, 0.3*q.random()))

    def empty(self, q, i):
        pass
            
class Machine(dict):

    def __init__(self, items):
        dict.__init__(self, items)

    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def randomise_style(self, limit, mapping=MachineMapping):
        styles=eval(hungarorise("%s_styles" % mapping[self["key"]]))
        if random.random() < limit:
            self["style"]=random.choice(styles)

    def render(self, struct, nbeats, generator):
        notes=generator.generate(n=nbeats,
                                 q=Q(self["seed"]),
                                 style=self["style"])
        struct.update(notes)
    
class Machines(list):

    @classmethod
    def randomise(self, mapping=MachineMapping):
        def init_seed(key, mapping):
            return int(1e8*random.random())
        def init_style(key, mapping):
            styles=eval(hungarorise("%s_styles" % mapping[key]))
            return random.choice(styles)
        return Machines([{"seed": init_seed(key, mapping),
                          "style": init_style(key, mapping),
                          "key": key}
                         for key in mapping])

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

    def render(self, keys, struct, nbeats, offset):
        def init_generator(key, samples, offset, volume=1):
            return TrigGenerator(key=key,
                                 samples=samples,
                                 offset=offset,
                                 volume=volume)                                
        machines={machine["key"]: machine
                  for machine in self["machines"]}
        for key in keys:
            machine=machines[key]
            generator=init_generator(key=key,
                                     samples=self["samples"],
                                     offset=offset)
            machine.render(struct, nbeats, generator)

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

    def render(self, struct, nbeats, keys=[Kick, Snare]):
        notes=Notes()
        for i_offset, i_slice in enumerate(self["pattern"]):
            offset=i_offset*nbeats
            slice=self["slices"][i_slice]
            slice.render(keys, notes, nbeats, offset)                         
        struct["tracks"]+=notes.expand()
                
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
