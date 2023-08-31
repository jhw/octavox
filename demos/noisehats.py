from octavox.core.model import SVNoteTrig, SVFXTrig, SVTrigs

from octavox.core.project import SVProject

from datetime import datetime

import os, random, yaml

Modules=yaml.safe_load("""
- name: Generator
  class: rv.modules.analoggenerator.AnalogGenerator
  defaults:
    waveform: 3 # noise
    attack: 0
    sustain: 0
    release: 0
- name: Filter
  class: rv.modules.filter.Filter
  defaults:
    type: 1 # HP
    freq: 9000
    resonance: 1350
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 64 # NB
    delay: 144
    delay_unit: 3 # tick
- name: Reverb
  class: rv.modules.reverb.Reverb
  defaults:
    wet: 4
""")

Links=yaml.safe_load("""
- - Generator
  - Filter
- - Filter
  - Echo
- - Echo
  - Reverb
- - Reverb
  - Output
""")

def noise_hats(trigfn,
               notefn,
               nticks):
    trigs=SVTrigs(nbeats=nticks)
    for i in range(nticks):
        if trigfn(i):
            notes=notefn(i)
            trigs+=notes
    return trigs.tracks

def spawn_patches(nticks,
                  nbeats,
                  npatches):
    def trigfn(i):
        return (0 == i % nticks and
                random.random() < 0.5)
    def repeats(i, nticks):
        return [[i],
                [i],
                [i],
                [i],
                [i, i+nticks/2],
                [i, i+nticks/2],
                [i+k for k in range(nticks)]]    
    def flatten(lists):
        flattened=[]
        for l in lists:
            flattened+=l
        return flattened    
    def notefn(i, note=96):
        fxvalues=["0000", random.choice(["3000", "3000", "3000", "6000"])]
        if random.random() < 0.5:
            fxvalues=list(reversed(fxvalues))
        notes=[[SVNoteTrig(mod="Generator",
                           note=note,
                           vel=random.random()*0.3+0.7,
                           i=j),
                SVFXTrig(target="Generator/attack",
                         value=int(fxvalues[0], 16),
                         i=j),
                SVFXTrig(target="Generator/release",
                         value=int(fxvalues[1], 16),
                         i=j)]
               for j in random.choice(repeats(i, nticks))]
        return flatten(notes)
    return [noise_hats(trigfn=trigfn,
                       notefn=notefn,
                       nticks=nbeats*nticks)
            for i in range(npatches)]

if __name__=="__main__":
    try:
        npatches, nbeats, nticks, bpm = 32, 16, 4, 120
        patches=spawn_patches(npatches=npatches,
                              nbeats=nbeats,
                              nticks=nticks)
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   bpm=bpm*nticks)
        if not os.path.exists("tmp/noisehats"):
            os.makedirs("tmp/noisehats")
        ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/noisehats/%s.sunvox" % ts
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
