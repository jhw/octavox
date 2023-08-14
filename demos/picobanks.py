"""
- dump each Pico bank as an individual sunvox project
"""

from octavox.modules.banks import SVBanks

from octavox.modules.model import SVTrigs, SVSampleKey, SVNoteTrig

from octavox.modules.project import SVProject

import os, yaml

Modules=yaml.safe_load("""
- name: Sampler
  class: octavox.modules.sampler.SVSampler
""")

Links=yaml.safe_load("""
- - Sampler
  - Output
""")

def generate(bankname,
             bank,
             banks,
             destfilename,
             modules=Modules,
             links=Links,
             bpm=120):
    wavfiles=bank.wavfiles
    nbeats=len(wavfiles)
    trigs=SVTrigs(nbeats=nbeats)
    for i, wavfile in enumerate(wavfiles):
        samplekey=SVSampleKey({"bank": bankname,
                               "file": wavfile})
        note=SVNoteTrig(mod="Sampler",
                        samplekey=samplekey,
                        i=i)
        trigs.append(note)
    project=SVProject().render(patches=[trigs.tracks],
                               modconfig=modules,
                               links=links,
                               banks=banks,
                               bpm=bpm)
    with open(destfilename, 'wb') as f:
        project.write_to(f)

if __name__=="__main__":
    banks=SVBanks("octavox/banks/pico")
    if not os.path.exists("tmp/picobanks"):
        os.makedirs("tmp/picobanks")
    for bankname, bank in banks.items():
        print (bankname)
        destfilename="tmp/picobanks/%s.sunvox" % bankname
        generate(bankname=bankname,
                 bank=bank,
                 banks=banks,
                 destfilename=destfilename)

