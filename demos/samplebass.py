"""
- single bass sample with random sample cutoff
"""

from octavox.modules.banks import SVBanks, SVSampleKey

from octavox.modules.project import SVTrigs, SVNoteTrig, SVProject

import random, yaml

Config=yaml.safe_load("""
modules:
  - name: Sampler
    class: octavox.modules.sampler.SVSampler
  - name: Echo
    class: rv.modules.echo.Echo
    defaults:
      dry: 256
      wet: 128
      feedback: 128
      delay: 192
  - name: Distortion
    class: rv.modules.distortion.Distortion
    defaults:
      power: 64
  - name: Reverb
    class: rv.modules.reverb.Reverb
    defaults:
      wet: 4
links:
  - - Sampler
    - Echo
  - - Echo
    - Distortion
  - - Distortion
    - Reverb
  - - Reverb
    - Output
""")

BPM=120

if __name__=="__main__":
    banks=SVBanks("octavox/banks/pico")
    trigs=SVTrigs(nbeats=32)
    for i in range(trigs.nbeats):
        if random.random() < 0.25:
            params={"action": "cutoff",
                    "n": 4,
                    "i": random.choice(range(4))}
            samplekey=SVSampleKey({"bank": "baseck",
                                   "file": "03 BRA04.wav",
                                   "params": params})
            vel=0.5+random.random()*0.5
            trig=SVNoteTrig(mod="Sampler",
                            samplekey=samplekey,
                            vel=vel,
                            i=i)
            trigs.append(trig)
    project=SVProject().render(patches=[trigs.tracks],
                               config=Config,
                               banks=banks,
                               bpm=120)
    with open("tmp/samplebass.sunvox", 'wb') as f:
        project.write_to(f)
