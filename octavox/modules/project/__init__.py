from rv.api import Project as RVProject
from rv.pattern import Pattern as RVPattern

from octavox.modules import load_class

from octavox.modules.banks import SVPool

from octavox.modules.project.modules import SVColor, init_mod_layout, Output

Volume, Height = 256, 64
                    
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
                filtered=pool.filter(mod["name"])
                kwargs={"banks": banks,
                        "pool": filtered}
            mod["instance"]=modclass(**kwargs)
                
    def init_modules(self,
                     proj,
                     modconfig,
                     links,
                     multipliers={"x": 1, "y": -1}):
        positions=init_mod_layout(modules=modconfig,
                                  links=links)
        modules={}
        for i, moditem in enumerate(modconfig):
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
               banks,
               bpm,
               volume=Volume):
        proj=RVProject()
        proj.initial_bpm=bpm
        proj.global_volume=volume
        pool=self.filter_pool(patches=patches)
        self.init_modclasses(modconfig=modconfig,
                             pool=pool,
                             banks=banks)
        modules=self.init_modules(proj=proj,
                                  modconfig=modconfig,
                                  links=links)
        self.link_modules(proj=proj,
                          links=links,
                          modules=modules)
        proj.patterns=self.init_patterns(modules=modules,
                                         patches=patches)
        return proj

if __name__=="__main__":
    pass
