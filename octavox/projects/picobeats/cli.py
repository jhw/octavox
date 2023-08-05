from octavox.modules.banks import SVSampleKey, SVBanks, SVPool

from octavox.modules.cli import SVBankCli, parse_line

from octavox.modules.project import SVNoteTrig

from octavox.projects import random_filename, flatten

from octavox.projects.picobeats.model import Patch, Patches

import json, os, random, yaml

Config=yaml.safe_load(open("octavox/projects/picobeats/config.yaml").read())

class Fixes(dict):

    @classmethod
    def create(self, soundkeys):
        return Fixes({soundkey:{} for soundkey in flatten(soundkeys.values())})
    
    def __init__(self, item={}):
        dict.__init__(self, item)

    def add(self, soundkey, samplekey):
        self[soundkey][str(samplekey)]=samplekey

class PicobeatsCli(SVBankCli):

    intro="Welcome to Picobeats :)"

    def __init__(self,
                 config=Config,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)
        self.fixes=Fixes.create(config["soundkeys"])

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
                                           bpm=self.env["bpm"],
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
                                  temperature=self.env["temperature"],
                                  density=self.env["density"])
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

    @parse_line(config=[{"name": "i",
                         "type": "int"}])
    def do_show_samples(self, i):
        patch=self.patches[i % len(self.patches)]
        rendered=patch.render(nbeats=self.env["nbeats"])
        trigs={K:{trig.i:trig for trig in V}
               for K, V in rendered.items()}
        for i in range(self.env["nbeats"]):
            for soundkey in trigs:
                if i in trigs[soundkey]:
                    trig=trigs[soundkey][i]
                    if isinstance(trig, SVNoteTrig):
                        if trig.samplekey:
                            print ("%i\t%s" % (i, trig.samplekey))

    @parse_line()
    def do_list_fixes(self):
        for k, V in self.fixes.items():
            for v in V.values():
                print ("- %s:%s" % (k, v))

    @parse_line(config=[{"name": "soundkey",
                         "type": "str"},
                        {"name": "bankfrag",
                         "type": "str"},
                        {"name": "wavfrag",
                         "type": "str"}])
    def do_fix_sample(self, soundkey, bankfrag, wavfrag):
        if soundkey not in self.fixes:
            raise RuntimeError("soundkey not found")
        bankname=self.banks.lookup(bankfrag)
        bank=self.banks[bankname]
        wavfile=bank.lookup(wavfrag)
        samplekey=SVSampleKey({"bank": bankname,
                               "file": wavfile})
        self.fixes.add(soundkey, samplekey)

    @parse_line()
    def do_clean_fixes(self, soundkeys=Config["soundkeys"]):
        self.fixes=Fixes.create(soundkeys)
                
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

if __name__=="__main__":
    try:
        def load_yaml(filename, home="octavox/projects/picobeats"):
            return yaml.safe_load(open("%s/%s" % (home, filename)).read())
        banks=SVBanks("octavox/banks/pico")
        pools=banks.spawn_pools().cull()
        pools["svdrum-curated"]=svdrum=SVPool(load_yaml("svdrum.yaml"))
        svdrum["sn"]=pools["default-curated"]["sn"] # NB
        PicobeatsCli(outdir="tmp/picobeats",
                     poolname="global-curated",
                     params=Params,
                     banks=banks,
                     pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
