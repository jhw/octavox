from octavox.projects.slicebeats.dom import Patches

from octavox.projects import Nouns, Adjectives

from datetime import datetime

import cmd, random, re, sys, yaml

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
dmute: 
  type: number
  value: 0.0
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
  value: 16
  min: 4
"""))

class Table(list):

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

def random_filename():
    return "%s-%s-%s" % (timestamp(),
                         random.choice(Adjectives),
                         random.choice(Nouns))
    
class Shell(cmd.Cmd):

    intro="Welcome to Octavox Slicebeats :)"

    prompt=">>> "

    def __init__(self, banks, env=Parameters):
        cmd.Cmd.__init__(self)
        self.banks=banks
        self.env=env
        self.stack=[]

    def wrap_action(fn):
        def wrapped(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except RuntimeError as error:
                print ("error: %s" % str(error))
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
    def do_listenv(self, *args, **kwargs):
        table=Table(sorted([{"key": k,
                             "value": v["value"]}
                            for k, v in self.env.items()],
                           key=lambda x: x["key"]))
        print (table.render(["key", "value"]))

    @parse_line()
    def do_randomise(self, *args, **kwargs):
        slicetemp=self.env["slicetemp"]["value"]
        n=self.env["npatches"]["value"]
        patches=Patches.randomise(banks=self.banks,
                                  slicetemp=slicetemp,
                                  n=n)
        filename=random_filename()
        self.stack.append((filename, patches))
        nbeats=self.env["nbeats"]["value"]
        patches.render(banks=self.banks,
                       nbeats=nbeats,
                       filename=filename)
        print (filename)

    @wrap_action
    def do_mutate(self, *args, **kwargs):
        print ("mutate")

    @wrap_action
    def do_exit(self, *args, **kwargs):
        return self.do_quit(*args, **kwargs)

    @wrap_action
    def do_quit(self, *args, **kwargs):
        print ("exiting")
        return True

if __name__=="__main__":
    try:
        pfname="default" if len(sys.argv) < 2 else sys.argv[1]
        if pfname not in Profiles:
            raise RuntimeError("profile is invalid")
        profile=Profiles[pfname]
        from octavox.samples.banks.pico import PicoBanks
        banks=PicoBanks(profile=profile,
                        root="tmp/banks/pico")
        Shell(banks).cmdloop()
    except RuntimeError as error:
        print ("error: %s" % str(error))
