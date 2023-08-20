from octavox.modules.banks import SVBanks

from octavox.modules.banks.pools import SVPool

from octavox.modules.cli import random_filename

from octavox.modules.model import SVSample, SVNoteTrig, SVFXTrig, SVTrigs

from octavox.modules.project import SVProject

import boto3, os, random, yaml

Modules=yaml.safe_load("""
- name: Sampler
  class: octavox.modules.sampler.SVSampler
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 32
    delay: 36
    delay_unit: 3 # tick
- name: Distortion
  class: rv.modules.distortion.Distortion
  defaults:
    power: 64
- name: Reverb
  class: rv.modules.reverb.Reverb
  defaults:
    wet: 4
""")

Links=yaml.safe_load("""
- - Sampler
  - Echo
- - Echo
  - Distortion
- - Distortion
  - Reverb
- - Reverb
  - Output
""")

def sample_bass(trigfn,
                samplefn,
                nbeats=16):
    def note_trig(trigs, target, sample, i):
        trigs.append(SVNoteTrig(mod=target,
                                sample=sample,
                                i=i))
    trigs=SVTrigs(nbeats=nbeats)
    sample=samplefn()
    for i in range(nbeats):
        if trigfn(i):
            note_trig(trigs, "Sampler", sample, i)
    return trigs.tracks

def spawn_patches(pool, npatches=32):
    """
    - https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
    """
    def trigfn(i):
        if 0==i%4:
            limit=0.6
        elif 0==i%3:
            limit=0.5
        elif 0==i%2:
            limit=0.3
        else:
            limit=0.1
        return random.random() < limit
    def spawn_samplefn(pool):
        def wrapped():
            key=random.choice(list(pool.keys()))
            return pool[key]
        return wrapped
    samplefn=spawn_samplefn(pool)
    return [sample_bass(trigfn=trigfn,
                        samplefn=samplefn)
            for i in range(npatches)]

def init_pool(banks, keys):
    pool=SVPool()
    for key in keys:
        bankname, stem = key.split("/")
        wavfile=banks[bankname].lookup(stem)
        sample=SVSample({"bank": bankname,
                         "file": wavfile})
        pool.add(sample)
    return pool

SampleKeys=yaml.safe_load("""
- baseck/03
- baseck/34
- baseck/37
- clipping/32
- dj-raitis-vinyl-cuts/47
- ib-magnetic-saturation/51
- legowelt/29
- nero-bellum/62
- pitch-black/27
- pitch-black/30
- pitch-black/32
- syntrx/09
- syntrx/19
- syntrx/24
- syntrx/26
- syntrx/53
- syntrx/60
""")

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        pool=init_pool(banks, SampleKeys)
        if not os.path.exists("tmp/demos"):
            os.makedirs("tmp/demos")
        patches=spawn_patches(pool)
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   banks=banks,
                                   bpm=120)
        destfilename="tmp/demos/%s.sunvox" % random_filename("samplebass")
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
