from octavox.projects.slicebeats.model import Patch, Patches

from octavox.projects import Nouns, Adjectives

from datetime import datetime

import cmd, json, os, random, re, yaml

Profiles=yaml.safe_load("""
default:
  kk: 0.7
  sn: 0.7
  oh: 0.4
  ch: 0.4
strict:
  kk: 1.0
  sn: 1.0
  oh: 0.8
  ch: 0.8
wild:
  kk: 0.4
  sn: 0.4
  oh: 0.2
  ch: 0.2
""")

class Parameterz(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def lookup(self, pat):
        keys=[key for key in self
              if pat in key]
        if keys==[]:
            raise RuntimeError("%s not found" % pat)
        elif len(keys) > 1:
            raise RuntimeError("multiple key matches for %s" % pat)
        key=keys.pop()
        return (key, self[key])            
        
Parameters=Parameterz(yaml.safe_load("""
profile:
  type: enum
  value: default
  options:
  - strict
  - default
  - wild
slicetemp: 
  type: number
  value: 1
  min: 0
  max: 1
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
nbreaks: 
  type: int
  value: 0
  min: 0
"""))

class KwikTable(list):

    def __init__(self, items=[]):
        list.__init__(self, items)

    def render(self, keys, width=16):
        def format_value(value, width):
            return value[:width] if len(value) > width else value+" ".join(['' for i in range(width-len(value))])
        return "\n".join([" ".join([format_value(str(item[key]) if key in item else '', width)
                                    for key in keys])
                          for item in self])

def timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")

def random_filename(generator):
    return "%s-%s-%s-%s" % (timestamp(),
                            generator,
                            random.choice(Adjectives),
                            random.choice(Nouns))
    
class Shell(cmd.Cmd):

    intro="Welcome to Octavox Slicebeats :)"

    prompt=">>> "

    def __init__(self, banks, env=Parameters):
        cmd.Cmd.__init__(self)
        self.banks=banks
        profilename=env["profile"]["value"]
        self.banks.profile=Profiles[profilename]
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

    def parse_line(keys=[]):
        def optimistic_parse(v):
            if re.search("^\\-?\\d+$", v):
                return int(v)
            elif re.search("^\\-?\\d+(\\.\\d+)?$", v):
                return float(v)
            else:
                return v
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

    def validate_param(fn):
        def validate_type(key, value, param):
            def is_number(value):
                return type(value) in [int, float]
            def is_int(value):
                return isinstance(value, int)
            def is_enum(value, options):
                return value in options
            fn=eval("is_%s" % param["type"])
            kwargs={"value": value}
            if param["type"]=="enum":
                kwargs["options"]=param["options"]
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
    def do_setparam(self, pat, value, profiles=Profiles):
        key, param = self.env.lookup(pat)
        param["value"]=value
        print ("%s=%s" % (key, param["value"]))
        if key=="profile":
            print ("updating bank profile")
            self.banks.profile=profiles[value]

    @wrap_action
    @parse_line(keys=["pat"])
    def do_getparam(self, pat):
        key, param = self.env.lookup(pat)
        print ("%s=%s" % (key, param["value"]))

    @wrap_action
    def do_listparams(self, *args, **kwargs):
        table=KwikTable(sorted([{"key": k,
                                 "value": v["value"]}
                                for k, v in self.env.items()],
                               key=lambda x: x["key"]))
        print (table.render(["key", "value"]))

    def validate_int(config):
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

    def render_patches(generator):
        def decorator(fn):
            def wrapped(self, *args, **kwargs):

                filename=random_filename(generator)
                print (filename)

                self.project=fn(self, *args, **kwargs)
                self.project.render_json(filename=filename)
                nbeats, nbreaks = (self.env["nbeats"]["value"],
                                   self.env["nbreaks"]["value"])
                self.project.render_sunvox(banks=self.banks,
                                           nbeats=nbeats,
                                           nbreaks=nbreaks,
                                           filename=filename)
            return wrapped
        return decorator
    
    @wrap_action
    @parse_line(keys=["npatches"])
    @validate_int({"name": "npatches",
                   "min": 1})
    @render_patches("randomiser")
    def do_randomise(self, npatches):
        slicetemp=self.env["slicetemp"]["value"]
        return Patches.randomise(banks=self.banks,
                                 slicetemp=slicetemp,
                                 n=npatches)

    @wrap_action
    @parse_line(keys=["frag"])
    def do_load(self, frag, dirname="tmp/slicebeats/json"):
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
    @parse_line(keys=["i", "npatches"])
    @validate_int({"name": "i",
                   "min": 0})
    @validate_int({"name": "npatches",
                   "min": 1})
    @render_patches("mutator")
    def do_mutate(self, i, npatches):
        roots=self.project
        root=roots[i % len(roots)]
        limits={k: self.env["d%s" % k]["value"]
                for k in "slices|pat|seed|style".split("|")}
        slicetemp=self.env["slicetemp"]["value"]
        return Patches([root]+[root.clone().mutate(limits=limits,
                                                   slicetemp=slicetemp)
                               for i in range(npatches-1)])

    @wrap_action
    def do_exit(self, *args, **kwargs):
        return self.do_quit(*args, **kwargs)

    @wrap_action
    def do_quit(self, *args, **kwargs):
        print ("exiting")
        return True

if __name__=="__main__":
    try:
        from octavox.banks.pico import PicoBanks
        banks=PicoBanks()
        Shell(banks).cmdloop()
    except RuntimeError as error:
        print ("error: %s" % str(error))
