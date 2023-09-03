from octavox.core.banks import SVBanks

from octavox.core.cli import SVBankCli, render_patches

from octavox.core.cli.parse import parse_line

from octavox.core.model import SVNoteTrig, SVPatch

from octavox.core.pools import SVSample, SVPools, SVPool

import boto3, os, random, sys, yaml

MinPoolSize=12

class SVCli(SVBankCli):

    intro="Welcome to Samplebeats :)"

    def __init__(self,
                 sequencers,
                 modulators,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        self.sequencers=sequencers
        self.modulators=modulators

    @parse_line()
    @render_patches(prefix="random")
    def do_randomise_patches(self):
        machines=self.sequencers+self.modulators
        patches=[]        
        for i in range(self.env["npatches"]):
            patch=SVPatch.randomise(machines=machines,
                                    pool=self.pools[self.poolname])
            patches.append(patch)
        return patches

def init_pools(banks, terms, limit=MinPoolSize):
    pools, globalz = SVPools(), SVPools()
    for bankname, bank in banks.items():
        for attr, pool in [("default", bank.default_pool),
                           ("curated", bank.filter_pool(terms))]:
            if len(pool) > limit:
                pools["%s-%s" % (bankname, attr)]=pool
    for attr in "default|curated".split("|"):        
        globalz["global-%s" % attr]=pools.flatten("\\-%s$" % attr)
    pools.update(globalz)
    return pools

Modules=yaml.safe_load("""
- name: KickSampler
  class: octavox.core.sampler.SVSampler
- name: SnareSampler
  class: octavox.core.sampler.SVSampler
- name: HatSampler
  class: octavox.core.sampler.SVSampler
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 256
    delay: 36
    delay_unit: 3 # tick
- name: Reverb
  class: rv.modules.reverb.Reverb
  defaults:
    wet: 4
""")

Links=yaml.safe_load("""
- - KickSampler
  - Echo
- - SnareSampler
  - Echo
- - HatSampler
  - Echo
- - Echo
  - Reverb
- - Reverb
  - Output
""")

EuclidSequencers=yaml.safe_load("""
- class: octavox.machines.sequencers.beats.euclid.EuclidSequencer
  name: KickSampler
  params:
    density: 0.66666
    modulation:
      sample:
        reversion: 0.5
        step: 4
        threshold: 0.5
      pattern:
        reversion: 0.5
        step: 4
        threshold: 0.5
    nsamples: 4
    tag: kk
- class: octavox.machines.sequencers.beats.euclid.EuclidSequencer
  name: SnareSampler
  params:
    density: 0.33333
    modulation:
      sample:
        reversion: 0.5
        step: 4
        threshold: 0.5
      pattern:
        reversion: 0.5
        step: 4
        threshold: 0.5
    nsamples: 4
    tag: sn
- class: octavox.machines.sequencers.beats.euclid.EuclidSequencer
  name: HatSampler
  params:
    density: 0.9
    modulation:
      sample:
        reversion: 0.5
        step: 4
        threshold: 0.5
      pattern:
        reversion: 0.5
        step: 4
        threshold: 0.5
    nsamples: 4
    tag: ht
""")

VitlingSequencers=yaml.safe_load("""
- class: octavox.machines.sequencers.beats.vitling.VitlingSequencer
  name: KickSampler
  params:
    density: 1.0
    modulation:
      sample:
        reversion: 0.5
        step: 4
        threshold: 0.8
      pattern:
        reversion: 0.5
        step: 4
        threshold: 0.8
    nsamples: 4
    patterns:
    - fourfloor
    - electro
    - triplets
    tag: kk
- class: octavox.machines.sequencers.beats.vitling.VitlingSequencer
  name: SnareSampler
  params:
    density: 1.0
    modulation:
      sample:
        reversion: 0.5
        step: 4
        threshold: 0.8
      pattern:
        reversion: 0.5
        step: 4
        threshold: 0.8
    nsamples: 4
    patterns:
    - backbeat
    - skip
    tag: sn
- class: octavox.machines.sequencers.beats.vitling.VitlingSequencer
  name: HatSampler
  params:
    density: 1.0
    modulation:
      sample:
        reversion: 0.5
        step: 4
        threshold: 0.8
      pattern:
        reversion: 0.5
        step: 4
        threshold: 0.8
    nsamples: 4
    patterns:
    - offbeats
    - closed
    tag: ht
""")

Modulators=yaml.safe_load("""
- class: octavox.machines.modulators.sample_hold.SampleHoldModulator
  name: Echo/wet
  params:
    increment: 0.25
    maxvalue: '8000'
    minvalue: '0000'
    range:
    - 0
    - 1
    step: 4
- class: octavox.machines.modulators.sample_hold.SampleHoldModulator
  name: Echo/feedback
  params:
    increment: 0.25
    maxvalue: '8000'
    minvalue: '0000'
    range:
    - 0
    - 1
    step: 4
""")

Env=yaml.safe_load("""
nbeats: 16
npatches: 32
bpm: 120
""")

Curated=yaml.safe_load("""
ht: (hat)|(ht)|(perc)|(ussion)|(prc)|(glitch)
kk: (kick)|(kik)|(kk)|(bd)|(bass)
sn: (snare)|(sn)|(sd)|(clap)|(clp)|(cp)|(hc)|(rim)|(plip)|(rs)
""")

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        pools=init_pools(banks, terms=Curated)
        poolname=random.choice(list(pools.keys()))
        print ("INFO: pool=%s" % poolname)
        SVCli(s3=s3,
              sequencers=EuclidSequencers,
              modulators=Modulators,
              projectname="samplebeats",
              bucketname=bucketname,
              poolname=poolname,
              env=Env,
              modules=Modules,
              links=Links,
              banks=banks,
              pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
