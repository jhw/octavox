from octavox.projects.slicebeats.project import SVProject

from collections import OrderedDict

import copy, json, os, random, yaml

"""
- https://github.com/beats/acid-banger/blob/main/src/pattern.ts
"""

Kick, Snare, OpenHat, ClosedHat = "kk", "sn", "oh", "ch"

FourFloor, Electro, Triplets, Backbeat, Skip, Offbeats, OffbeatsOpen, OffbeatsClosed, Closed, Empty = "fourfloor", "electro", "triplets", "backbeat", "skip", "offbeats", "offbeats_open", "offbeats_closed", "closed", "empty"

SVDrum, Drum, Sampler = "svdrum", "Drum", "Sampler"

TrigStyles=OrderedDict({Kick: [Electro, FourFloor, Triplets],
                        Snare: [Backbeat, Skip],
                        OpenHat: [OffbeatsOpen],
                        ClosedHat: [OffbeatsClosed]})

SampleHold="sample_hold"

FXStyles=[SampleHold]

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
        
class Player(dict):

    def __init__(self, obj):
        dict.__init__(self, obj)

class MachineBase(list):

    def __init__(self, items):
        list.__init__(self, items)

    """ 
    - all players in a machine need the same seed
    """
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            for player in self:                
                player["seed"]=seed
        
class KickMachine(MachineBase):

    KickStyles=[FourFloor, Electro, Triplets]
    
    @classmethod
    def randomise(self, styles=KickStyles):
        seed=int(1e8*random.random())
        style=random.choice(styles)
        return KickMachine(seed, style)
    
    def __init__(self, seed, style):
        MachineBase.__init__(self,
                             [Player({"key": Kick,
                                      "seed": seed,
                                      "style": style})])

    def randomise_style(self, limit, styles=KickStyles):
        if random.random() < limit:
            for player in self:
                player["style"]=random.choice(styles)
                  
class SnareMachine(MachineBase):

    SnareStyles=[FourFloor, Electro, Triplets]
    
    @classmethod
    def randomise(self, styles=SnareStyles):
        seed=int(1e8*random.random())
        style=random.choice(styles)
        return SnareMachine(seed, style)
    
    def __init__(self, seed, style):
        MachineBase.__init__(self,
                             [Player({"key": Snare,
                                      "seed": seed,
                                      "style": style})])

    def randomise_style(self, limit, styles=SnareStyles):
        if random.random() < limit:
            for player in self:
                player["style"]=random.choice(styles)

class HatsMachine(MachineBase):

    HatsStyles=[Offbeats, Closed]
    
    @classmethod
    def randomise(self, styles=HatsStyles):
        seed=int(1e8*random.random())
        style=random.choice(styles)
        return HatsMachine(seed, style)

    @classmethod
    def substyles(self, style):
        return [OffbeatsOpen, OffbeatsClosed] if style==Offbeats else [Closed, Empty]
    
    def __init__(self, seed, rootstyle):
        MachineBase.__init__(self,
                             [Player({"key": Hats,
                                      "seed": seed,
                                      "style": substyle})
                              for substyle in HatsMachine.substyles(rootstyle)])

    def randomise_style(self, limit, styles=HatsStyles):
        if random.random() < limit:
            rootstyle=random.choice(styles)
            for player, substyle in zip(self, HatsMachine.substyles(rootstyle):
                player["style"]=substyle
                
class Machines(list):

    """
    @classmethod
    def randomise(self, machines=TrigStyles):
        return Machines([Player.randomise(key)
                         for key in machines])
    """

    @classmethod
    def randomise(self, machines=TrigStyles):
        pass
            
    def __init__(self, machines):
        list.__init__(self, [Player(player)
                             for player in machines])

    """
    def to_map(self):
        return {player["key"]:player
                for player in self}
    """
        
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

    def offbeats_open(self, q, i, k=OpenHat):
        if i % 4 == 2:
            self.add(i, (k, 0.4))
        elif q.random() < 0.15:
            self.add(i, (k, 0.2*q.random()))

    def offbeats_closed(self, q, i, k=ClosedHat):
        if 0.15 < q.random() < 0.3:
            self.add(i, (k, 0.2*q.random()))

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
                      pattern=random.choice(self.Patterns),
                      mutes=[])
        
    def __init__(self, slices, pattern, mutes):
        dict.__init__(self, {"slices": Slices(slices),
                             "pattern": pattern,
                             "mutes": mutes})

    def randomise_pattern(self, limit):
        if random.random() < limit:
            self["pattern"]=random.choice(self.Patterns)

    def render(self, struct, nbeats, _machines=TrigStyles):
        for key in _machines:
            svtrig={"type": "trig",
                    "notes": {}}
            volume=1 if key not in self["mutes"] else 0
            for j, i in enumerate(self["pattern"]):
                slice=self["slices"][i]
                offset=j*nbeats
                generator=TrigGenerator(samples=slice["samples"],
                                        offset=offset,
                                        volume=volume)
                player=slice["machines"].to_map()[key]
                values=generator.generate(n=nbeats,
                                          q=Q(player["seed"]),
                                          style=player["style"])
                svtrig["notes"].update(values)
            struct["tracks"].append(svtrig)

    @property
    def nslices(self):
        return len(self["pattern"])
            
class Effect(dict):

    @classmethod
    def randomise(self, controller, styles=FXStyles):
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
