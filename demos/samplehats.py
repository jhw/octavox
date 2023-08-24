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

def sample_hats(trigfn,
                samplefn,
                velfn,
                nbeats=16):
    def note_trig(trigs, target, sample, vel, i):
        trigs.append(SVNoteTrig(mod=target,
                                sample=sample,
                                vel=vel,
                                i=i))
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if trigfn(i):
            note_trig(trigs, "Sampler", samplefn(), velfn(), i)
    return trigs.tracks

def spawn_patches(pool, npatches=16):
    def trigfn(i):
        return random.random() < 0.75
    def velfn():
        return random.random()*0.5+0.5
    def spawn_samplefn(pool):
        samples=[]
        for i in range(2):
            base=random.choice(pool)
            rev=base.clone()
            rev["mod"]="reverse"
            rev["ctrl"]={}
            rep=base.clone()
            rep["mod"]="repeat"
            rep["ctrl"]={"n": 2,
                         "sz": 62.5}
            samples+=[base, base, base, rev, rep]
        def wrapped():
            return random.choice(samples)
        return wrapped            
    return [sample_hats(trigfn=trigfn,
                        velfn=velfn,
                        samplefn=spawn_samplefn(pool))
            for i in range(npatches)]

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        # pool=banks.filter_pool({"ht": "(open)|(closed)|(hat)|(ht)|(oh)|( ch)|(perc)|(ussion)|(prc)"})
        pool=banks["pico-richard-devine"].default_pool
        patches=spawn_patches(pool)
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   banks=banks,
                                   bpm=120)
        if not os.path.exists("tmp/samplehats"):
            os.makedirs("tmp/samplehats")
        ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/samplehats/%s.sunvox" % ts
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
