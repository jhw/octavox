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
                nticks):
    def note_trig(trigs, target, sample, vel, i):
        trigs.append(SVNoteTrig(mod=target,
                                sample=sample,
                                vel=vel,
                                i=i))
    trigs=SVTrigs(nbeats=nticks)
    for i in range(nticks):
        if trigfn(i):
            note_trig(trigs, "Sampler", samplefn(), velfn(), i)
    return trigs.tracks

def spawn_patches(pool,
                  nticks,
                  nbeats,
                  npatches):
    def trigfn(i):
        if 0 == i % nticks:
            return random.random() < 0.75
        elif nticks/2 == i % nticks:
            return random.random() < 0.2
        else:
            return random.random() < 0.05            
    def velfn():
        return random.random()*0.5+0.5
    def reverse(sample):
        rev=sample.clone()
        rev["mod"]="reverse"
        rev["ctrl"]={}
        return rev
    def spawn_samplefn(pool):            
        samples=[]
        for tag in "oh|ch".split("|"):
            sample=random.choice(pool)
            rev=reverse(sample)
            samples+=[sample, sample, rev]
        def wrapped():
            return random.choice(samples)
        return wrapped            
    return [sample_hats(trigfn=trigfn,
                        velfn=velfn,
                        samplefn=spawn_samplefn(pool),
                        nticks=nbeats*nticks)
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
        npatches, nbeats, nticks, bpm = 16, 16, 4, 120
        patches=spawn_patches(pool,
                              npatches=npatches,
                              nbeats=nbeats,
                              nticks=nticks)
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   banks=banks,
                                   bpm=bpm*nticks)
        if not os.path.exists("tmp/samplehats"):
            os.makedirs("tmp/samplehats")
        ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/samplehats/%s.sunvox" % ts
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
