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
                pitchfn,
                nbeats=16):
    def note_trig(trigs, target, sample, pitch, i):
        sample["pitch"]=pitch
        trigs.append(SVNoteTrig(mod=target,
                                sample=sample,
                                i=i))
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if trigfn(i):
            note_trig(trigs, "Sampler", samplefn(), pitchfn(), i)
    return trigs.tracks

def spawn_patches(pool, npatches=16):
    def trigfn(i):
        return random.random() < 0.5
    def spawn_samplefn(pool):
        base=random.choice(pool)
        def wrapped():
            sample=base.clone()
            sample["mod"]="granular"
            sample["ctrl"]={"offset": random.random([50, 100, 200, 400]),
                            "sz": random.choice([25, 50, 100, 200]),
                            "n": random.choice([5, 10, 20]),
                            "fadeout": 50}
            return sample
        return wrapped            
    def pitchfn():
        q=random.random()
        if q < 0.7:
            return 0
        elif q < 0.8:
            return -2
        elif q < 0.9:
            return 7
        else:
            return 12
    return [grain_pad(trigfn=trigfn,
                      samplefn=spawn_samplefn(pool),
                      pitchfn=pitchfn)
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
        for sample in pool:
            print (sample)
        """
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
        """
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
