from octavox.modules.banks import SVSampleKey, SVBanks, SVPool

from octavox.modules.cli import SVBankCli, parse_line

from octavox.modules.project import Output

from octavox.projects import random_filename

from octavox.projects.picobass.model import Patch, Patches, Instruments

import json, os, random, yaml

class PicobassCli(SVBankCli):

    intro="Welcome to Picobass :)"

    def __init__(self,
                 instruments=Instruments,
                 *args,
                 **kwargs):
        SVBankCli.__init__(self, *args, **kwargs)

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
                                  temperature=self.env["temperature"])
            patches.append(patch)
        return patches

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
        def load_yaml(filename, home="octavox/projects/picobass"):
            return yaml.safe_load(open("%s/%s" % (home, filename)).read())
        banks=SVBanks("octavox/banks/pico")
        pools=banks.spawn_pools().cull()
        config=load_yaml("config.yaml")
        validate_config(config)
        PicobassCli(outdir="tmp/picobass",
                    poolname="global-curated",
                    params=Params,
                    banks=banks,
                    pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
