from octavox.modules.banks import SVBanks, SVPools, SVPool

from octavox.modules.cli import SVBankCli, render_patches

from octavox.modules.cli.parse import parse_line

from octavox.modules.model import SVSampleKey, SVNoteTrig, SVPatch

import json, os, random, yaml

Machines=yaml.safe_load("""
- name: KickSampler
  class: octavox.projects.slicebeats.model.Sequencer
  params:
    tag: kk
    styles:
    - fourfloor
    - electro
    - triplets
- name: SnareSampler
  class: octavox.projects.slicebeats.model.Sequencer
  params:
    tag: sn
    styles:
    - backbeat
    - skip
- name: HatSampler
  class: octavox.projects.slicebeats.model.Sequencer
  params:
    tag: ht
    styles:
    - offbeats
    - closed
- name: Echo/wet
  class: octavox.projects.slicebeats.model.Modulator
  params:
    style: sample_hold
    range: [0, 1]
    increment: 0.25
    step: 4
    live: 0.66666
    multiplier: 32768
- name: Echo/feedback
  class: octavox.projects.slicebeats.model.Modulator
  params:
    style: sample_hold
    range: [0, 1]
    increment: 0.25
    step: 4
    live: 1.0
    multiplier: 32768
""")


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

    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    @render_patches(prefix="mutate")
    def do_mutate_patch(self, i):
        root=self.patches[i % len(self.patches)]
        patches=[root]
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches-1):
            patch=root.clone()
            for machine in patch["machines"]:
                if "slices" in machine:
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
                        if trig.samplekey:
                            print ("%i\t%s" % (i, trig.samplekey.full_key))

    @parse_line()
    def do_list_fixes(self):
        for samplekey in self.fixes.values():
            print ("- %s" % samplekey)

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
                      poolname="default-curated",
                      params=Params,
                      modules=Modules,
                      links=Links,
                      banks=banks,
                      pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
