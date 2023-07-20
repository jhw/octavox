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
        key=matches.pop()
        return (key, self[key])  
        
Env=Environment(yaml.safe_load("""
dslices: 
  type: number
  value: 0.5
  min: 0
  max: 1
dpat: 
  type: number
  value: 0.5
  min: 0
  max: 1
dseed: 
  type: number
  value: 0.5
  min: 0
  max: 1
dstyle: 
  type: number
  value: 0.5
  min: 0
  max: 1
nbeats: 
  type: int
  value: 16
  min: 4
npatches:
  type: int
  value: 32
  min: 4
poolname:
  type: str
  value: global-curated
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

    """
    - floats and negative number support currently not required
    """
    
    def parse_line(keys=[]):
        def optimistic_parse(V):
            if re.search("^(\\d+\\|)+\\d+$", V): # array
                return [int(v) for v in V.split("|")]
            elif re.search("^\\d+$", V): # int
                return int(V)
            else:
                return V
        def decorator(fn):            
            def wrapped(self, line):
                args=[tok for tok in line.split(" ") if tok!='']
                if len(args) < len(keys):
                    raise RuntimeError("please enter %s" % ", ".join(keys))
                kwargs={k:optimistic_parse(v)
                        for k, v in zip(keys, args[:len(keys)])}
                return fn(self, *[], **kwargs)
            return wrapped
        return decorator

    def validate_int_arg(config):
        def decorator(fn):
            def wrapped(self, *args, **kwargs):
                if config["name"] not in kwargs:
                    raise RuntimeError("%s not found" % config["name"])
                value=kwargs[config["name"]]
                if not isinstance(value, int):
                    raise RuntimeError("%s is not an integer" % config["name"])
                if "min" in config and value < config["min"]:
                    raise RuntimeError("%s exceeds minimum" % config["name"])
                return fn(self, *args, **kwargs)
            return wrapped
        return decorator

    def validate_array_arg(config):
        def decorator(fn):
            def wrapped(self, *args, **kwargs):
                if config["name"] not in kwargs:
                    raise RuntimeError("%s not found" % config["name"])
                value=kwargs[config["name"]]
                if not isinstance(value, int):
                    raise RuntimeError("%s is not an array" % config["name"])
                for v in value:
                    if not isinstance(v, int):
                        raise RuntimeError("%s is not an array" % config["name"])
                    if "min" in config and v < config["min"]:
                        raise RuntimeError("%s exceeds minimum" % config["name"])
                return fn(self, *args, **kwargs)
            return wrapped
        return decorator

    """
    - no need for array support here
    """
    
    def validate_param(fn):
        def validate_type(key, value, param):
            def is_number(value):
                return type(value) in [int, float]
            def is_int(value):
                return isinstance(value, int)
            def is_str(value):
                return True
            fn=eval("is_%s" % param["type"])
            kwargs={"value": value}
            if not fn(**kwargs):
                raise RuntimeError("%s is invalid %s value" % (value, key))
        def validate_minmax(key, value, param):
            if "min" in param and value < param["min"]:
                raise RuntimeError("%s exceeds %s min value" % (value, key))
            if "max" in param and value > param["max"]:
                raise RuntimeError("%s exceeds %s max value" % (value, key))
        def wrapped(self, *args, **kwargs):
            pat, value = kwargs["pat"], kwargs["value"]
            key, param = self.env.lookup(pat)
            validate_type(key, value, param)
            validate_minmax(key, value, param)
            return fn(self, *args, **kwargs)
        return wrapped

    @wrap_action
    @parse_line(keys=["pat", "value"])
    @validate_param
    def do_setparam(self, pat, value):
        key, param = self.env.lookup(pat)
        param["value"]=self.pools.lookup(value) if key=="poolname" else value
        print ("%s=%s" % (key, param["value"]))

    @wrap_action
    @parse_line(keys=["pat"])
    def do_getparam(self, pat):
        key, param = self.env.lookup(pat)
        print ("%s=%s" % (key, param["value"]))

    @wrap_action
    def do_listparams(self, *args, **kwargs):
        print (yaml.safe_dump({k:v["value"]
                               for k, v in self.env.items()}))

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
                nbeats=self.env["nbeats"]["value"]
                self.project.render_sunvox(banks=self.banks,
                                           nbeats=nbeats,
                                           nbreaks=nbreaks,
                                           filename=filename)
            return wrapped
        return decorator
    
    @wrap_action
    @render_patches(generator="random")
    def do_randomise(self, *args, **kwargs):
        poolname=self.pools[self.env["poolname"]["value"]]
        npatches=self.env["npatches"]["value"]
        return Patches.randomise(pool=poolname,
                                 n=npatches)

    @wrap_action
    @parse_line(keys=["frag"])
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
    @parse_line(keys=["i"])
    @validate_int_arg({"name": "i",
                       "min": 0})
    @render_patches(generator="mutation")
    def do_mutate(self, i):
        roots=self.project
        root=roots[i % len(roots)]
        limits={k: self.env["d%s" % k]["value"]
                for k in "slices|pat|seed|style".split("|")}
        npatches=self.env["npatches"]["value"]
        return Patches([root]+[root.clone().mutate(limits=limits)
                               for i in range(npatches-1)])

    @wrap_action
    @assert_project
    @parse_line(keys=["i"])
    @validate_int_arg({"name": "i",
                       "min": 0})
    @render_patches(generator="chain",
                    nbreaks=1)
    def do_chain(self, i, instruments="kk|sn|ht".split("|")):
        # initialise
        roots=self.project
        root=roots[i % len(roots)]
        """
        samples=[slice["samples"]                 
                 for slice in root["tracks"]["slices"]]
        """
        chain=Patches([root])
        npatches=self.env["npatches"]["value"]
        nmutations=int(npatches/4)                
        # generate mutations
        limits={k: self.env["d%s" % k]["value"]
                for k in "slices|pat|seed|style".split("|")}
        for i in range(nmutations-1):
            mutation=root.clone().mutate(limits=limits)
            # override samples
            """
            for i, slice in enumerate(mutation["tracks"]["slices"]):
                slice["samples"]=samples[i % len(samples)]
            """
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
