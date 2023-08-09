"""
- dump each Pico bank to a separate sunvox file so you can hear all the sounds
"""

from octavox.modules.banks import SVBanks, SVSampleKey

from octavox.modules.project import SVTrigs, SVNoteTrig, SVTrigs, SVProject

import yaml

Config=yaml.safe_load("""
modules:
  - name: Sampler
    class: octavox.modules.sampler.SVSampler
links:
  - - Sampler
    - Output
""")

SrcDir, DestDir = ("octavox/banks/pico",
                   "tmp/banks/pico")

BPM=120

def dump_project(bankname, bank, banks,
                 dirname=DestDir,
                 config=Config,
                 bpm=BPM):
    wavfiles=bank.wavfiles
    nbeats=len(wavfiles)
    trigs=SVTrigs(nbeats=nbeats)
    for i, wavfile in enumerate(wavfiles):
        samplekey=SVSampleKey({"bank": bankname,
                               "file": wavfile})
        trig=SVNoteTrig(mod="Sampler",
                        samplekey=samplekey,
                        i=i)
        trigs.append(trig)
    project=SVProject().render(patches=[trigs.tracks],
                               config={"modules": config["modules"],
                                       "links": config["links"]},
                               banks=banks,
                               bpm=bpm)
    projfile="%s/%s.sunvox" % (dirname, bankname)
    with open(projfile, 'wb') as f:
        project.write_to(f)

if __name__=="__main__":
    import os
    for path in [DestDir]:
        if not os.path.exists(path):
            os.makedirs(path)            
    banks=SVBanks(SrcDir)
    for bankname, bank in banks.items():
        print (bankname)
        dump_project(bankname, bank, banks)

