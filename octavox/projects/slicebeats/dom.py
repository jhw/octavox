from octavox.projects.slicebeats.project import SVProject

from collections import OrderedDict

import copy, json, os, random, yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

FourFloor, Electro, Triplets, Backbeat, Skip, Offbeats, OffbeatsOpen, OffbeatsClosed, Closed, Empty = "fourfloor", "electro", "triplets", "backbeat", "skip", "offbeats", "offbeats_open", "offbeats_closed", "closed", "empty"

KickStyles, SnareStyles, HatsStyles = [FourFloor, Electro, Triplets], [Backbeat, Skip], [Offbeats, Closed]

MachineMapping={Kick: "kick",
                Snare: "snare",
                Hats: "hats"}

PlayerKeys=[Kick, Snare, OpenHat, ClosedHat]

SVDrum, Drum, Sampler = "svdrum", "Drum", "Sampler"

SampleHold="sample_hold"

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

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
        
class MachineBase(dict):

    @classmethod
    def initialise(self, machine, mapping=MachineMapping):
        klass=eval("%sMachine" % mapping[machine["key"]].capitalize())
        return klass(machine)
    
    def __init__(self, items):
        dict.__init__(self, items)

    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def randomise_style(self, limit, mapping=MachineMapping):
        styles=eval("%sStyles" % mapping[self["key"]].capitalize())
        if random.random() < limit:
            self["style"]=random.choice(styles)
            
    @property
    def players(self):
        return [self]
    
class KickMachine(MachineBase):

    pass
                
class SnareMachine(MachineBase):

    pass
    
class HatsMachine(MachineBase):
    
    @property
    def substyles(self):
        return zip([OpenHat, ClosedHat],
                   [OffbeatsOpen, OffbeatsClosed] if self["style"]==Offbeats else [Closed, Empty])
                   
    @property
    def players(self):
        return [{"key": key,
                 "seed": self["seed"],
                 "style": substyle}
                for key, substyle in self.substyles]

class Machines(list):

    @classmethod
    def randomise(self, mapping=MachineMapping):
        def init_seed(key, mapping):
            return int(1e8*random.random())
        def init_style(key, mapping):
            styles=eval("%sStyles" % mapping[key].capitalize())
            return random.choice(styles)
        return Machines([{"seed": init_seed(key, mapping),
                          "style": init_style(key, mapping),
                          "key": key}
                         for key in mapping])

    def __init__(self, machines):
        list.__init__(self, [MachineBase.initialise(machine)
                             for machine in machines])

class Slice(dict):

    @classmethod
    def randomise(self, randomisers):
        return Slice(samples=Samples.randomise(randomisers),
                     machines=Machines.randomise())
    
    def __init__(self, samples, machines):
        dict.__init__(self, {"samples": Samples(samples),
                             "machines": Machines(machines)})

class Slices(list):

    @classmethod
    def randomise(self, randomisers, n=4):
        return Slices([Slice.randomise(randomisers)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])

"""
- https://github.com/beats/acid-banger/blob/main/src/pattern.ts
"""
        
class TrigGenerator(dict):
    
    def __init__(self, samples, offset=0, volume=1):
        dict.__init__(self)
        self.samples={k: SampleKey(v).expand()
                      for k, v in samples.items()}
        self.offset=offset
        self.volume=volume

    def generate(self, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)
        return self
        
    def add(self, i, v):
        trig=dict(self.samples[v[0]])
        trig["vel"]=v[1]*self.volume
        self[i+self.offset]=trig

    def fourfloor(self, q, i, k=Kick):
        if i % 4 == 0:
            self.add(i, (k, 0.9))
        elif i % 2 == 0 and q.random() < 0.1:
            self.add(i, (k, 0.6))

    def electro(self, q, i, k=Kick):
        if i == 0:
            self.add(i, (k, 1))
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5) or
              q.random() < 0.05):
            self.add(i, (k, 0.9*q.random()))

    def triplets(self, q, i, k=Kick):
        if i % 16  in [0, 3, 6, 9, 14]:
           self.add(i, (k, 1))
           
    def backbeat(self, q, i, k=Snare):
        if i % 8 == 4:
            self.add(i, (k, 1))

    def skip(self, q, i, k=Snare):
        if i % 8 in [3, 6]:
            self.add(i, (k, 0.6+0.4*q.random()))
        elif i % 2 == 0 and q.random() < 0.2:
            self.add(i, (k, 0.4+0.2*q.random()))
        elif q.random() < 0.1:
            self.add(i, (k, 0.2+0.2*q.random()))

    """
    - offbeats_open/closed must pre- define two random variables to ensure they always remain in sync
    - ie don't nest one call to `q.random()` inside another
    """
            
    def offbeats_open(self, q, i, k=OpenHat):
        q0, q1 = q.random(), q.random()
        if i % 4 == 2:
            self.add(i, (k, 0.4))
        elif q0 < 0.15:
            self.add(i, (k, 0.2*q1))

    def offbeats_closed(self, q, i, k=ClosedHat):
        q0, q1 = q.random(), q.random()
        if 0.15 < q0 < 0.3:
            self.add(i, (k, 0.2*q1))

    def closed(self, q, i, k=ClosedHat):
        if i % 2 == 0:
            self.add(i, (k, 0.4))
        elif q.random() < 0.5:
            self.add(i, (k, 0.3*q.random()))

    def empty(self, q, i):
        pass
        
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

    def render(self, struct, nbeats, volume=1, keys=PlayerKeys):
        notes={key: {} for key in keys}
        for i_offset, i_slice in enumerate(self["pattern"]):
            slice_=self["slices"][i_slice]
            offset=i_offset*nbeats
            generator=TrigGenerator(samples=slice_["samples"],
                                    offset=offset,
                                    volume=volume)
            for machine in slice_["machines"]:
                for player in machine.players:
                    values=generator.generate(n=nbeats,
                                              q=Q(player["seed"]),
                                              style=player["style"])
                    notes[player["key"]].update(values)
                    print (i_slice, i_offset, player["key"], len(notes[player["key"]]))
        trigs=[{"notes": v,
                "type": "trig"}
               for v in notes.values()]
        struct["tracks"]+=trigs

    @property
    def nslices(self):
        return len(self["pattern"])
            
class Effect(dict):

    @classmethod
    def randomise(self, controller, styles=[SampleHold]):
        return Effect({"controller": controller,
                       "seed": int(1e8*random.random()),
                       "style": random.choice(styles)})
    
    def __init__(self, obj):
        dict.__init__(self, obj)

    def randomise_seed(self, limit):
        if random.random() < limit:
            self["seed"]=int(1e8*random.random())

class FXGenerator(dict):
    
    def __init__(self, ctrl, offset=0):
        dict.__init__(self)
        self.ctrl=ctrl
        self.offset=offset

    def generate(self, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)
        return self

    def add(self, i, v):
        j=i+self.offset
        self[j]={"value": v,
                 "mod": self.ctrl["mod"],
                 "attr": self.ctrl["attr"]}
    
    def sample_hold(self, q, i):
        kwargs=self.ctrl["kwargs"][SampleHold]
        step=kwargs["step"]
        floor=kwargs["min"] if "min" in kwargs else 0
        ceil=kwargs["max"] if "max" in kwargs else 1
        inc=kwargs["inc"] if "inc" in kwargs else 0.25
        if 0 == i % step:
            v0=floor+(ceil-floor)*q.random()
            v=inc*int(0.5+v0/inc)
            self.add(i, v)
            
class Effects(list):

    @classmethod
    def randomise(self, controllers):
        return Effects([Effect.randomise(controller)
                        for controller in controllers])
    
    def __init__(self, effects):
        list.__init__(self, [Effect(effect)
                             for effect in effects])

    def randomise_seeds(self, limit):
        for trig in self:
            trig.randomise_seed(limit)

    """
    - NB define q on per- effect level, not locally for each slice
    """
            
    def render(self, struct, nslices, nbeats):
        for effect in self:
            svtrig={"type": "fx",
                    "notes": {}}
            q=Q(effect["seed"]) 
            for j in range(nslices):
                offset=j*nbeats
                generator=FXGenerator(ctrl=effect["controller"],
                                      offset=offset)
                values=generator.generate(n=nbeats,
                                          q=q,
                                          style=effect["style"])
                svtrig["notes"].update(values)
            struct["tracks"].append(svtrig)
            
class Patch(dict):

    @classmethod
    def randomise(self, randomisers, controllers):
        return Patch(tracks=Tracks.randomise(randomisers),
                     effects=Effects.randomise(controllers))
    
    def __init__(self, tracks, effects):
        dict.__init__(self, {"tracks": Tracks(**tracks),
                             "effects": Effects(effects)})

    def clone(self):
        return copy.deepcopy(self)
        
    def render(self, nbeats):
        struct={"n": nbeats,
                "tracks": []}
        nslices=self["tracks"].nslices
        nslicebeats=int(nbeats/nslices)
        self["tracks"].render(struct,
                              nbeats=nslicebeats)
        self["effects"].render(struct,
                               nslices=nslices,
                               nbeats=nslicebeats)
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
    - json dumps/loads to clear classes which yaml won't represent by default
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
