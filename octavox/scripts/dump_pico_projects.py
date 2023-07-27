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

def render_project(banks, bankname, patch, nbeats, config=Config):
    project=SVProject().render(patches=[patch],
                               config=config,
                               banks=banks)
    projfile="tmp/banks/pico/%s.sunvox" % bankname
    with open(projfile, 'wb') as f:
        project.write_to(f)

if __name__=="__main__":
    if not os.path.exists("tmp/banks/pico"):
        os.makedirs("tmp/banks/pico")
    banks=SVBanks("octavox/banks/pico")
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
