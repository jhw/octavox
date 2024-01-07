from octavox.core.banks import SVBanks

from octavox.core.cli import SVBankCli, render_patches, assert_project

from octavox.core.cli.parse import parse_line

from octavox.core.model import SVPatch

from octavox.core.pools import SVPool, SVPools, SVSample

import boto3, itertools, json, os, random, sys, yaml

(Modules,
 Links,
 Sequencers,
 Modulators,
 Banned) = [yaml.safe_load(open("octavox/projects/samplebeats/%s.yaml" % attr).read())
            for attr in "modules|links|sequencers|modulators|banned".split("|")]

Env=yaml.safe_load("""
nticks: 16
npatches: 32
density: 0.66666
temperature: 0.66666
bpm: 120
tpb: 4 # ticks per beat
nbreaks: 0
""")

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

    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    @assert_project
    def do_dump_patch(self, i):
        class Column(list):
            def __init__(self, items=[]):
                list.__init__(self, items)
            @property
            def width(self):
                return max([len(v) for v in self])
        class Track(Column):
            def __init__(self, n, defaultval=".."):
                Column.__init__(self, [defaultval for i in range(n)])
        class Index(Column):
            def __init__(self, n):
                Column.__init__(self, [str(i) for i in range(n)])
        class Grid(dict):
            def __init__(self, n):
                dict.__init__(self)
                self["Index"]=Index(n)
            @property
            def widths(self):
                widths={}
                for k, v in self.items():
                    widths[k]=max([len(k), v.width])
                return widths
            def format_cell(self, v, n):
                return v+" ".join(['' for i in range(1+n-len(v))]) if len(v) < n else v[:n]
            def render(self, keys, delimiter="  "):
                widths=self.widths
                rows=[]
                titles=[self.format_cell(key, widths[key])
                        for key in keys]
                rows.append(titles)
                for i in range(len(self["Index"])):
                    row=[self.format_cell(self[key][i], widths[key])
                         for key in keys]
                    rows.append(row)
                return "\n".join([delimiter.join(row)
                                  for row in rows])
        patch=SVPatch(**self.patches[i % len(self.patches)])
        rendered=patch.render(nticks=self.env["nticks"],
                              density=self.env["density"],
                              temperature=self.env["temperature"])
        grid=Grid(self.env["nticks"])
        for key, trigs in rendered.items():
            if "Sampler" in key:
                grid.setdefault(key, Track(self.env["nticks"]))
                for trig in trigs:
                    grid[key][trig.i]="%s/%s" % (trig.sample["bank"],
                                                 trig.sample["file"])
        print (grid.render(keys=["Index",
                                 "KickSampler",
                                 "SnareSampler",
                                 "HatSampler"]))
        
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
        def unique_permutations(strings):
            perms=[]
            for r in range(1, len(strings)):
                for _perm in itertools.permutations(strings, r):
                    perm="/".join(sorted(list(_perm)))
                    if perm not in perms:
                        perms.append(perm)
            return [perm.split("/")
                    for perm in perms]
        roots=[self.patches[i % len(self.patches)]
               for i in I]
        allmutes=unique_permutations(["%sSampler" % attr.capitalize()
                                      for attr in "kick|snare|hat".split("|")])
        patches=[]
        for root in roots:
            patches.append(root)
            for mutes in allmutes:
                patch=SVPatch(machines=root["machines"],
                              mutes=mutes)
                patches.append(patch)
        return patches
                
def init_pools(dirname="octavox/projects/samplebeats/pools"):
    pools=SVPools()
    for filename in os.listdir(dirname):
        poolname=filename.split(".")[0]
        pool=SVPool()        
        for sample in yaml.safe_load(open("%s/%s" % (dirname, filename)).read()):
            pool.add(SVSample(sample))
        pools[poolname]=pool
    return pools
        
if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        pools=init_pools()
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
