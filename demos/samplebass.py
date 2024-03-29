from octavox.core.banks import SVBanks

from octavox.core.model import SVNoteTrig, SVFXTrig, SVTrigs

from octavox.core.pools import SVSample, SVPool

from octavox.core.project import SVProject

from datetime import datetime

import boto3, os, random, yaml

"""
- Filter included for manual manipulation
"""

Modules=yaml.safe_load("""
- name: Sampler
  class: octavox.core.sampler.SVSampler
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

def sample_bass(trigfn,
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

"""
- only using 16 patches as samplebass can rack up a lot of different samples
- 3 notes x 4 lengths = 12 possible options
- 16 steps and 50% density means 8 notes avg could all be different samples
- 32 patches x 8 samples = 256 slots
- (not quite that bad as some patches will share samples)
- but you can see where the problem comes from 
- because sampler treats each pitch and each length as a separate sample
- does sunvox really have no sample cutoff parameter?
"""

def spawn_patches(pool, npatches=16):
    def trigfn(i):
        return random.random() < 0.5
    def spawn_samplefn(pool):
        base=random.choice(pool)
        def wrapped():
            sample=base.clone()
            sample["mod"]="cutoff?cutoff=%i&fadeout=50" % random.choice([125, 250, 500, 1000])
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
    return [sample_bass(trigfn=trigfn,
                        samplefn=spawn_samplefn(pool),
                        pitchfn=pitchfn)
            for i in range(npatches)]

"""
- hand curated by dev/init_samplebass.py
"""

BassSamples=yaml.safe_load("""
- pico-baseck/03 BRA04.wav
- pico-baseck/34 syncussion.wav
- pico-baseck/37 syncussion.wav
- pico-clipping/32 ShooterMelodyBass.wav
- pico-dj-raitis-vinyl-cuts/47 CUT.wav
- pico-ib-magnetic-saturation/51 SYN.wav
- pico-legowelt/29 ERIKAAntiloophuppelSynth.wav
- pico-nero-bellum/62 String Guitar Drone Drone Source.wav
- pico-pitch-black/27 Ernie ball bass guitar note sustain lead.wav
- pico-pitch-black/30 coast lin fm lead.wav
- pico-pitch-black/32 buchla bass shot lead.wav
- pico-syntrx/09 swpbas1.wav
- pico-syntrx/19 bass1.wav
- pico-syntrx/24 fmbs1.wav
- pico-syntrx/26 bass2.wav
- pico-syntrx/53 kik2.wav
- pico-syntrx/60 snare3.wav
""")

def init_pool(terms):
    pool=SVPool()
    for term in terms:
        bankname, filename = term.split("/")
        sample=SVSample({"bank": bankname,
                         "file": filename})
        pool.append(sample)
    return pool

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        pool=init_pool(terms=BassSamples)
        patches=spawn_patches(pool)
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   banks=banks,
                                   bpm=120)
        if not os.path.exists("tmp/samplebass"):
            os.makedirs("tmp/samplebass")
        ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/samplebass/%s.sunvox" % ts
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
