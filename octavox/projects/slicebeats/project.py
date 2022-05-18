from rv.api import Project as RVProject
from rv.pattern import Pattern as RVPattern
from rv.note import Note as RVNote

from rv.modules.drumsynth import DrumSynth as RVDrumSynth
from rv.modules.echo import Echo as RVEcho
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.modules.sampler import SVSampler

import random, yaml

Drum, Sampler = "Drum", "Sampler"

Modules=yaml.safe_load("""
- name: Sampler
  # class: RVSampler
  class: SVSampler
  position:
    x: -3
    y: -1
- name: Drum
  class: RVDrumSynth
  position:
    x: -3
    y: 1
- name: Echo
  class: RVEcho
  position:
    x: -3
  defaults:
    dry: 128
    wet: 128
    delay: 192
- name: Distortion
  class: RVDistortion
  position:
    x: -2
  defaults:
    power: 64
- name: Reverb
  class: RVReverb
  position:
    x: -1
  defaults:
    wet: 4
""")

Links=yaml.safe_load("""
- - Sampler
  - Echo
- - Drum
  - Echo
- - Echo
  - Distortion
- - Distortion
  - Reverb
- - Reverb
  - Output
""")

Globals=yaml.safe_load("""
bpm: 120
volume: 256
""")

class SVTrig(dict):

    def __init__(self, item):
        dict.__init__(self, item)

    def render(self, modules, controllers, volume=128):
        trig=1+self["id"]
        mod=1+modules[self["mod"]]
        vel=max(1, int(self["vel"]*volume)) 
        return RVNote(note=trig,
                      vel=vel,
                      module=mod)

class SVEffect(dict):
    
    def __init__(self, item):
        dict.__init__(self, item)
        
    def render(self, modules, controllers,
               ctrlmult=256,
               maxvalue=256*128):
        mod=1+modules[self["mod"]]
        ctrl=ctrlmult*controllers[self["mod"]][self["attr"]]
        value=int(self["value"]*maxvalue) # don't add 1 as will exceed max
        return RVNote(module=mod,
                      ctl=ctrl,
                      val=value)

class SVOffset:

    def __init__(self):
        self.value=0
        self.count=0

    def increment(self, value):
        self.value+=value
        self.count+=1

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
    
    def init_modules(self, proj, modules):
        for i, item in enumerate(modules):
            klass=eval(item["class"])
            kwargs={"name": item["name"]}
            for attr, mult in [("x", 1),
                               ("y", -2)]:
                if attr in item["position"]:
                    value=item["position"][attr]
                    kwargs[attr]=int(512+128*mult*value)
            mod=klass(**kwargs)
            if "defaults" in item:
                for k, v in item["defaults"].items():
                    mod.set_raw(k, v)
            proj.attach_module(mod)

    def link_modules(self, proj, links):
        modmap={mod.name: mod.index
                for mod in proj.modules}
        for src, dest in links:
            proj.connect(proj.modules[modmap[src]],
                         proj.modules[modmap[dest]])

    def init_grid(self, patch):
        def classfn(type):
            return SVTrig if type=="trig" else SVEffect
        return [{k:classfn(v["type"])(v)
                 for k, v in track.items()}
                for track in patch["tracks"]]
        
    def init_pattern(self,
                     proj,
                     modules,
                     controllers,
                     patch,
                     offset,
                     color,
                     height=64):
        grid=self.init_grid(patch)
        def notefn(self, j, i):
            return grid[i][j].render(modules,
                                     controllers) if j in grid[i] else RVNote()
        rvpat=RVPattern(name=str(offset.count),
                        fg_color=(255, 255, 255),
                        lines=patch["n"],
                        tracks=len(patch["tracks"]),
                        x=offset.value,
                        y_size=height,
                        bg_color=color)
        rvpat.set_via_fn(notefn)
        offset.increment(patch["n"])                
        return rvpat

    def init_controllers(self, modules):
        controllers={}
        for mod in modules:
            controllers.setdefault(mod.name, {})
            for controller in mod.controllers.values():
                controllers[mod.name].setdefault(controller.name, {})
                controllers[mod.name][controller.name]=controller.number
        return controllers

    def init_patterns(self, proj, patches):
        modmap={mod.name: mod.index
                for mod in proj.modules}
        ctrlmap=self.init_controllers(proj.modules)
        offset=SVOffset()
        patterns, color = [], None
        for i, patch in enumerate(patches):
            color=self.new_color() if 0==i%4 else self.mutate_color(color)
            pattern=self.init_pattern(proj,
                                      modmap,
                                      ctrlmap,
                                      patch,
                                      offset,
                                      color)
            patterns.append(pattern)
        return patterns

    def render(self,
               banks,
               patches,
               globalz=Globals,
               modules=Modules,
               links=Links):
        proj=RVProject()
        proj.initial_bpm=globalz["bpm"]
        proj.global_volume=globalz["volume"]
        self.init_modules(proj, modules)
        self.link_modules(proj, links)
        sampler={mod.name: mod
                 for mod in proj.modules}[Sampler]
        sampler.initialise(banks, patches)
        proj.patterns=self.init_patterns(proj, patches)
        return proj

if __name__=="__main__":
    pass
