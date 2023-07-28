from octavox.modules.banks import SVBanks, SVSampleKey

from octavox.modules.project import SVProject, SVPatch

import os, yaml

Config=yaml.safe_load("""
modules:
  - name: Sampler
    class: octavox.modules.samplers.SVSampler
    key: trig
links:
  - - Sampler
    - Output
""")

SrcDirName, DestDirName = ("tmp/banks/pico/zipped",
                           "tmp/banks/pico/sunvox")

def render_project(banks,
                   bankname,
                   patch,
                   nbeats,
                   dirname=DestDirName,
                   config=Config):
    project=SVProject().render(patches=[patch],
                               config=config,
                               banks=banks)
    projfile="%s/%s.sunvox" % (dirname, bankname)
    with open(projfile, 'wb') as f:
        project.write_to(f)

if __name__=="__main__":
    for path in [DestDirName]:
        if not os.path.exists(path):
            os.makedirs(path)            
    banks=SVBanks(SrcDirName)
    for bankname, bank in banks.items():
        print (bankname)
        wavfiles=bank.wavfiles
        nbeats=len(wavfiles)
        patch=SVPatch(nbeats=nbeats)
        patch["trig"]=[]
        for i, wavfile in enumerate(wavfiles):
            key=SVSampleKey.create(bank=bankname,
                                   file=wavfile)
            trig={"mod": "Sampler",
                  "i": i,
                  "key": key}
            patch["trig"].append(trig)
        render_project(banks=banks,
                       bankname=bankname,
                       patch=patch,
                       nbeats=nbeats)
