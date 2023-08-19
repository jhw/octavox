from octavox.modules.model import SVTrigs, SVNoteTrig, SVFXTrig

from octavox.modules.project import SVProject

from datetime import datetime

import os, random, yaml

Modules=yaml.safe_load("""
- name: Generator
  class: rv.modules.analoggenerator.AnalogGenerator
  defaults:
    waveform: 2 # square
    sustain: 0
    release: 256
    filter: 1 # LP
    f_envelope: 1
    f_freq_hz: 4096
    f_resonance: 1250
    f_release: 192
""")

Links=yaml.safe_load("""
- - Generator
  - Output
""")

def generate(destfilename,
             modules=Modules,
             links=Links,
             nbeats=32,
             bpm=120):
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if random.random() < 0.66666:
            note=SVNoteTrig(mod="Generator",
                            note=12,
                            i=i)
            ffreq=SVFXTrig(mod="Generator",
                           ctrl="f_freq_hz",
                           value=10000+int(random.random()*5000),
                           i=i)
            frelease=SVFXTrig(mod="Generator",
                              ctrl="f_release",
                              value=20000+int(random.random()*5000),
                              i=i)
            trigs+=[note, ffreq, frelease]
    project=SVProject().render(patches=[trigs.tracks],
                               modconfig=modules,
                               links=links,
                               bpm=bpm)
    with open(destfilename, 'wb') as f:
        project.write_to(f)

if __name__=="__main__":
    try:
        if not os.path.exists("tmp/demos/analog303"):
            os.makedirs("tmp/demos/analog303")
        ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/demos/analog303/%s.sunvox" % ts
        generate(destfilename=destfilename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
