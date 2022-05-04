from octavox.projects.slicebeats.project import SVProject

from collections import OrderedDict

import copy, json, os, random, yaml

Kick, Snare, Hats, OpenHat, ClosedHat, EchoWet, EchoFeedback = "kk", "sn", "ht", "oh", "ch", "ew", "ef"

FourFloor, Electro, Triplets, Backbeat, Skip, Offbeats, OffbeatsOpen, OffbeatsClosed, Closed, Empty = "fourfloor", "electro", "triplets", "backbeat", "skip", "offbeats", "offbeats_open", "offbeats_closed", "closed", "empty"

SampleHold="sample_hold"

KickStyles, SnareStyles, HatsStyles, EchowetStyles, EchofeedbackStyles = [FourFloor, Electro, Triplets], [Backbeat, Skip], [Offbeats, Closed], [SampleHold], [SampleHold]

MachineMapping={Kick: "kick",
                Snare: "snare",
                Hats: "hats",
                EchoWet: "echoWet",
                EchoFeedback: "echoFeedback"}

SVDrum, Drum, Sampler = "svdrum", "Drum", "Sampler"

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

class FXGenerator(dict):
    
    def __init__(self,
                 mod,
                 attr,
                 offset=0,
                 step=4,
                 floor=0,
                 ceil=1,
                 inc=0.25):
        dict.__init__(self)
        self.mod=mod
        self.attr=attr
        self.offset=offset
        self.step=step
        self.floor=floor
        self.ceil=ceil
        self.inc=inc

    def generate(self, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)
        return self

    def add(self, i, v):
        j=i+self.offset
        self[j]={"value": v,
                 "mod": self.mod,
                 "attr": self.attr}
    
    def sample_hold(self, q, i):
        if 0 == i % self.step:
            v0=self.floor+(self.ceil-self.floor)*q.random()
            v=self.inc*int(0.5+v0/self.inc)
            self.add(i, v)
    
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
    def tracks(self):
        return [self]

class TrigMachineBase(MachineBase):
    
    """
    - NB generator is currently stateful ie you need a new one for each iteration
    """
    
    def render(self, struct, nbeats, offset, samples, volume=1):
        for track in self.tracks:
            generator=TrigGenerator(samples=samples,
                                    offset=offset,
                                    volume=volume)                                
            notes=generator.generate(n=nbeats,
                                     q=Q(track["seed"]),
                                     style=track["style"])
            struct.setdefault(track["key"], {})
            struct[track["key"]].update(notes)
    
class KickMachine(TrigMachineBase):

    pass
                
class SnareMachine(TrigMachineBase):

    pass
    
class HatsMachine(TrigMachineBase):
    
    @property
    def substyles(self):
        return zip([OpenHat, ClosedHat],
                   [OffbeatsOpen, OffbeatsClosed] if self["style"]==Offbeats else [Closed, Empty])
                   
    @property
    def tracks(self):
        return [{"key": key,
                 "seed": self["seed"],
                 "style": substyle}
                for key, substyle in self.substyles]

class FXMachineBase(MachineBase):

    def render(self, struct, nbeats, offset, **kwargs):
        generator=FXGenerator(mod=self.Mod,
                              attr=self.Attr,
                              ceil=self.Ceil,
                              offset=offset)
        notes=generator.generate(n=nbeats,
                                 q=Q(self["seed"]),
                                 style=self["style"])
        struct.setdefault(self["key"], {})
        struct[self["key"]].update(notes)
        
class EchowetMachine(FXMachineBase):

    Mod, Attr, Ceil = "Echo", "wet", 1.0

class EchofeedbackMachine(FXMachineBase):

    Mod, Attr, Ceil = "Echo", "feedback", 0.75
    
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

    def render(self, keys, struct, nbeats, offset):
        machines={machine["key"]: machine
                  for machine in self["machines"]}
        for key in keys:
            machine=machines[key]
            machine.render(struct, nbeats, offset,
                           samples=self["samples"])

class Slices(list):

    @classmethod
    def randomise(self, randomisers, n=4):
        return Slices([Slice.randomise(randomisers)
                       for i in range(n)])
    
    def __init__(self, slices):
        list.__init__(self, [Slice(**slice)
                             for slice in slices])
        
class Tracks(dict):

    TrigPatterns=FXPatterns=[[0],
                             [0, 1],
                             [0, 0, 0, 1],
                             [0, 1, 0, 2],
                             [0, 1, 2, 3]]

    @classmethod
    def randomise(self, randomisers):
        return Tracks(slices=Slices.randomise(randomisers),
                      trigpattern=random.choice(self.TrigPatterns),
                      fxpattern=random.choice(self.FXPatterns))
        
    def __init__(self, slices, trigpattern, fxpattern):
        dict.__init__(self, {"slices": Slices(slices),
                             "trigpattern": trigpattern,
                             "fxpattern": fxpattern})

    def randomise_trig_pattern(self, limit):
        if random.random() < limit:
            self["trigpattern"]=random.choice(self.TrigPatterns)

    def randomise_fx_pattern(self, limit):
        if random.random() < limit:
            self["fxpattern"]=random.choice(self.TrigPatterns)


    def _render(self, struct, keys, pattern, type, nbeats):
        notes={}
        for i_offset, i_slice in enumerate(pattern):
            offset=i_offset*nbeats
            slice=self["slices"][i_slice]
            slice.render(keys, notes, nbeats, offset)                         
        struct["tracks"]+=[{"notes": v,
                            "type": type}
                           for v in notes.values()]
                
    def render_trigs(self, struct, nbeats):
        self._render(struct=struct,
                    keys=[Kick, Snare, Hats],
                    pattern=self["trigpattern"],
                    type="trig",
                    nbeats=nbeats)

    def render_effects(self, struct, nbeats):
        self._render(struct=struct,
                     keys=[EchoWet, EchoFeedback],
                     pattern=self["fxpattern"],
                     type="fx",
                     nbeats=nbeats)

    def render(self, struct, nbeats):
        self.render_trigs(struct, nbeats)
        self.render_effects(struct, nbeats)
        
    @property
    def ntrigslices(self):
        return len(self["trigpattern"])

    @property
    def nfxslices(self):
        return len(self["fxpattern"])
            
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
        ntrigslices=self["tracks"].ntrigslices
        ntrigbeats=int(nbeats/ntrigslices)
        self["tracks"].render_trigs(struct, ntrigbeats)
        nfxslices=self["tracks"].nfxslices
        nfxbeats=int(nbeats/nfxslices)
        self["tracks"].render_effects(struct, nfxbeats)
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
