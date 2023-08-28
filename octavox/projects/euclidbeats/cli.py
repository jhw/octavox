from octavox import load_yaml

from octavox.modules.banks import SVBanks

from octavox.modules.cli import SVBankCli, render_patches

from octavox.modules.cli.parse import parse_line

from octavox.modules.model import SVNoteTrig, SVPatch

from octavox.modules.pools import SVSample, SVPools, SVPool

import boto3, json, os, random, re, yaml

Machines=load_yaml("projects/euclidbeats/machines.yaml")

MinPoolSize=12

class SVCli(SVBankCli):

    intro="Welcome to Euclidbeats :)"

    def __init__(self,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        
    @parse_line()
    @render_patches(prefix="random")
    def do_randomise_patches(self, machines=Machines):
        patches=[]
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches):
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

Curated=yaml.safe_load("""
ht: (hat)|(ht)|(perc)|(ussion)|(prc)|(glitch)
kk: (kick)|(kik)|(kk)|(bd)|(bass)
sn: (snare)|(sn)|(sd)|(clap)|(clp)|(cp)|(hc)|(rim)|(plip)|(rs)
""")

Params=yaml.safe_load("""
nbeats: 16
blocksize: 4
nblocks: 8
bpm: 120
""")

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        modules, links = [load_yaml("projects/euclidbeats/%s.yaml" % key) for key in "modules|links".split("|")]
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
              modules=modules,
              links=links,
              banks=banks,
              pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
