from octavox.core.banks import SVBanks

from octavox.core.cli import SVBankCli, render_patches

from octavox.core.cli.parse import parse_line

from octavox.core.model import SVNoteTrig, SVPatch

from octavox.core.pools import SVSample, SVPools, SVPool

import boto3, os, random, sys, yaml

Modules=yaml.safe_load(open("octavox/projects/samplebeats/modules.yaml").read())

Links=yaml.safe_load(open("octavox/projects/samplebeats/links.yaml").read())

EuclidSequencers=yaml.safe_load(open("octavox/projects/samplebeats/sequencers/euclid.yaml").read())

VitlingSequencers=yaml.safe_load(open("octavox/projects/samplebeats/sequencers/vitling.yaml").read())

Modulators=yaml.safe_load(open("octavox/projects/samplebeats/modulators.yaml").read())

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

def randomise_sequencers(sequencers):
    def group_sequencers(seqs):
            groups={}
            for seq in seqs:
                groups.setdefault(seq["name"], [])
                groups[seq["name"]].append(seq)
            return groups
    return [random.choice(seqs)
            for seqs in group_sequencers(sequencers).values()]
    
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
        sequencers=randomise_sequencers(EuclidSequencers+VitlingSequencers)
        for seq in sequencers:
            print ("INFO: %s=%s" % (seq["name"], seq["class"].split(".")[-1]))
        SVCli(s3=s3,                                  
              sequencers=sequencers,
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
