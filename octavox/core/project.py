from rv.api import Project as RVProject
from rv.pattern import Pattern as RVPattern

from octavox.core import load_class

from octavox.core.banks import SVPool

import random

Volume, Height = 256, 64

Output= "Output"

class SVColor(list):

    @classmethod
    def randomise(self,
                  offset=64,
                  contrast=128,
                  n=16):
        def randomise(offset):
            return [int(offset+random.random()*(255-offset))
                    for i in range(3)]
        for i in range(n):
            color=randomise(offset)
            if (max(color)-min(color)) > contrast:
                return SVColor(color)
        return SVColor([127 for i in range(3)])
    
    def __init__(self, rgb=[]):
        list.__init__(self, rgb)

    def mutate(self,
               contrast=32):
        values=range(-contrast, contrast)
        return SVColor([min(255, max(0, rgb+random.choice(values)))
                        for rgb in self])
                    
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
                        modconfig,
                        pool,
                        banks):
        for mod in modconfig:
            modclass=load_class(mod["class"])
            kwargs={}
            if mod["class"].lower().endswith("sampler"):
                filtered=pool.filter_tag(mod["name"])
                kwargs={"banks": banks,
                        "pool": filtered}
            mod["instance"]=modclass(**kwargs)
                
    def init_modules(self,
                     proj,
                     modconfig):
        modules={}
        for i, moditem in enumerate(modconfig):
            mod, name = moditem["instance"], moditem["name"]
            setattr(mod, "name", name)
            if "defaults" in moditem:
                for k, v in moditem["defaults"].items():
                    mod.set_raw(k, v)
            proj.attach_module(mod)
            modules[name]=mod
        return modules

    def link_modules(self,
                     proj,
                     links,
                     modules):
        output=sorted(proj.modules, key=lambda x: -x.index).pop()
        for src, dest in links:
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
        from rv.note import Note
        def notefn(self, j, i):
            return grid[i][j].render(modules,
                                     controllers) if j in grid[i] else Note()
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
               modconfig,
               links,
               bpm,
               banks=None,
               volume=Volume):
        proj=RVProject()
        proj.initial_bpm=bpm
        proj.global_volume=volume
        pool=self.filter_pool(patches=patches)
        self.init_modclasses(modconfig=modconfig,
                             pool=pool,
                             banks=banks)
        modules=self.init_modules(proj=proj,
                                  modconfig=modconfig)
        self.link_modules(proj=proj,
                          links=links,
                          modules=modules)
        proj.patterns=self.init_patterns(modules=modules,
                                         patches=patches)
        return proj

if __name__=="__main__":
    pass
