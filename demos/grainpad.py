from octavox.modules.banks import SVBanks

from octavox.modules.model import SVNoteTrig, SVFXTrig, SVTrigs

from octavox.modules.pools import SVSample, SVPool

from octavox.modules.project import SVProject

from datetime import datetime

import boto3, os, random, yaml

Modules=yaml.safe_load("""
- name: Sampler
  class: octavox.modules.sampler.SVSampler
- name: Filter
  class: rv.modules.filter.Filter
  defaults:
    type: 0
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 32
    delay: 36
    delay_unit: 3 # tick
- name: Reverb
  class: rv.modules.reverb.Reverb
  defaults:
    wet: 4
""")

Links=yaml.safe_load("""
- - Sampler
  - Filter
- - Filter
  - Echo
- - Echo
  - Reverb
- - Reverb
  - Output
""")

def grain_pad(trigfn,
                samplefn,
                nbeats=16):
    def note_trig(trigs, target, sample, i):
        trigs.append(SVNoteTrig(mod=target,
                                sample=sample,
                                i=i))
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if trigfn(i):
            note_trig(trigs, "Sampler", samplefn(), i)
    return trigs.tracks

def spawn_patches(pool, npatches=16):
    def trigfn(i):
        return random.random() < 0.25
    def spawn_samplefn(pool):
        base=random.choice(pool)
        def wrapped():
            sample=base.clone()
            sample["mod"]="granular"
            sample["ctrl"]={"offset": random.choice([50, 100, 200]),
                            "sz": random.choice([50, 100]),
                            "n": random.choice([5, 10]),
                            "padding": 25,
                            "fadeout": 100}
            return sample
        return wrapped            
    return [grain_pad(trigfn=trigfn,
                      samplefn=spawn_samplefn(pool))
            for i in range(npatches)]

def init_pool(banks, terms):
    pool=SVPool()
    for bankname, bank in banks.items():
        pool+=bank.curate_pool(terms)
    return pool
                
if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        pool=banks.curate_pool({"pads": "(pad)|(chord)|(drone)"})
        patches=spawn_patches(pool)
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   banks=banks,
                                   bpm=120)
        if not os.path.exists("tmp/grainpad"):
            os.makedirs("tmp/grainpad")
        ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/grainpad/%s.sunvox" % ts
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
