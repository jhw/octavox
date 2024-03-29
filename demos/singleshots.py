from octavox.core.banks import SVBanks

from octavox.core.model import SVTrigs, SVNoteTrig

from octavox.core.pools import SVSample

from octavox.core.project import SVProject

import boto3, os, yaml

Modules=yaml.safe_load("""
- name: Sampler
  class: octavox.core.sampler.SVSampler
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
        sample=SVSample({"bank": bankname,
                               "file": wavfile})
        note=SVNoteTrig(mod="Sampler",
                        sample=sample,
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
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)        
        if not os.path.exists("tmp/singleshots"):
            os.makedirs("tmp/singleshots")
        for bankname, bank in banks.items():
            print ("INFO: generating %s" % bankname)
            destfilename="tmp/singleshots/%s.sunvox" % bankname
            generate(bankname=bankname,
                     bank=bank,
                     banks=banks,
                     destfilename=destfilename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
