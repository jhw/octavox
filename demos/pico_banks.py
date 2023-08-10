"""
- dump each Pico bank as an individual sunvox project
"""

from octavox.modules.banks import SVBanks, SVSampleKey

from octavox.modules.project import SVTrigs, SVNoteTrig, SVTrigs, SVProject

import os, yaml

Config=yaml.safe_load("""
modules:
  - name: Sampler
    class: octavox.modules.sampler.SVSampler
links:
  - - Sampler
    - Output
""")

def generate(bankname,
             bank,
             banks,
             destfilename,
             config=Config,
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
                               config={"modules": config["modules"],
                                       "links": config["links"]},
                               banks=banks,
                               bpm=bpm)
    with open(destfilename, 'wb') as f:
        project.write_to(f)

if __name__=="__main__":
    banks=SVBanks("octavox/banks/pico")
    if not os.path.exists("tmp/banks/pico"):
        os.makedirs("tmp/banks/pico")
    for bankname, bank in banks.items():
        print (bankname)
        destfilename="tmp/banks/pico/%s.sunvox" % bankname
        generate(bankname=bankname,
                 bank=bank,
                 banks=banks,
                 destfilename=destfilename)

