"""
- single note bass sample, varying sample cutoff
"""

from octavox.modules.banks import SVBanks, SVSampleKey

from octavox.modules.project import SVTrigs, SVNoteTrig, SVFXTrig, SVProject

from octavox.projects import Q

from datetime import datetime

import os, random, re, yaml

Config=yaml.safe_load("""
modules:
  - name: BassSampler
    class: octavox.modules.sampler.SVSampler
  - name: PitchShifter
    class: rv.modules.pitchshifter.PitchShifter
  - name: Filter
    class: rv.modules.filter.Filter
    defaults:
      freq: 0
      resonance: 1250
      type: 0 # LP
  - name: Echo
    class: rv.modules.echo.Echo
    defaults:
      dry: 256
      wet: 64
      feedback: 128
      delay: 192
  - name: Reverb
    class: rv.modules.reverb.Reverb
    defaults:
      wet: 4
links:
  - - BassSampler
    - PitchShifter
  - - PitchShifter
    - Filter
  - - Filter
    - Echo
  - - Echo
    - Reverb
  - - Reverb
    - Output
""")

Patterns=[0, 0, 0, -2]

def generate(banks,
             bankname,
             filename,
             destfilename,
             seed,
             density,
             freqmin,
             freqmax,
             modules=Config["modules"],
             links=Config["links"],
             patterns=Patterns,
             nslices=4,
             nbeats=32,
             bpm=120):
    trigs=SVTrigs(nbeats=nbeats)
    q=Q(seed)
    pattern=q.choice(patterns)
    for i in range(nbeats):
        if q.random() < density:
            params={"action": "cutoff",
                    "n": nslices,
                    "i": q.choice(range(nslices))}
            samplekey=SVSampleKey({"bank": bankname,
                                   "file": filename,
                                   "params": params})
            vel=0.5+q.random()*0.5
            notetrig=SVNoteTrig(mod="BassSampler",
                                samplekey=samplekey,
                                vel=vel,
                                i=i)
            freq=freqmin+int((freqmax-freqmin)*q.random())
            freqtrig=SVFXTrig(mod="Filter",
                              ctrl="freq",
                              value=freq,
                              i=i)
            trigs+=[notetrig,
                    freqtrig]
    project=SVProject().render(patches=[trigs.tracks],
                               config={"modules": modules,
                                       "links": links},
                               banks=banks,
                               bpm=bpm)
    with open(destfilename, 'wb') as f:
        project.write_to(f)
    
if __name__=="__main__":
    try:
        import sys
        if len(sys.argv) < 7:
            raise RuntimeError("please enter bankname, filename, seed, density, freqmin, freqmax")
        _bankname, _filename, seed, density, freqmin, freqmax = sys.argv[1:7]
        if not re.search("^\\d+", seed):
            raise RuntimeError("seed is invalid")
        seed=int(seed)
        if not re.search("^\\d+(\\.\\d+)$", density):
            raise RuntimeError("density is invalid")
        density=float(density)
        if density > 1 or density < 0:
            raise RuntimeError("density is invalid")
        if not re.search("^\\d+$", freqmin):
            raise RuntimeError("freqmax is invalid")
        freqmin=int(freqmin)
        if not re.search("^\\d+$", freqmax):
            raise RuntimeError("freqmax is invalid")
        freqmax=int(freqmax)
        banks=SVBanks("octavox/banks/pico")
        bankname=banks.lookup(_bankname)
        bank=banks[bankname]
        filename=bank.lookup(_filename)
        print ("%s/%s" % (bankname, filename))       
        if not os.path.exists("tmp/samplebass"):
            os.makedirs("tmp/samplebass")
        timestamp=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/samplebass/%s-%s-%s.sunvox" % (timestamp,
                                                         bankname,
                                                         filename.replace(" ", "-"))
        generate(banks=banks,
                 bankname=bankname,
                 seed=seed, 
                 density=density,
                 freqmin=freqmin,
                 freqmax=freqmax,
                 filename=filename,
                 destfilename=destfilename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
        
        
