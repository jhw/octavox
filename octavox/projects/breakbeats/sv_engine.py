from rv.api import Project as RVProject
from rv.pattern import Pattern as RVPattern
from rv.note import Note as RVNote
from rv.note import NOTE as RVNOTE

from rv.modules.sampler import Sampler as RVSampler
from rv.modules.drumsynth import DrumSynth as RVDrumSynth
from rv.modules.echo import Echo as RVEcho
from rv.modules.distortion import Distortion as RVDistortion
from rv.modules.reverb import Reverb as RVReverb

from octavox.projects.breakbeats.utils.sv_utils import *

from octavox.projects.breakbeats.utils.sampler_utils import load_sample

import yaml

Drum, Sampler = "Drum", "Sampler"

Modules=yaml.safe_load("""
- name: Sampler
  class: RVSampler
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
    wet: 8
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

class SVPatches(list):

    def ___init__(self, patches):
        list.__init__(self, patches)

    """
    - returns list of all unique sample keys listed in patches
    - so you only need to load used samples from banks, thereby reducing overall sunvox file size
    - order not important because patch is updated with note of whatever slot a particular sample is inserted into
    """
            
    @property
    def sample_keys(self):
        def keyfn(key):
            return "%s:%i" % (key["bank"],
                              key["id"])
        keys={}
        for patch in self:
            for track in patch["tracks"]:
                if track["type"]=="trig":
                    trigs=track["notes"]
                    for trig in trigs.values():
                        if trig and trig["mod"]==Sampler:
                            keys[keyfn(trig["key"])]=trig["key"]
        return list(keys.values())

    def add_sample_ids(self, mapping):
        for patch in self:
            for track in patch["tracks"]:
                if track["type"]=="trig":
                    trigs=track["notes"]
                    for trig in trigs.values():
                        if trig and trig["mod"]==Sampler:
                            trig["id"]=mapping.index(trig["key"])
    
def render(banks,
           patches,
           globalz=Globals,
           modules=Modules,
           links=Links):
    def init_modules(proj, modules):
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
    def link_modules(proj, links):
        modmap={mod.name: mod.index
                for mod in proj.modules}
        for src, dest in links:
            proj.connect(proj.modules[modmap[src]],
                         proj.modules[modmap[dest]])
    def init_sampler(proj, banks, patches, maxslots=120):
        sampler={mod.name: mod
                 for mod in proj.modules}[Sampler]
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        samplekeys=patches.sample_keys
        if len(samplekeys) > maxslots:
            raise RuntimeError("sampler max slots exceeded")
        print ("%i sampler slots used" % len(samplekeys))
        patches.add_sample_ids(samplekeys)
        for i, samplekey in enumerate(samplekeys):
            sampler.note_samples[notes[i]]=i
            src=banks.get_wavfile(samplekey)
            load_sample(src, sampler, i)
            sample=sampler.samples[i]
            sample.relative_note+=(root-i)
    class Trig(dict):
        def __init__(self, item):
            dict.__init__(self, item)
        def render(self, modules, controllers, volume=128):
            trig=1+self["id"]
            mod=1+modules[self["mod"]]
            vel=max(1, int(self["vel"]*volume)) 
            return RVNote(note=trig,
                          vel=vel,
                          module=mod)
    class Effect(dict):
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
    def init_pattern(proj, modules, controllers, patch, offset, color, height=64):
        def init_grid(patch):
            def classfn(type):
                return Trig if type=="trig" else Effect
            return [{k:classfn(track["type"])(v)
                     for k, v in track["notes"].items()}
                    for track in patch["tracks"]]
        grid=init_grid(patch)
        def notefn(self, j, i):
            return grid[i][j].render(modules, controllers) if j in grid[i] else RVNote()
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
    class Offset:
        def __init__(self):
            self.value=0
            self.count=0
        def increment(self, value):
            self.value+=value
            self.count+=1
    def init_patterns(proj, patches):
        def init_controllers(modules):
            controllers={}
            for mod in modules:
                controllers.setdefault(mod.name, {})
                for controller in mod.controllers.values():
                    controllers[mod.name].setdefault(controller.name, {})
                    controllers[mod.name][controller.name]=controller.number
            return controllers
        modmap={mod.name: mod.index
                for mod in proj.modules}
        ctrlmap=init_controllers(proj.modules)
        offset=Offset()
        patterns, color = [], None
        for i, patch in enumerate(patches):
            color=new_color() if 0==i%4 else mutate_color(color)
            pattern=init_pattern(proj, modmap, ctrlmap, patch, offset, color)
            patterns.append(pattern)
        return patterns
    proj=RVProject()
    proj.initial_bpm=globalz["bpm"]
    proj.global_volume=globalz["volume"]
    init_modules(proj, modules)
    link_modules(proj, links)
    init_sampler(proj, banks, SVPatches(patches))
    proj.patterns=init_patterns(proj, patches)
    return proj

if __name__=="__main__":
    pass
