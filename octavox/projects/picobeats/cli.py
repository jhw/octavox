from octavox.modules.banks import SVSampleKey, SVBanks, SVPool

from octavox.modules.cli import SVBankCli, parse_line

from octavox.modules.project import Output

from octavox.projects import random_filename

from octavox.projects.picobeats.model import Patch, Patches, Instruments

import json, os, random, yaml

def flatten(lists):
    values=[]
    for l in lists:
        values+=l
    return values

class Fixes(dict):

    @classmethod
    def create(self, instruments=Instruments):
        return Fixes({key:{} for key in flatten(instruments.values())})
    
    def __init__(self, item={}):
        dict.__init__(self, item)

    def add(self, key, samplekey):
        self[key][str(samplekey)]=samplekey

class PicobeatsCli(SVBankCli):

    intro="Welcome to Picobeats :)"

    def __init__(self,
                 instruments=Instruments,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        self.fixes=Fixes.create()

    @parse_line(config=[{"name": "frag",
                         "type": "str"}])
    def do_load_project(self, frag):
        matches=[filename for filename in os.listdir(self.outdir+"/json")
                 if frag in filename]
        if matches==[]:
            print ("WARNING: no matches")
        elif len(matches)==1:
            filename=matches.pop()
            print ("INFO: %s" % filename)
            abspath="%s/%s" % (self.outdir+"/json", filename)
            patches=json.loads(open(abspath).read())
            self.patches=Patches([Patch(**patch)
                                  for patch in patches])
        else:
            print ("WARNING: multiple matches")
        
    def render_patches(prefix):
        def decorator(fn):
            def wrapped(self, *args, **kwargs):
                self.filename=random_filename(prefix)
                print ("INFO: %s" % self.filename)
                self.patches=fn(self, *args, **kwargs)
                jsonfilename="%s/json/%s.json" % (self.outdir,
                                                  self.filename)
                self.patches.render_json(filename=jsonfilename)
                svfilename="%s/sunvox/%s.sunvox" % (self.outdir,
                                                    self.filename)                
                self.patches.render_sunvox(banks=self.banks,
                                           nbeats=self.env["nbeats"],
                                           density=self.env["density"],
                                           filename=svfilename)
            return wrapped
        return decorator

    @parse_line()
    @render_patches(prefix="random")
    def do_randomise_patches(self):
        patches=Patches()
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches):
            patch=Patch.randomise(pool=self.pools[self.poolname],
                                  fixes=self.fixes,
                                  temperature=self.env["temperature"])
            patches.append(patch)
        return patches

    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    @render_patches(prefix="mutate")
    def do_mutate_patch(self, i):
        root=self.patches[i % len(self.patches)]
        limits={k: self.env["d%s" % k]
                for k in "seed|style".split("|")}
        patches=Patches([root])
        npatches=self.env["nblocks"]*self.env["blocksize"]
        for i in range(npatches-1):
            patch=root.clone().mutate(limits)
            patches.append(patch)
        return patches

    @parse_line(config=[{"name": "I",
                         "type": "array"}])
    @render_patches(prefix="scatter")
    def do_scatter_patches(self, I,
                           patterns=[[0, 0, 0, 0],
                                     [0, 0, 0, 1],
                                     [0, 0, 1, 0],
                                     [0, 1, 0, 2]],
                           mutes=[[] for i in range(3)]+[[key] for key in Instruments]):
        roots=[self.patches[i % len(self.patches)]
               for i in I]
        patches=Patches()
        for i in range(self.env["nblocks"]):
            blockpattern=random.choice(patterns)
            blockpatches=[random.choice(roots)
                          for i in range(1+max(blockpattern))]
            blockmute=random.choice(mutes)            
            for j in range(self.env["blocksize"]):
                k=blockpattern[j]
                patch=blockpatches[k].clone()
                patch["mutes"]=blockmute
                patches.append(patch)
        return patches
                
    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    def do_show_patch(self, i, instruments=Instruments):
        patch=self.patches[i % len(self.patches)]
        rendered=patch.render(nbeats=self.env["nbeats"],
                              density=self.env["density"])
        trigs={K:{trig["i"]:trig for trig in V}
               for K, V in rendered.items()}
        for i in range(self.env["nbeats"]):
            row=[i]
            for key in instruments:
                if key in trigs:
                    if i in trigs[key]:
                        trig=trigs[key][i]
                        cell=str(trig["key"]) if "key" in trig else "%s:svdrum/%i" % (key, trig["id"])
                        row.append(cell)
                    else:
                        row.append("...")
            print ("\t".join([str(cell)
                              for cell in row]))

    @parse_line()
    def do_list_fixes(self):
        for k, V in self.fixes.items():
            for v in V.values():
                print ("- %s:%s" % (k, v))

    @parse_line(config=[{"name": "key",
                         "type": "str"},
                        {"name": "bankfrag",
                         "type": "str"},
                        {"name": "wavfrag",
                         "type": "str"}])
    def do_fix_sample(self, key, bankfrag, wavfrag):
        if key not in self.fixes:
            raise RuntimeError("instrument not found")
        bankname=self.banks.lookup(bankfrag)
        bank=self.banks[bankname]
        wavfile=bank.lookup(wavfrag)
        samplekey=SVSampleKey({"bank": bankname,
                               "file": wavfile})
        self.fixes.add(key, samplekey)

    @parse_line()
    def do_clean_fixes(self, instruments=Instruments):
        self.fixes=Fixes.create()
                
def validate_config(config):
    def validate_track_keys(config):
        modkeys=[mod["key"] for mod in config["modules"]
                 if "key" in mod]
        for key in modkeys:
            if key not in config["sequencers"]:
                raise RuntimeError("key %s missing from sequencer config" % key)
        for key in config["sequencers"]:
            if key not in modkeys:
                raise RuntimeError("key %s missing from module config" % key)
    def validate_module_links(config):
        modnames=[Output]+[mod["name"] for mod in config["modules"]]
        for links in config["links"]:
            for modname in links:
                if modname not in modnames:
                    raise RuntimeError("unknown module %s in links" % modname)
    def validate_module_refs(config):
        modnames=[mod["name"] for mod in config["modules"]]
        for attr in ["sequencers", "lfos"]:
            for item in config[attr].values():
                if item["mod"] not in modnames:
                    raise RuntimeError("mod %s not found" % item["mod"])
    validate_track_keys(config)
    validate_module_links(config)
    validate_module_refs(config)

Params=yaml.safe_load("""
temperature: 1.0
density: 0.75
dseed: 1.0
dstyle: 0.66666
nbeats: 16
blocksize: 4
nblocks: 8
""")

if __name__=="__main__":
    try:
        def load_yaml(filename, home="octavox/projects/picobeats"):
            return yaml.safe_load(open("%s/%s" % (home, filename)).read())
        banks=SVBanks("octavox/banks/pico")
        pools=banks.spawn_pools().cull()
        pools["svdrum-curated"]=svdrum=SVPool(load_yaml("svdrum.yaml"))
        svdrum["sn"]=pools["default-curated"]["sn"] # NB
        config=load_yaml("config.yaml")
        validate_config(config)
        PicobeatsCli(outdir="tmp/picobeats",
                     poolname="global-curated",
                     params=Params,
                     banks=banks,
                     pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
