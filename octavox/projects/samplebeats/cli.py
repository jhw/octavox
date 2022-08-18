import cmd, re, yaml

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
  value: 64
  min: 4
"""))

class SamplebeatsShell(cmd.Cmd):

    intro="Welcome to Octavox Samplebeats :)"

    prompt=">>> "

    def __init__(self, params=Parameters):
        cmd.Cmd.__init__(self)
        self.params=params
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

    @wrap_action
    @parse_line(keys=["pat", "value"])
    def do_setparam(self, pat, value):
        def validate(value, param):
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
            if "min" in param and value < param["min"]:
                raise RuntimeError("%s exceeds %s min value" % (value, key))
            if "max" in param and value > param["max"]:
                raise RuntimeError("%s exceeds %s max value" % (value, key))
        key, param = self.params.lookup(pat)
        validate(value, param)
        param["value"]=value
        print ("%s=%s" % (key, param["value"]))

    @wrap_action
    @parse_line(keys=["pat"])
    def do_getparam(self, pat):
        key, param = self.params.lookup(pat)
        print ("%s=%s" % (key, param["value"]))
    
    @parse_line()
    def do_randomise(self, *args, **kwargs):
        print ("randomise")

    @parse_line()
    def do_mutate(self, *args, **kwargs):
        print ("mutate")

    @parse_line()
    def do_exit(self, *args, **kwargs):
        return self.do_quit(arg)

    @parse_line()
    def do_quit(self, *args, **kwargs):
        print ("exiting")
        return True

if __name__=="__main__":
    SamplebeatsShell().cmdloop()
