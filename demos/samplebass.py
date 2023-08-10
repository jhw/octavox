"""
- single note bass sample, varying sample cutoff
"""

from octavox.modules.banks import SVBanks, SVSampleKey

from octavox.modules.project import SVTrigs, SVNoteTrig, SVProject

import os, random, re, yaml

Config=yaml.safe_load("""
modules:
  - name: BassSampler
    class: octavox.modules.sampler.SVSampler
  - name: Filter
    class: rv.modules.filter.Filter
    defaults:
      freq: 1500
      resonance: 1000
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
             limit,
             config=Config,
             nslices=4,
             nbeats=32,
             bpm=120):
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if random.random() < limit:
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
            trigs.append(note)
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
            raise RuntimeError("please enter bankname, filename, limit")
        _bankname, _filename, limit = sys.argv[1:4]
        if not re.search("^\\d+(\\.\\d+)$", limit):
            raise RuntimeError("limit is invalid")
        banks=SVBanks("octavox/banks/pico")
        bankname=banks.lookup(_bankname)
        bank=banks[bankname]
        filename=bank.lookup(_filename)
        print ("%s/%s" % (bankname, filename))
        destfilename="tmp/samplebass/%s-%s.sunvox" % (bankname,
                                                      filename.replace(" ", "-"))
        limit=float(limit)
        if limit > 1 or limit < 0:
            raise RuntimeError("limit is invalid")
        if not os.path.exists("tmp/samplebass"):
            os.makedirs("tmp/samplebass")
        generate(banks=banks,
                 bankname=bankname,
                 limit=limit,
                 filename=filename,
                 destfilename=destfilename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
        
        
