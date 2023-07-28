from octavox.projects import random_filename

from octavox.modules.banks import SVBanks, SVPool, SVSampleKey

from octavox.modules.cli import SVCli, parse_line

from octavox.projects.picobeats.model import Patch, Patches, Instruments

from octavox.modules.project import Output

import json, os, traceback, yaml

class PicobeatsCli(SVCli):

    intro="Welcome to Picobeats :)"

    def __init__(self,
                 banks,
                 pools,
                 poolname,
                 *args,
                 **kwargs):
        SVCli.__init__(self, *args, **kwargs)        
        self.banks=banks
        self.pools=pools
        self.poolname=poolname

    @parse_line(config=[{"name": "frag"}])
    def do_show_bank(self, frag):
        try:
            bankname=self.banks.lookup(str(frag))
            bank=self.banks[bankname]
            for wavfile in bank.wavfiles:
                print (wavfile)
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))
    
    def do_list_pools(self, _):
        for poolname in sorted(self.pools.keys()):
            poollabel=poolname.upper() if poolname==self.poolname else poolname
            print ("- %s [%i]" % (poollabel,
                                  self.pools[poolname].size))
            
    @parse_line(config=[{"name": "poolname"}])
    def do_set_pool(self, poolname):
        try:
            self.poolname=self.pools.lookup(poolname)
            print ("INFO: pool=%s" % self.poolname)
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))

    @parse_line(config=[{"name": "fsrc"},
                        {"name": "fdest"}])
    def do_copy_pool(self, fsrc, fdest):
        try:
            def lookup(self, frag):
                try:
                    return self.pools.lookup(str(frag))
                except RuntimeError as error:
                    return None
            src=lookup(self, fsrc)
            if not src:                
                raise RuntimeError("src does not exist")
            dest=lookup(self, fdest)
            if not dest:
                self.pools[fdest]=SVPool()
                dest=fdest
            print ("INFO: copying %s to %s" % (src, dest))
            self.pools[dest].add(self.pools[src])
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))
                    
    def render_patches(prefix, nbreaks=0):
        def decorator(fn):
            def wrapped(self, *args, **kwargs):
                try:
                    self.filename=random_filename(prefix)
                    print ("INFO: %s" % self.filename)
                    self.project=fn(self, *args, **kwargs)
                    self.project.render_json(filename=self.filename)
                    self.project.render_sunvox(banks=self.banks,
                                               nbeats=self.env["nbeats"],
                                               nbreaks=nbreaks,
                                               density=self.env["density"],
                                               filename=self.filename)
                except RuntimeError as error:
                    print ("ERROR: %s" % str(error))
                except Exception as error:
                    print ("EXCEPTION: %s" % ''.join(traceback.TracebackException.from_exception(error).format()))
            return wrapped
        return decorator

    @render_patches(prefix="random")
    def do_randomise_patches(self, _):
        return Patches.randomise(pool=self.pools[self.poolname],
                                 temperature=self.env["temperature"],
                                 n=self.env["npatches"])

    @parse_line(config=[{"name": "i"}])
    @render_patches(prefix="concat")
    def do_concat_patches(self, i):
        I=[i] if not isinstance(i, list) else i
        return Patches([self.project[i % len(self.project)]
                       for i in I])

    @parse_line(config=[{"name": "i"}])
    @render_patches(prefix="decomp",
                    nbreaks=1)
    def do_decompile_patches(self, i, instruments=Instruments):
        I=[i] if not isinstance(i, list) else i
        patches=Patches([self.project[i % len(self.project)]
                       for i in I])
        for solo in instruments:
            mutes=[inst for inst in instruments
                   if inst!=solo]
            for patch in patches[:len(I)]:
                clone=patch.clone()
                clone["mutes"]=mutes
                patches.append(clone)
        return patches
    
    @parse_line(config=[{"name": "i"}])
    @render_patches(prefix="mutate")
    def do_mutate_patch(self, i):
        patch=self.project[i % len(self.project)]
        limits={k: self.env["d%s" % k]
                for k in "slices|pat|seed|style".split("|")}
        return Patches([patch]+[patch.clone().mutate(temperature=self.env["temperature"],
                                                   limits=limits)
                               for i in range(self.env["npatches"]-1)])
    
    @parse_line(config=[{"name": "i"}])
    def do_show_patch(self, i, instruments=Instruments):
        patch=self.project[i % len(self.project)]
        rendered=patch.render(nbeats=self.env["nbeats"],
                              density=self.env["density"])
        trigs={K:{trig["i"]:trig for trig in V}
               for K, V in rendered.items()}
        for i in range(self.env["nbeats"]):
            row=[i]
            for key in instruments:
                if i in trigs[key]:
                    trig=trigs[key][i]
                    value=SVSampleKey(trig["key"]).short_label if "key" in trig else "sv/%i" % trig["id"]
                    row.append("%s:%s" % (key, value))
                else:
                    row.append("...     ")
            print ("\t".join([str(cell)
                              for cell in row]))

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
dslices: 0.5
dpat: 0.5
dseed: 0.5
dstyle: 0.5
nbeats: 16
npatches: 32
""")
    
if __name__=="__main__":
    try:
        banks=SVBanks("octavox/banks/pico")
        pools=banks.spawn_pools().cull()
        pools["svdrum-curated"]=svdrum=SVPool(yaml.safe_load(open("octavox/projects/picobeats/svdrum.yaml").read()))
        svdrum["sn"]=pools["default-curated"]["sn"] # NB
        config=yaml.safe_load(open("octavox/projects/picobeats/config.yaml").read())):
        validate_config(config)
        PicobeatsCli(outdir="tmp/picobeats",
                     poolname="global-curated",
                     params=Params,
                     banks=banks,
                     pools=pools).cmdloop()
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
