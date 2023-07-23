from octavox.projects.picobeats.samples import Banks, Pools, Pool

from octavox.projects.picobeats.model import Patch, Patches

from octavox.projects import Nouns, Adjectives, is_abbrev

from datetime import datetime

import cmd, json, os, random, re, traceback, yaml

class Environment(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def lookup(self, abbrev):
        matches=[]
        for key in self:
            if is_abbrev(abbrev, key):
                matches.append(key)
        if matches==[]:
            raise RuntimeError("%s not found" % abbrev)
        elif len(matches) > 1:
            raise RuntimeError("multiple key matches for %s" % abbrev)
        return matches.pop()
        
Env=Environment(yaml.safe_load("""
dslices: 0.5
dpat: 0.5
dseed: 0.5
dstyle: 0.5
nbeats: 16
density: 0.75
npatches: 32
pool: global-curated
"""))

def random_filename(generator):
    ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    return "%s-%s-%s-%s" % (ts,
                            generator,
                            random.choice(Adjectives),
                            random.choice(Nouns))

class Shell(cmd.Cmd):

    intro="Welcome to Octavox Picobeats :)"

    prompt=">>> "

    def __init__(self,
                 banks,
                 pools,
                 env=Env):
        cmd.Cmd.__init__(self)
        self.banks=banks
        self.pools=pools
        self.env=env
        self.project=None
        self.filename=None

    def parse_line(config):
        def parse_value(V):
            if re.search("^\\-?\\d+\\.\\d+$", V): # float
                return float(V)
            elif re.search("^\\-?\\d+$", V): # int
                return int(V)
            else: # str
                return V
        def decorator(fn):
            def wrapped(self, line):
                try:
                    keys=[item["name"] for item in config]
                    args=[tok for tok in line.split(" ") if tok!='']
                    if len(args) < len(config):
                        raise RuntimeError("please enter %s" % ", ".join(keys))
                    kwargs={k:parse_value(v)
                            for k, v in zip(keys, args[:len(keys)])}
                    return fn(self, *[], **kwargs)
                except RuntimeError as error:
                    print ("ERROR: %s" % str(error))
            return wrapped
        return decorator
            
    @parse_line(config=[{"name": "pat"},
                        {"name": "value"}])
    def do_param(self, pat, value):
        try:
            key=self.env.lookup(pat)
            self.env[key]=self.pools.lookup(value) if key=="pool" else value
            print ("INFO: %s=%s" % (key, self.env[key]))
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))

    def do_params(self, _):
        print (yaml.safe_dump(dict(self.env)))

    def do_pools(self, _):
        for poolname in sorted(self.pools.keys()):
            print ("- %s [%i]" % (poolname,
                                  self.pools[poolname].size))
                    
    def render_patches(generator, nbreaks=0):
        def decorator(fn):
            def wrapped(self, *args, **kwargs):
                try:
                    self.filename=random_filename(generator)
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

    @render_patches(generator="random")
    def do_randomise(self, _):
        return Patches.randomise(pool=self.pools[self.env["pool"]],
                                 n=self.env["npatches"])

    @parse_line(config=[{"name": "frag"}])
    def do_load(self, frag, dirname="tmp/picobeats/json"):
        matches=[filename for filename in os.listdir(dirname)
                 if frag in filename]
        if matches==[]:
            print ("WARNING: no matches")
        elif len(matches)==1:
            filename=matches.pop()
            print ("INFO: %s" % filename)
            abspath="%s/%s" % (dirname, filename)
            patches=json.loads(open(abspath).read())
            self.project=Patches([Patch(**patch)
                                  for patch in patches])
        else:
            print ("WARNING: multiple matches")

    @parse_line(config=[{"name": "i"}])
    @render_patches(generator="mutate")
    def do_mutate(self, i):
        roots=self.project
        root=roots[i % len(roots)]
        limits={k: self.env["d%s" % k]
                for k in "slices|pat|seed|style".split("|")}
        return Patches([root]+[root.clone().mutate(limits=limits)
                               for i in range(self.env["npatches"]-1)])

    @parse_line(config=[{"name": "i"}])
    @render_patches(generator="octachain",
                    nbreaks=1)
    def do_octachain(self, i, instruments="kk|sn|ht".split("|")):
        # initialise
        roots=self.project
        root=roots[i % len(roots)]
        chain=Patches([root])
        nmutations=int(self.env["npatches"]/4)                
        # generate mutations
        limits={k: self.env["d%s" % k]
                for k in "slices|pat|seed|style".split("|")}
        for i in range(nmutations-1):
            mutation=root.clone().mutate(limits=limits)
            chain.append(mutation)
        # add mutes
        for solo in instruments:
            mutes=[inst for inst in instruments
                   if inst!=solo]
            for mutation in chain[:nmutations]:
                clone=mutation.clone()
                clone["mutes"]=mutes
                chain.append(clone)
        # return
        return chain

    @parse_line(config=[{"name": "fsrc"},
                        {"name": "fdest"}])
    def do_copy(self, fsrc, fdest):
        try:
            def lookup(self, frag):
                try:
                    return self.pools.lookup(frag)
                except RuntimeError as error:
                    return None
            src=lookup(self, fsrc)
            if not src:                
                raise RuntimeError("src does not exist")
            dest=lookup(self, fdest)
            if not dest:
                self.pools[fdest]=Pool()
                dest=fdest
            print ("INFO: copying %s to %s" % (src, dest))
            self.pools[dest].add(self.pools[src])
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))
    
    def do_clean(self, _):
        os.system("rm -rf tmp/picobeats")
    
    def do_exit(self, _):
        return self.do_quit(None)

    def do_quit(self, _):
        print ("INFO: exiting")
        return True

if __name__=="__main__":
    banks=Banks("octavox/banks/pico")
    pools=banks.spawn_pools().cull()
    Shell(banks=banks,
          pools=pools).cmdloop()
