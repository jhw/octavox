from octavox.modules import load_class

import json

"""
- SVSample must be dict as typically needs to be rendered to JSON as part of custom project Samples class
- SVSample is lenient with respect to passing of `params` and `tags` args; note that key functions check for their existence and non- emptiness
"""

class SVSample(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def clone(self):
        kwargs={"bank": self["bank"],
                "file": self["file"]}
        if "params" in self:
            kwargs["params"]=dict(self["params"])
        if "tags" in self:
            kwargs["tags"]=list(self["tags"])
        return SVSample(kwargs)

    def add_tag(self, tag):
        if "tags" not in self:
            self["tags"]=[]
        if tag not in self["tags"]:
            self["tags"].append(tag)
    
    @property
    def ext(self):
        return self["file"].split(".")[-1]

    def __str__(self):
        tokens=[]
        tokens.append("%s/%s" % (self["bank"],
                                 self["file"]))
        if ("tags" in self and 
            self["tags"]!=[]):
            tokens.append("[%s]" % ", ".join(sorted(self["tags"])))
        return " ".join(tokens)

"""
- mod is automatically added to sample tags so that samples can be properly allocated to samplers at project rendering time
- chord is expanded into a series of note trigs with different track keys
- chords do not support sample
"""

class SVNoteTrig:

    Volume=128
    
    def __init__(self, mod, i,
                 chord=None,
                 sample=None,
                 note=None,
                 vel=1):
        self.mod=mod
        self.i=i
        self.chord=chord
        if sample:
            sample.add_tag(mod) # NB
        self.sample=sample
        self.note=note
        self.vel=vel        
        
    @property
    def expanded(self):
        if self.chord:
            return [("%s/%i" % (self.mod, i),
                     SVNoteTrig(mod=self.mod,
                                i=self.i,
                                note=note))
                    for i, note in enumerate(self.chord)]
        else:
            return [(self.mod, self)]
        
    def render(self,
               modules,
               *args):
        if self.mod not in modules:
            raise RuntimeError("mod %s not found" % self.mod)
        mod=modules[self.mod]
        modid=1+mod.index # NB 1+
        note=1+(mod.lookup(self.sample) if self.sample else self.note)
        vel=max(1, int(self.vel*self.Volume))
        from rv.note import Note
        return Note(module=modid,
                    note=note,
                    vel=vel)

class SVFXTrig:

    CtrlMult=256

    def __init__(self, target, value, i):
        self.target=target
        self.value=value
        self.i=i

    @property
    def mod(self):
        return self.target.split("/")[0]

    @property
    def ctrl(self):
        return self.target.split("/")[1]
        
    @property
    def expanded(self):
        return [(self.target, self)]
        
    def render(self,
               modules,
               controllers):
        if (self.mod not in modules or
            self.mod not in controllers):
            raise RuntimeError("mod %s not found" % self.mod)
        mod, controller = modules[self.mod], controllers[self.mod]
        modid=1+mod.index # NB 1+
        if self.ctrl not in controller:
            raise RuntimeError("ctrl %s not found in mod %s" % (self.ctrl,
                                                                self.mod))
        ctrlid=self.CtrlMult*controller[self.ctrl]
        from rv.note import Note
        return Note(module=modid,
                    ctl=ctrlid,
                    val=self.value)

class SVTrigs(list):

    def __init__(self, nbeats, items=[]):
        list.__init__(self, items)
        self.nbeats=nbeats

    @property
    def tracks(self):
        tracks=SVTracks(self.nbeats)
        for _trig in self:
            for key, trig in _trig.expanded:
                tracks.setdefault(key, [])
                tracks[key].append(trig)
        return tracks

"""
- SVTracks class is locally named a patch, for post- rendering convenience
"""
    
class SVTracks(dict):

    def __init__(self, nbeats, item={}):
        dict.__init__(self)
        self.nbeats=nbeats

    def filter_pool(self, keys):
        for track in self.values():
            for trig in track:
                if (hasattr(trig, "sample") and trig.sample):
                    keys.add(trig.sample)

    @property
    def grid(self):
        return [{note.i:note
                 for note in track}
                for key, track in self.items()]

class SVMachines(list):
    
    @classmethod
    def randomise(self,
                  machines,
                  **kwargs):
        return SVMachines([load_class(machine["class"]).randomise(machine=machine,
                                                                **kwargs)
                           for machine in machines])
    
    def __init__(self, machines):
        list.__init__(self, [load_class(machine["class"])(machine=machine)
                             for machine in machines])
        
    def clone(self):
        return SVMachines([machine.clone()
                           for machine in self])
    
class SVPatch(dict):
    
    @classmethod
    def randomise(self, density, machines, **kwargs):
        return SVPatch(machines=SVMachines.randomise(machines=machines,
                                                     **kwargs),
                       density=density)
        
    def __init__(self,
                 machines,
                 density):
        dict.__init__(self, {"machines": SVMachines(machines),
                             "density": density})
        
    def clone(self):
        return SVPatch(machines=self["machines"].clone(),
                       density=self["density"])
    
    def render(self,
               nbeats):
        trigs=SVTrigs(nbeats=nbeats)
        for machine in self["machines"]:
            for trig in machine.render(nbeats=nbeats,
                                       density=self["density"]):
                trigs.append(trig)
        return trigs.tracks

if __name__=="__main__":
    pass
