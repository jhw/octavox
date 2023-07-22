from octavox.projects.picobeats.samples import Banks, Pools

from octavox.projects.picobeats.model import Patch, Patches

from octavox.projects import Nouns, Adjectives, is_abbrev

from datetime import datetime

import cmd, json, os, random, re, yaml

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
poolname: global-curated
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

    def wrap_action(fn):
        def wrapped(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except RuntimeError as error:
                print ("error: %s" % str(error))
        return wrapped

    def assert_project(fn):
        def wrapped(self, *args, **kwargs):
            if not self.project:
                raise RuntimeError("no project found")
            return fn(self, *args, **kwargs)
        return wrapped

    def parse_line(config):
        def parse_value(V):
            if re.search("^(\\-?\\d+\\|)+\\d+$", V): # array
                return [int(v) for v in V.split("|")]
            if re.search("^\\-?\\d+\\.\\d+$", V): # float
                return float(V)
            elif re.search("^\\-?\\d+$", V): # int
                return int(V)
            else: # str
                return V
        def decorator(fn):
            def wrapped(self, line):
                keys=[item["name"] for item in config]
                args=[tok for tok in line.split(" ") if tok!='']
                if len(args) < len(config):
                    raise RuntimeError("please enter %s" % ", ".join(keys))
                kwargs={k:parse_value(v)
                        for k, v in zip(keys, args[:len(keys)])}
                return fn(self, *[], **kwargs)
            return wrapped
        return decorator
            
    @wrap_action
    @parse_line(config=[{"name": "pat"},
                        {"name": "value"}])
    def do_setparam(self, pat, value):
        key=self.env.lookup(pat)
        self.env[key]=self.pools.lookup(value) if key=="poolname" else value
        print ("%s=%s" % (key, self.env[key]))

    @wrap_action
    @parse_line(config=[{"name": "pat"}])
    def do_getparam(self, pat):
        key=self.env.lookup(pat)
        print ("%s=%s" % (key, self.env[key]))

    @wrap_action
    def do_listparams(self, *args, **kwargs):
        print (yaml.safe_dump(dict(self.env)))

    @wrap_action
    def do_listpools(self, *args, **kwargs):
        print (yaml.safe_dump(sorted(list(self.pools.keys()))))
                    
    def render_patches(generator, nbreaks=0):
        def decorator(fn):
            def wrapped(self, *args, **kwargs):
                filename=random_filename(generator)
                print (filename)
                self.project=fn(self, *args, **kwargs)
                self.project.render_json(filename=filename)
                nbeats=self.env["nbeats"]
                density=self.env["density"]
                self.project.render_sunvox(banks=self.banks,
                                           nbeats=nbeats,
                                           nbreaks=nbreaks,
                                           density=density,
                                           filename=filename)
            return wrapped
        return decorator

    @wrap_action
    @render_patches(generator="random")
    def do_randomise(self, *args, **kwargs):
        poolname=self.pools[self.env["poolname"]]
        npatches=self.env["npatches"]
        return Patches.randomise(pool=poolname,
                                 n=npatches)

    @wrap_action
    @parse_line(config=[{"name": "frag"}])
    def do_load(self, frag, dirname="tmp/picobeats/json"):
        matches=[filename for filename in os.listdir(dirname)
                 if frag in filename]
        if matches==[]:
            print ("no matches")
        elif len(matches)==1:
            filename=matches.pop()
            print (filename)
            abspath="%s/%s" % (dirname, filename)
            patches=json.loads(open(abspath).read())
            self.project=Patches([Patch(**patch)
                                  for patch in patches])
        else:
            print ("multiple matches")

    @wrap_action
    @assert_project
    @parse_line(config=[{"name": "i"}])
    @render_patches(generator="mutation")
    def do_mutate(self, i):
        roots=self.project
        root=roots[i % len(roots)]
        limits={k: self.env["d%s" % k]
                for k in "slices|pat|seed|style".split("|")}
        npatches=self.env["npatches"]
        return Patches([root]+[root.clone().mutate(limits=limits)
                               for i in range(npatches-1)])

    @wrap_action
    @assert_project
    @parse_line(config=[{"name": "i"}])
    @render_patches(generator="chain",
                    nbreaks=1)
    def do_chain(self, i, instruments="kk|sn|ht".split("|")):
        # initialise
        roots=self.project
        root=roots[i % len(roots)]
        chain=Patches([root])
        npatches=self.env["npatches"]
        nmutations=int(npatches/4)                
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
    
    @wrap_action
    def do_exit(self, *args, **kwargs):
        return self.do_quit(*args, **kwargs)

    @wrap_action
    def do_quit(self, *args, **kwargs):
        print ("exiting")
        return True

if __name__=="__main__":
    try:
        banks=Banks("octavox/banks/pico")
        pools=banks.spawn_pools().cull()
        Shell(banks=banks,
              pools=pools).cmdloop()
    except RuntimeError as error:
        print ("error: %s" % str(error))
