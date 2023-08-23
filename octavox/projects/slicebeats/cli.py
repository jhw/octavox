from octavox import load_yaml

from octavox.modules.banks import SVBanks

from octavox.modules.banks.pools import SVPools, SVPool

from octavox.modules.cli import SVBankCli, render_patches, assert_project

from octavox.modules.cli.parse import parse_line

from octavox.modules.model import SVSample, SVNoteTrig, SVPatch

from octavox.projects.slicebeats.model import Pattern

import boto3, json, os, random, re

Machines=load_yaml("projects/slicebeats/machines.yaml")

class SlicebeatsCli(SVBankCli):

    intro="Welcome to Slicebeats :)"

    def __init__(self,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        self.fixes=SVPool()
        
    @parse_line()
    @render_patches(prefix="random")
    def do_randomise_patches(self, machines=Machines):
        patches=[]
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches):
            patch=SVPatch.randomise(machines=machines,
                                    pool=self.pools[self.poolname],
                                    fixes=self.fixes,
                                    temperature=self.env["temperature"],
                                    density=self.env["density"])
            patches.append(patch)
        return patches


    """
    - could add style or density mutation
    """
    
    @parse_line(config=[{"name": "i",
                         "type": "int"},
                        {"name": "level",
                         "type": "enum",
                         "options": "lo|hi".split("|")}])
    @assert_project
    @render_patches(prefix="mutate")
    def do_mutate_patch(self, i, level, machines=Machines):
        root=self.patches[i % len(self.patches)]
        patches=[root]
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches-1):
            patch=root.clone()
            for machine in patch["machines"]:
                if "slices" in machine:
                    if level=="hi":
                        machine["pattern"]=Pattern.randomise(self.env["temperature"])
                    for slice in machine["slices"]:
                        if random.random() < self.env["dseed"]:
                            slice["seed"]=int(1e8*random.random())
                else:
                    if random.random() < self.env["dseed"]:
                        machine["seed"]=int(1e8*random.random())
            patches.append(patch)
        return patches

    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    def do_show_samples(self, i):
        patch=self.patches[i % len(self.patches)]
        rendered=patch.render(nbeats=self.env["nbeats"])
        trigs={K:{trig.i:trig for trig in V}
               for K, V in rendered.items()}
        for i in range(self.env["nbeats"]):
            for tag in trigs:
                if i in trigs[tag]:
                    trig=trigs[tag][i]
                    if isinstance(trig, SVNoteTrig):
                        if trig.sample:
                            print ("%i\t%s" % (i, trig.sample))

    @parse_line()
    def do_list_fixes(self):
        for sample in self.fixes.values():
            print ("- %s" % sample)

    @parse_line(config=[{"name": "tag",
                         "type": "str"},
                        {"name": "bankstem",
                         "type": "str"},
                        {"name": "wavstem",
                         "type": "str"}])
    def do_fix_sample(self, tag, bankstem, wavstem):
        bankname=self.banks.lookup(bankstem)
        bank=self.banks[bankname]
        wavfile=bank.lookup(wavstem)
        sample=SVSample({"tags": [tag],
                               "bank": bankname,
                               "file": wavfile})
        self.fixes.add(sample)

    @parse_line()
    def do_clean_fixes(self):
        self.fixes=SVPool()

def init_pools(banks, terms, limit=12):
    pools, globalz = SVPools(), SVPools()
    for bankname, bank in banks.items():
        for attr, pool in [("default", bank.default_pool),
                           ("curated", bank.curate_pool(terms))]:
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
        modules, links, params, curated = [load_yaml("projects/slicebeats/%s.yaml" % key) for key in "modules|links|params|curated".split("|")]
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        pools=init_pools(banks, terms=curated)
        poolname=random.choice(list(pools.keys()))
        print ("INFO: pool=%s" % poolname)
        SlicebeatsCli(s3=s3,
                      projectname="slicebeats",
                      bucketname=bucketname,
                      poolname=poolname,
                      params=params,
                      modules=modules,
                      links=links,
                      banks=banks,
                      pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
