from octavox.core.banks import SVBanks

from octavox.core.cli import SVBankCli, render_patches, assert_project

from octavox.core.cli.parse import parse_line

from octavox.core.model import SVPatch

from octavox.core.pools import SVPools

import boto3, itertools, os, random, sys, yaml

Modules, Links, Sequencers, Modulators = [yaml.safe_load(open("octavox/projects/samplebeats/%s.yaml" % attr).read())
                                          for attr in "modules|links|sequencers|modulators".split("|")]

Env=yaml.safe_load("""
nbeats: 16
npatches: 32
density: 0.66666
temperature: 0.66666
bpm: 120
nbreaks: 0
""")

Curated=yaml.safe_load("""
ht: (hat)|(ht)|(perc)|(ussion)|(prc)|(glitch)
kk: (kick)|(kik)|(kk)|(bd)|(bass)
sn: (snare)|(sn)|(sd)|(clap)|(clp)|(cp)|(hc)|(rim)|(plip)|(rs)
""")

MinPoolSize=12

class SequencerMap(dict):

    def __init__(self, sequencers):
        groups={}
        for seq in sequencers:
            groups.setdefault(seq["name"], [])
            groups[seq["name"]].append(seq)
        dict.__init__(self, groups)

    def randomise(self):
        return [random.choice(self[key])
                for key in self]
        
class SVCli(SVBankCli):

    intro="Welcome to Samplebeats :)"

    def __init__(self,
                 sequencers,
                 modulators,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        self.sequencers=SequencerMap(sequencers)
        self.modulators=modulators

    @parse_line()
    @render_patches(prefix="random")
    def do_randomise_patches(self):
        patches=[]
        for i in range(self.env["npatches"]):
            machines=self.sequencers.randomise()+self.modulators
            patch=SVPatch.initialise(machines=machines,
                                     pool=self.pools[self.poolname])            
            patches.append(patch)
        return patches

    def _mutate_patch(self, i, attrs):
        root=self.patches[i % len(self.patches)]
        patches=[root]
        for i in range(self.env["npatches"]-1):
            patch=root.clone()
            for machine in patch["machines"]:
                for attr in attrs:
                    if attr in machine["seeds"]:
                        machine["seeds"][attr]=int(1e8*random.random())
            patches.append(patch)
        return patches
    
    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    @assert_project
    @render_patches(prefix="mutation")
    def do_mutate_patch_1(self, i):
        return self._mutate_patch(i, attrs="level|volume".split("|"))
    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    @assert_project
    @render_patches(prefix="mutation")
    def do_mutate_patch_2(self, i):
        return self._mutate_patch(i, attrs="level|volume|trig|pattern".split("|"))
    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    @assert_project
    @render_patches(prefix="mutation")
    def do_mutate_patch_3(self, i):
        return self._mutate_patch(i, attrs="level|volume|trig|pattern|sample".split("|"))                

    @parse_line(config=[{"name": "I",
                         "type": "array"}])
    @assert_project
    @render_patches(prefix="chain")
    def do_chain_patches(self, I):
        def permutations_of(s):
            n, perms = len(s), []            
            for i in range(1, n):
                for perm in itertools.permutations(s, i):
                    perms.append(set(perm))                    
            return perms
        roots=[self.patches[i % len(self.patches)]
               for i in I]
        patches=[]
        patches+=roots
        allmutes=permutations_of(["%sSampler" % attr.capitalize()
                               for attr in "kick|snare|hat".split("|")])
        for root in roots:
            for mutes in allmutes:
                patch=SVPatch(machines=root["machines"],
                              mutes=mutes)
                """
                patch=root.clone()
                patch["mutes"]=mutes
                """
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
              sequencers=Sequencers,
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
