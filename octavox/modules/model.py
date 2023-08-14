from octavox.modules import load_class

import json

"""
- SVSampleKey must be dict as typically needs to be rendered to JSON as part of custom project Samples class
- SVSampleKey is lenient with respect to passing of `params` and `tags` args; note that key functions check for their existence and non- emptiness
"""

class SVSampleKey(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def clone(self):
        kwargs={"bank": self["bank"],
                "file": self["file"]}
        if "params" in self:
            kwargs["params"]=dict(self["params"])
        if "tags" in self:
            kwargs["tags"]=list(self["tags"])
        return SVSampleKey(kwargs)

    def add_tag(self, tag):
        if "tags" not in self:
            self["tags"]=[]
        if tag not in self["tags"]:
            self["tags"].append(tag)
    
    @property
    def ext(self):
        return self["file"].split(".")[-1]

    @property
    def base_key(self):
        tokens=[]
        tokens.append("%s/%s" % (self["bank"],
                                 self["file"]))
        return " ".join(tokens)
            
    @property
    def full_key(self):
        tokens=[]
        tokens.append("%s/%s" % (self["bank"],
                                 self["file"]))
        if ("params" in self and
            self["params"]!={}):
            tokens.append(json.dumps(self["params"]))
        if ("tags" in self and 
            self["tags"]!=[]):
            tokens.append("[%s]" % ", ".join(sorted(self["tags"])))
        return " ".join(tokens)

"""
- mod is automatically added to samplekey tags so that samples can be properly allocated to samplers at project rendering time
"""

class SVNoteTrig:

    def __init__(self, mod, i, samplekey=None, id=None, vel=1):
        self.mod=mod
        self.i=i
        if samplekey:
            samplekey.add_tag(mod) # NB
        self.samplekey=samplekey
        self.id=id
        self.vel=vel        
        
    @property
    def track_key(self):
        return self.mod
        
    def render(self,
               modules,
               controllers,
               volume=128):
        if self.mod not in modules:
            raise RuntimeError("mod %s not found" % self.mod)
        mod=modules[self.mod]
        trig=1+(mod.lookup(self.samplekey) if self.samplekey else self.id)
        modid=1+mod.index # NB 1+
        vel=max(1, int(self.vel*volume))
        from rv.note import Note
        return Note(note=trig,
                    vel=vel,
                    module=modid)

class SVFXTrig:
    
    def __init__(self, mod, ctrl, value, i):
        self.mod=mod
        self.ctrl=ctrl
        self.value=value
        self.i=i

    @property
    def track_key(self):
        return "%s/%s" % (self.mod,
                          self.ctrl)
        
    def render(self,
               modules,
               controllers,
               ctrlmult=256,
               maxvalue=256*128):
        if (self.mod not in modules or
            self.mod not in controllers):
            raise RuntimeError("mod %s not found" % self.mod)
        mod, controller = modules[self.mod], controllers[self.mod]
        modid=1+mod.index # NB 1+
        if self.ctrl not in controller:
            raise RuntimeError("ctrl %s not found in mod %s" % (self.ctrl,
                                                                self.mod))
        ctrlid=ctrlmult*controller[self.ctrl]
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
        for trig in self:
            key=trig.track_key
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
                if (hasattr(trig, "samplekey") and trig.samplekey):
                    keys.add(trig.samplekey)

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
            machine.render(nbeats=nbeats,
                           trigs=trigs,
                           density=self["density"])
        return trigs.tracks

if __name__=="__main__":
    pass
