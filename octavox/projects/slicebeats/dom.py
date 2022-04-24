from octavox.projects.slicebeats.trigs import Channels

from octavox.projects.slicebeats.trigs import TrigGenerator

from octavox.projects.slicebeats.trigs import Styles as TrigStyles

from octavox.projects.slicebeats.fx import FXGenerator

from octavox.projects.slicebeats.fx import Styles as FXStyles

from octavox.projects.slicebeats.project import SVProject

import copy, json, os, random, yaml

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

class Samples(dict):

    @classmethod
    def randomise(self, randomisers):
        return Samples(randomisers["samples"].randomise())

    def __init__(self, obj):
        dict.__init__(self, obj)

    def randomise_samples(self, samples):
        for channel in self.keys():
            self[channel]=random.choice(samples[channel])
        
class Trig(dict):

    @classmethod
    def randomise(self, channel, styles=TrigStyles):
        return Trig({"channel": channel,
                     "seed": int(1e8*random.random()),
                     "style": random.choice(styles[channel])})

    def __init__(self, obj):
        dict.__init__(self, obj)

    def randomise_style(self, limit, styles=TrigStyles):
        if random.random() < limit:
            self["style"]=random.choice(styles[self["channel"]])
            
    def randomise_seed(self, limit):
        if random.random() < limit:
            self["seed"]=int(1e8*random.random())
        
class Trigs(list):

    @classmethod
    def randomise(self, channels=Channels):
        return Trigs([Trig.randomise(channel)
                      for channel in channels])
            
    def __init__(self, trigs):
        list.__init__(self, [Trig(trig)
                             for trig in trigs])

    @property
    def trigmap(self):
        return {trig["channel"]:trig
                for trig in self}
            
class Slice(dict):

    @classmethod
    def randomise(self, randomisers):
        return Slice(samples=Samples.randomise(randomisers),
                     trigs=Trigs.randomise())
    
    def __init__(self, samples, trigs):
        dict.__init__(self, {"samples": Samples(samples),
                             "trigs": Trigs(trigs)})

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
                      pattern=random.choice(self.Patterns),
                      mutes=[])
        
    def __init__(self, slices, pattern, mutes):
        dict.__init__(self, {"slices": Slices(slices),
                             "pattern": pattern,
                             "mutes": mutes})

    def randomise_pattern(self, limit):
        if random.random() < limit:
            self["pattern"]=random.choice(self.Patterns)

    def randomise_mutes(self, limit, channels=Channels):
        self["mutes"]=[channel for channel in channels
                       if random.random() < limit]
            
    def render(self, struct, nbeats, channels=Channels):
        for channel in channels:
            svtrig={"type": "trig",
                    "notes": {}}
            volume=1 if channel not in self["mutes"] else 0
            for j, i in enumerate(self["pattern"]):
                slice=self["slices"][i]
                trig=slice["trigs"].trigmap[channel]
                offset=j*nbeats
                generator=TrigGenerator(samples=slice["samples"],
                                        offset=offset,
                                        volume=volume)
                values=generator.generate(n=nbeats,
                                          q=Q(trig["seed"]),
                                          style=trig["style"])
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