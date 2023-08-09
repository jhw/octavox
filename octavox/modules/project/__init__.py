from rv.api import Project as RVProject
from rv.pattern import Pattern as RVPattern
from rv.note import Note as RVNote

from octavox.modules.banks import SVPool

from octavox.modules.project.modules import SVColor, init_layout, Output

import importlib

Volume, Height = 256, 64

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
        return RVNote(note=trig,
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
        ctrlvalue=int(self.value*maxvalue) # NB **NOT** 1+
        return RVNote(module=modid,
                      ctl=ctrlid,
                      val=ctrlvalue)

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
                    
class SVOffset:

    def __init__(self):
        self.value=0
        self.count=0

    def increment(self, value):
        self.value+=value
        self.count+=1
        
class SVProject:

    def filter_pool(self,
                          patches):
        pool=SVPool()
        for patch in patches:
            patch.filter_pool(pool)
        return pool

    def init_modclasses(self,
                        config,
                        pool,
                        banks):
        def init_class(mod):
            try:
                tokens=mod["class"].split(".")            
                modpath, classname = ".".join(tokens[:-1]), tokens[-1]
                module=importlib.import_module(modpath)
                return getattr(module, classname)
            except:
                raise RuntimeError("error importing %s" % mod["class"])
        for mod in config["modules"]:
            modclass=init_class(mod)
            kwargs={}
            if mod["class"].lower().endswith("sampler"):
                filtered=pool.filter(mod["name"])
                kwargs={"banks": banks,
                        "pool": filtered}
            mod["instance"]=modclass(**kwargs)
                
    def init_modules(self,
                     proj,
                     config,
                     multipliers={"x": 1, "y": -1}):
        positions=init_layout(modules=config["modules"],
                              links=config["links"])
        modules={}
        for i, moditem in enumerate(config["modules"]):
            mod, name = moditem["instance"], moditem["name"]
            setattr(mod, "name", name)
            for i, attr in enumerate(["x", "y"]):            
                value=positions[name][i]
                mult=multipliers[attr]
                setattr(mod, attr, int(512+128*mult*value))
            if "defaults" in moditem:
                for k, v in moditem["defaults"].items():
                    try:
                        mod.set_raw(k, v)
                    except:
                        raise RuntimeError("error setting ctrl %s in %s" % (k, moditem["name"]))
            proj.attach_module(mod)
            modules[name]=mod
        return modules
    
    def link_modules(self,
                     proj,
                     config,
                     modules):
        output=sorted(proj.modules, key=lambda x: -x.index).pop()
        for src, dest in config["links"]:
            proj.connect(modules[src],
                         output if dest==Output else modules[dest])

    def attach_pattern(fn):
        def wrapped(*args, **kwargs):
            rvpat=fn(*args, **kwargs)
            kwargs["patterns"].append(rvpat)
            kwargs["offset"].increment(kwargs["patch"].nbeats)
        return wrapped
    
    @attach_pattern
    def init_pattern(self,
                     patterns,
                     modules,
                     controllers,
                     patch,
                     offset,
                     color,
                     height=Height):
        grid=patch.grid
        def notefn(self, j, i):
            return grid[i][j].render(modules,
                                     controllers) if j in grid[i] else RVNote()
        return RVPattern(lines=patch.nbeats,
                         tracks=len(patch),
                         x=offset.value,
                         y_size=height,
                         bg_color=color).set_via_fn(notefn)

    def init_controllers(self, modules):
        controllers={}
        for mod in modules.values():
            controllers.setdefault(mod.name, {})
            for controller in mod.controllers.values():
                controllers[mod.name].setdefault(controller.name, {})
                controllers[mod.name][controller.name]=controller.number
        return controllers

    def init_patterns(self,
                      modules,
                      patches):
        controllers=self.init_controllers(modules)
        offset=SVOffset()
        patterns, color = [], None
        for i, patch in enumerate(patches):
            color=SVColor.randomise() if 0==i%4 else color.mutate()
            self.init_pattern(patterns=patterns,
                              modules=modules,
                              controllers=controllers,
                              patch=patch,
                              offset=offset,
                              color=color)            
        return patterns

    def render(self,
               patches,
               config,
               banks,
               bpm,
               volume=Volume):
        proj=RVProject()
        proj.initial_bpm=bpm
        proj.global_volume=volume
        pool=self.filter_pool(patches=patches)
        self.init_modclasses(config=config,
                             pool=pool,
                             banks=banks)
        modules=self.init_modules(proj=proj,
                                  config=config)
        self.link_modules(proj=proj,
                          config=config,
                          modules=modules)
        proj.patterns=self.init_patterns(modules=modules,
                                         patches=patches)
        return proj

if __name__=="__main__":
    pass
