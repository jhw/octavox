from octavox.modules.banks import SVSampleKey, SVBanks, SVPools, SVPool

from octavox.modules.cli import SVBankCli, parse_line, render_patches

from octavox.modules.project import SVNoteTrig

from octavox.projects.slicebeats.model import Patch

import json, os, random, yaml

class SlicebeatsCli(SVBankCli):

    intro="Welcome to Slicebeats :)"

    def __init__(self,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        self.fixes=SVPool()

    @parse_line(config=[{"name": "stub",
                         "type": "str"}])
    def do_load_project(self, stub):
        matches=[filename for filename in os.listdir(self.outdir+"/json")
                 if stub in filename]
        if matches==[]:
            print ("WARNING: no matches")
        elif len(matches)==1:
            filename=matches.pop()
            print ("INFO: %s" % filename)
            abspath="%s/json/%s" % (self.outdir, filename)
            patches=json.loads(open(abspath).read())
            self.patches=[Patch(**patch)
                          for patch in patches]
        else:
            print ("WARNING: multiple matches")
        
    @parse_line()
    @render_patches(prefix="random")
    def do_randomise_patches(self):
        patches=[]
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches):
            patch=Patch.randomise(pool=self.pools[self.poolname],
                                  fixes=self.fixes,
                                  temperature=self.env["temperature"],
                                  density=self.env["density"])
            patches.append(patch)
        return patches

    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    @render_patches(prefix="mutate")
    def do_mutate_patch(self, i):
        root=self.patches[i % len(self.patches)]
        patches=[root]
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches-1):
            patch=root.clone()
            for seq in patch["sequencers"]:
                for slice in seq["slices"]:
                    if random.random() < self.env["dseed"]:
                        slice["seed"]=int(1e8*random.random())
            for lfo in patch["lfos"]:
                if random.random() < self.env["dseed"]:
                    lfo["seed"]=int(1e8*random.random())
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
                        if trig.samplekey:
                            print ("%i\t%s" % (i, trig.samplekey.full_key))

    @parse_line()
    def do_list_fixes(self):
        for samplekey in self.fixes.values():
            print ("- %s" % samplekey)

    @parse_line(config=[{"name": "tag",
                         "type": "str"},
                        {"name": "bankstub",
                         "type": "str"},
                        {"name": "wavstub",
                         "type": "str"}])
    def do_fix_sample(self, tag, bankstub, wavstub):
        bankname=self.banks.lookup(bankstub)
        bank=self.banks[bankname]
        wavfile=bank.lookup(wavstub)
        samplekey=SVSampleKey({"tags": [tag],
                               "bank": bankname,
                               "file": wavfile})
        self.fixes.add(samplekey)

    @parse_line()
    def do_clean_fixes(self):
        self.fixes=SVPool()
                
Params=yaml.safe_load("""
temperature: 1.0
density: 0.75
dseed: 1.0
dstyle: 0.66666
nbeats: 16
blocksize: 4
nblocks: 8
bpm: 120
""")

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
    delay: 192
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
- - KickSampler
  - Echo
- - SnareSampler
  - Echo
- - HatSampler
  - Echo
- - Echo
  - Distortion
- - Distortion
  - Reverb
- - Reverb
  - Output
""")

if __name__=="__main__":
    try:
        def load_yaml(filename, home="octavox/projects/slicebeats"):
            return yaml.safe_load(open("%s/%s" % (home, filename)).read())
        banks=SVBanks("octavox/banks/pico")
        pools=SVPools({poolname:pool
                       for poolname, pool in banks.spawn_pools().items()
                       if len(pool) > 24})
        SlicebeatsCli(projectname="slicebeats",
                      poolname="global-curated",
                      params=Params,
                      modules=Modules,
                      links=Links,
                      banks=banks,
                      pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
