from rv.api import Project as RVProject
from rv.pattern import Pattern as RVPattern
from rv.note import Note as RVNote

import importlib, math, random

Output, Volume, Height = "Output", 256, 64

class SVNoteTrig:

    def __init__(self, mod, i, samplekey=None, id=None, vel=1):
        self.mod=mod
        self.i=i
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
        mod, controller = modules[self.mod], controllers[self.mod]
        modid=1+mod.index # NB 1+
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

    def filter_samplekeys(self, keys):
        for track in self.values():
            for trig in track:
                if (hasattr(trig, "samplekey") and trig.samplekey):
                    keys[str(trig.samplekey)]=trig.samplekey

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

class SVModGrid(dict):

    @classmethod
    def all(self, sz):
        offset=int(sz/2)
        return [(x-offset, y-offset)
                for y in range(sz)
                for x in range(sz)]
    
    @classmethod
    def randomise(self, modnames):
        sz=1+int(math.ceil(len(modnames)**0.5)) # NB +1 to ensure decent amount of whitespace in which to move cells around
        coords=sorted(SVModGrid.all(sz),
                      key=lambda x: random.random())[:len(modnames)]
        return SVModGrid(sz=sz,
                         item={mod:xy
                               for mod, xy in zip(modnames, coords)})
    
    def __init__(self, sz, item):
        dict.__init__(self, item)
        self.sz=sz

    def clone(self):
        return SVModGrid(sz=self.sz,
                         item={k:v for k, v in self.items()})

    @property
    def allocated(self):
        allocated=set(self.values())
        allocated.add((0, 0))
        return list(allocated)

    @property
    def unallocated(self):
        all, allocated = SVModGrid.all(self.sz), self.allocated
        return [xy for xy in all if xy not in allocated]

    def shuffle(self, n):
        keys, unallocated = list(self.keys()), self.unallocated
        for i in range(min(n, len(unallocated))):
            key=random.choice(keys)
            self[key]=unallocated[i]
        return self
    
    def rms_distance(self, links):
        total=0
        for link in links:
            a, b = [self[modname]
                    for modname in link]
            distance=((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
            total+=distance
        return total

class SVProject:

    def random_color(self, offset):
        return [int(offset+random.random()*(255-offset))
                for i in range(3)]
    
    def new_color(self,
                  offset=64,
                  contrast=128,
                  n=16):
        for i in range(n):
            color=self.random_color(offset)
            if (max(color)-min(color)) > contrast:
                return color
        return [127 for i in range(3)]

    def mutate_color(self,
                     color,
                     contrast=32):
        values=range(-contrast, contrast)
        return [min(255, max(0, rgb+random.choice(values)))
                for rgb in  color]

    def init_layout(self,
                    config,
                    n=1000,
                    nclones=5):
        def shuffle(config, grid, q):
            clone=grid.clone()
            clone.shuffle(q)
            distance=clone.rms_distance(config["links"])
            return (clone, distance)
        modnames=[Output]+[mod["name"]
                           for mod in config["modules"]]
        grid=SVModGrid.randomise(modnames)
        best=grid.rms_distance(config["links"])
        for i in range(n):
            q=int(math.ceil(len(modnames)*(n-i)/n))
            clones=sorted([shuffle(config, grid, q)
                           for i in range(nclones)],
                          key=lambda x: -x[1])
            newgrid, newbest = clones[-1]
            if newbest < best:
                grid, best = newgrid, newbest
        return grid

    def filter_samplekeys(self,
                          patches):
        samplekeys={}
        for patch in patches:
            patch.filter_samplekeys(samplekeys)
        return list(samplekeys.values())

    """
    - creation of sampler kwargs may need to change if you have multiple classes of sampler in the future
    """
    
    def init_modclasses(self,
                        config,
                        samplekeys,
                        banks):
        def init_class(mod):
            tokens=mod["class"].split(".")            
            modpath, classname = ".".join(tokens[:-1]), tokens[-1]
            module=importlib.import_module(modpath)
            return getattr(module, classname)
        for mod in config["modules"]:
            modclass=init_class(mod)
            kwargs={}
            if mod["class"].lower().endswith("sampler"):
                kwargs={"banks": banks,
                        "samplekeys": [samplekey for samplekey in samplekeys
                                       if mod["name"] in samplekey["tags"]]}
            mod["instance"]=modclass(**kwargs)
    
    def init_modules(self,
                     proj,
                     config,
                     multipliers={"x": 1, "y": -2}):
        positions=self.init_layout(config)
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
                    mod.set_raw(k, v)
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
            color=self.new_color() if 0==i%4 else self.mutate_color(color)
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
        samplekeys=self.filter_samplekeys(patches=patches)
        self.init_modclasses(config=config,
                             samplekeys=samplekeys,
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
