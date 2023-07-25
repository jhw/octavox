from rv.api import Project as RVProject
from rv.pattern import Pattern as RVPattern
from rv.note import Note as RVNote

# START TEMP CODE

from rv.modules.echo import Echo as RVEcho
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.modules.sampler import SVSampler

# END TEMP CODE

import math, random, yaml

Output="Output"

Globals=yaml.safe_load("""
bpm: 120
volume: 256
""")

BreakSz, Height = 16, 64

class SVTrig(dict):

    def __init__(self, item):
        dict.__init__(self, item)

    def render(self, modules, controllers,
               volume=128):
        mod=modules[self["mod"]]
        trig=1+(mod.lookup(self["key"]) if "key" in self else self["id"])
        modid=1+mod.index # NB 1+
        vel=max(1, int(self["vel"]*volume))
        return RVNote(note=trig,
                      vel=vel,
                      module=modid)

class SVEffect(dict):
    
    def __init__(self, item):
        dict.__init__(self, item)
        
    def render(self, modules, controllers,
               ctrlmult=256,
               maxvalue=256*128):
        mod, controller = modules[self["mod"]], controllers[self["mod"]]
        modid=1+mod.index # NB 1+
        ctrlid=ctrlmult*controller[self["ctrl"]]
        ctrlvalue=int(self["v"]*maxvalue) # NB **NOT** 1+
        return RVNote(module=modid,
                      ctl=ctrlid,
                      val=ctrlvalue)

class SVOffset:

    def __init__(self):
        self.value=0
        self.count=0

    def increment(self, value):
        self.value+=value
        self.count+=1

class ModGrid(dict):

    @classmethod
    def all(self, sz):
        offset=int(sz/2)
        return [(x-offset, y-offset)
                for y in range(sz)
                for x in range(sz)]
    
    @classmethod
    def randomise(self, modnames):
        sz=1+int(math.ceil(len(modnames)**0.5)) # NB +1 to ensure decent amount of whitespace in which to move cells around
        coords=sorted(ModGrid.all(sz),
                      key=lambda x: random.random())[:len(modnames)]
        return ModGrid(sz=sz,
                       item={mod:xy
                             for mod, xy in zip(modnames, coords)})
    
    def __init__(self, sz, item):
        dict.__init__(self, item)
        self.sz=sz

    def clone(self):
        return ModGrid(sz=self.sz,
                       item={k:v for k, v in self.items()})

    @property
    def allocated(self):
        allocated=set(self.values())
        allocated.add((0, 0))
        return list(allocated)

    @property
    def unallocated(self):
        all, allocated = ModGrid.all(self.sz), self.allocated
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
    
    def new_color(self, offset=64, contrast=128, n=16):
        for i in range(n):
            color=self.random_color(offset)
            if (max(color)-min(color)) > contrast:
                return color
        return [127 for i in range(3)]

    def mutate_color(self, color, contrast=32):
        values=range(-contrast, contrast)
        return [min(255, max(0, rgb+random.choice(values)))
                for rgb in  color]

    def init_layout(self, modconfig, n=1000):
        def shuffle(grid, links, q):
            clone=grid.clone()
            clone.shuffle(q)
            distance=clone.rms_distance(links)
            return (clone, distance)
        modnames=[Output]+[mod["name"]
                           for mod in modconfig["modules"]]
        grid=ModGrid.randomise(modnames)
        links=modconfig["links"]
        best=grid.rms_distance(links)
        for i in range(n):
            q=int(math.ceil(len(modnames)*(n-i)/n))
            clones=sorted([shuffle(grid, links, q)
                           for i in range(10)],
                          key=lambda x: -x[1])
            newgrid, newbest = clones[-1]
            if newbest < best:
                grid, best = newgrid, newbest
        return grid

    def filter_samples(self,
                       patches,
                       nbeats,
                       density):
        samplekeys={}
        for patch in patches:
            for track in patch.render(nbeats=nbeats,
                                      density=density):
                for trig in track:
                    if "key" in trig:
                        key=trig["mod"][:2].lower()
                        samplekeys.setdefault(key, set()) # NB set()
                        samplekeys[key].add(tuple(trig["key"])) # NB tuple()
        return {k:list(v)
                for k, v in samplekeys.items()}
    
    def init_modclasses(self,
                        modconfig,
                        samplekeys,
                        banks):
        for mod in modconfig["modules"]:
            modclass=eval(mod["classname"])
            if "Sampler" in mod["name"]:
                key=mod["name"][:2].lower() # change?
                kwargs={"samplekeys": samplekeys[key] if key in samplekeys else [],
                        "banks": banks}
            else:
                kwargs={}
            mod["instance"]=modclass(**kwargs)
    
    def init_modules(self,
                     proj,
                     modconfig,
                     multipliers={"x": 1, "y": -2}):
        positions=self.init_layout(modconfig)
        modules={}
        for i, moditem in enumerate(modconfig["modules"]):
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
    
    def link_modules(self, proj, modconfig, modules):
        output=sorted(proj.modules, key=lambda x: -x.index).pop()
        for src, dest in modconfig["links"]:
            proj.connect(modules[src],
                         output if dest==Output else modules[dest])

    def init_grid(self, patch):
        def classfn(v):
            return SVEffect if "ctrl" in v else SVTrig
        return [{note["i"]:classfn(note)(note)
                 for note in track}
                for track in patch]

    def attach_pattern(fn):
        def wrapped(*args, **kwargs):
            rvpat=fn(*args, **kwargs)
            kwargs["patterns"].append(rvpat)
            kwargs["offset"].increment(kwargs["nbeats"])
        return wrapped
    
    @attach_pattern
    def init_pattern(self,
                     patterns,
                     modules,
                     controllers,
                     patch,
                     nbeats,
                     offset,
                     color,
                     height=Height):
        grid=self.init_grid(patch)
        def notefn(self, j, i):
            return grid[i][j].render(modules,
                                     controllers) if j in grid[i] else RVNote()
        return RVPattern(lines=nbeats,
                        tracks=len(patch),
                         x=offset.value,
                         y_size=height,
                         bg_color=color).set_via_fn(notefn)

    @attach_pattern
    def init_blank(self,
                   patterns,
                   patch,
                   nbeats,
                   offset,
                   color,
                   height=Height):
        def notefn(self, j, i):
            return RVNote()
        return RVPattern(lines=nbeats,
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
                      patches,
                      nbeats,
                      nbreaks,
                      density):
        controllers=self.init_controllers(modules)
        offset=SVOffset()
        patterns, color = [], None
        for i, patch in enumerate(patches):
            rendered=patch.render(nbeats=nbeats,
                                  density=density)
            color=self.new_color() if 0==i%4 else self.mutate_color(color)
            self.init_pattern(patterns=patterns,
                              modules=modules,
                              controllers=controllers,
                              patch=rendered,
                              nbeats=nbeats,
                              offset=offset,
                              color=color)            
            for i in range(nbreaks):
                self.init_blank(patterns=patterns,
                                patch=rendered,
                                nbeats=nbeats,
                                offset=offset,
                                color=color)
        return patterns

    def render(self,
               patches,
               modconfig,
               nbeats,
               nbreaks,
               density,
               banks,
               globalz=Globals):
        proj=RVProject()
        proj.initial_bpm=globalz["bpm"]
        proj.global_volume=globalz["volume"]
        samplekeys=self.filter_samples(patches=patches,
                                       nbeats=nbeats,
                                       density=density)
        self.init_modclasses(modconfig=modconfig,
                             samplekeys=samplekeys,
                             banks=banks)
        modules=self.init_modules(proj=proj,
                                  modconfig=modconfig)
        self.link_modules(proj=proj,
                          modconfig=modconfig,
                          modules=modules)
        proj.patterns=self.init_patterns(modules=modules,
                                         patches=patches,
                                         nbeats=nbeats,
                                         nbreaks=nbreaks,
                                         density=density)
        return proj

if __name__=="__main__":
    pass
