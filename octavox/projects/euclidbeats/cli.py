from octavox import load_yaml

from octavox.modules.banks import SVBanks

from octavox.modules.cli import SVBankCli, render_patches

from octavox.modules.cli.parse import parse_line

from octavox.modules.model import SVNoteTrig, SVPatch

from octavox.modules.pools import SVSample, SVPools, SVPool

import boto3, os, random, yaml

MachinesSrc="projects/euclidbeats/machines.yaml"

MinPoolSize=12

class SVCli(SVBankCli):

    intro="Welcome to Euclidbeats :)"

    def __init__(self,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        
    @parse_line()
    @render_patches(prefix="random")
    def do_randomise_patches(self, src=MachinesSrc):
        machines, patches = load_yaml(src), []
        for i in range(self.env["npatches"]):
            patch=SVPatch.randomise(machines=machines,
                                    pool=self.pools[self.poolname],
                                    density=self.env["density"])
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
  class: octavox.modules.sampler.SVSampler
- name: SnareSampler
  class: octavox.modules.sampler.SVSampler
- name: HatSampler
  class: octavox.modules.sampler.SVSampler
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

Params=yaml.safe_load("""
density: 0.5
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
              projectname="euclidbeats",
              bucketname=bucketname,
              poolname=poolname,
              params=Params,
              modules=Modules,
              links=Links,
              banks=banks,
              pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
