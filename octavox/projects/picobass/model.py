from octavox.modules.project import SVProject, SVPatch

import json, os, random, yaml

Config=yaml.safe_load(open("octavox/projects/picobass/config.yaml").read())

Instruments={"kk": ["kk"],
             "sn": ["sn"],
             "ht": ["oh", "ch"]}

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

class Samples(dict):

    @classmethod
    def randomise(self,
                  i,
                  key,
                  pool,
                  instruments=Instruments):
        samples={}
        for k in instruments[key]:
            samples[k]=random.choice(pool[k])
        return Samples(samples)
            
    def __init__(self, obj):
        dict.__init__(self, obj)

    def clone(self):
        return Samples(self)

def init_machine(config):
    def decorator(fn):
        def wrapped(self, item, **kwargs):
            fn(self, item, **kwargs)
            params=config[item["key"]]
            for attr in params:
                setattr(self, attr, params[attr])
        return wrapped
    return decorator

class Sequencer(dict):

    @classmethod
    def randomise(self,
                  key,
                  pool)
        return Sequencer({"key": key})

    @init_machine(config=Config["sequencers"])
    def __init__(self, item):
        dict.__init__(self, {"key": item["key"]})
                
    def clone(self):
        return Sequencer({"key": self["key"]})

    """
    def render(self,
               tracks,
               nbeats):
        multiplier=int(nbeats/self["pattern"].size)
        offset=0
        for pat in self["pattern"].expanded:
            slice=self["slices"][pat["i"]]
            q=Q(slice["seed"])            
            fn=getattr(self, slice["style"])
            nsamplebeats=pat["n"]*multiplier
            for i in range(nsamplebeats):
                fn(q, i, tracks, offset, slice["samples"])
            offset+=nsamplebeats
    """

    def apply(fn):
        def wrapped(self, q, i, d,
                    tracks,
                    offset,
                    samples):
            v=fn(self, q, i, d, tracks, offset, samples)
            if v!=None: # explicit because could return zero
                instkey, volume = v
                samplekey=samples[instkey]
                trig={"vel": volume,
                      "i": i+offset}
                trig["mod"]=self.mod
                trig["key"]=samplekey
                tracks.setdefault(self["key"], [])
                tracks[self["key"]].append(trig)
        return wrapped
    
class Sequencers(list):

    @classmethod
    def randomise(self,
                  pool,
                  config=Config["sequencers"]):
        return Sequencers([Sequencer.randomise(key=key,
                                               pool=pool)
                          for key in config])

    def __init__(self, sequencers):
        list.__init__(self, [Sequencer(seq)
                             for seq in sequencers])

    def clone(self):
        return Sequencers([seq.clone()
                           for seq in self])

class Lfo(dict):

    @classmethod
    def randomise(self, key):
        return Lfo({"key": key,
                    "seed": int(1e8*random.random())})

    @init_machine(config=Config["lfos"])
    def __init__(self, item):
        dict.__init__(self, item)
        
    def clone(self):
        return Lfo(self)
        
    def randomise_seed(self, limit):
        if random.random() < limit:
            seed=int(1e8*random.random())
            self["seed"]=seed

    def render(self, nbeats, tracks):
        q=Q(self["seed"])
        for i in range(nbeats):
            self.sample_hold(q, i, tracks)

    def apply(fn):
        def wrapped(self, q, i, tracks):
            v=fn(self, q, i, tracks)
            if v!=None: # explicit because could return zero
                trig={"mod": self.mod,
                      "ctrl": self.ctrl,
                      "v": v,
                      "i": i}
                tracks.setdefault(self["key"], [])
                tracks[self["key"]].append(trig)
        return wrapped

    @apply
    def sample_hold(self, q, i, *args):
        if 0 == i % self.step:
            if q.random() < self.live:
                floor, ceil = self.range
                v0=floor+(ceil-floor)*q.random()
                return self.increment*int(0.5+v0/self.increment)
            else:
                return 0.0
                
class Lfos(list):

    @classmethod
    def randomise(self, config=Config["lfos"]):
        return Lfos([Lfo.randomise(key)
                     for key in config])

    def __init__(self, lfos):
        list.__init__(self, [Lfo(lfo)
                             for lfo in lfos])

    def clone(self):
        return Lfos([lfo.clone()
                     for lfo in self])

class Patch(dict):

    @classmethod
    def randomise(self, pool):
        return Patch(sequencers=Sequencers.randomise(pool=pool)
                     lfos=Lfos.randomise())
        
    def __init__(self,
                 sequencers,
                 lfos):
        dict.__init__(self, {"sequencers": Sequencers(sequencers),
                             "lfos": Lfos(lfos)})
        
    def clone(self):
        return Patch(sequencers=self["sequencers"].clone(),
                     lfos=self["lfos"].clone())

    def render(self,
               nbeats):
        tracks=SVPatch(nbeats=nbeats)
        for seq in self["sequencers"]:
            seq.render(nbeats=nbeats,
                       tracks=tracks)
        for lfo in self["lfos"]:
            lfo.render(nbeats=nbeats,
                       tracks=tracks)
        return tracks

class Patches(list):

    def __init__(self, patches=[]):
        list.__init__(self, [Patch(**patch)
                             for patch in patches])

    def render_json(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self,
                               indent=2))

    def render_sunvox(self,
                      banks,
                      nbeats,
                      filename,
                      config=Config):
        project=SVProject().render(patches=[patch.render(nbeats=nbeats)
                                            for patch in self],
                                   config=config,
                                   banks=banks)
        with open(filename, 'wb') as f:
            project.write_to(f)
    
if __name__=="__main__":
    pass
