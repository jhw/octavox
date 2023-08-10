"""
- single note bass sample, varying sample cutoff
"""

from octavox.modules.banks import SVBanks, SVSampleKey

from octavox.modules.project import SVTrigs, SVNoteTrig, SVFXTrig, SVProject

from datetime import datetime

import os, random, re, yaml

Config=yaml.safe_load("""
modules:
  - name: BassSampler
    class: octavox.modules.sampler.SVSampler
  - name: Filter
    class: rv.modules.filter.Filter
    defaults:
      resonance: 1250
  - name: Echo
    class: rv.modules.echo.Echo
    defaults:
      dry: 256
      wet: 64
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
  - - BassSampler
    - Filter
  - - Filter
    - Echo
  - - Echo
    - Distortion
  - - Distortion
    - Reverb
  - - Reverb
    - Output
""")

def generate(banks,
             bankname,
             filename,
             destfilename,
             density,
             config=Config,
             nslices=4,
             nbeats=32,
             bpm=120):
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if random.random() < density:
            params={"action": "cutoff",
                    "n": nslices,
                    "i": random.choice(range(nslices))}
            samplekey=SVSampleKey({"bank": bankname,
                                   "file": filename,
                                   "params": params})
            vel=0.5+random.random()*0.5
            note=SVNoteTrig(mod="BassSampler",
                            samplekey=samplekey,
                            vel=vel,
                            i=i)
            freq=SVFXTrig(mod="Filter",
                          ctrl="freq",
                          value=0.25*random.random(),
                          i=i)
            trigs+=[note, freq]
    project=SVProject().render(patches=[trigs.tracks],
                               config=config,
                               banks=banks,
                               bpm=bpm)
    with open(destfilename, 'wb') as f:
        project.write_to(f)
    
if __name__=="__main__":
    try:
        import sys
        if len(sys.argv) < 4:
            raise RuntimeError("please enter bankname, filename, density")
        _bankname, _filename, density = sys.argv[1:4]
        if not re.search("^\\d+(\\.\\d+)$", density):
            raise RuntimeError("density is invalid")
        banks=SVBanks("octavox/banks/pico")
        bankname=banks.lookup(_bankname)
        bank=banks[bankname]
        filename=bank.lookup(_filename)
        print ("%s/%s" % (bankname, filename))
        density=float(density)
        if density > 1 or density < 0:
            raise RuntimeError("density is invalid")
        if not os.path.exists("tmp/samplebass"):
            os.makedirs("tmp/samplebass")
        timestamp=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/samplebass/%s-%s-%s.sunvox" % (timestamp,
                                                         bankname,
                                                         filename.replace(" ", "-"))
        generate(banks=banks,
                 bankname=bankname,
                 density=density,
                 filename=filename,
                 destfilename=destfilename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
        
        
