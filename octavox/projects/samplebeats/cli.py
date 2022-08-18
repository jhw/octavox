import cmd, re, yaml

Parameters=yaml.safe_load("""
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
dslices: 
  type: number
  value: 0.5
dpat: 
  type: number
  value: 0.5
dmute: 
  type: number
  value: 0.0
dseed: 
  type: number
  value: 0.5
dstyle: 
  type: number
  value: 0.5
nbeats: 
  type: int
  value: 16
npatches: 
  type: int
  value: 64
""")

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
    @parse_line(keys=["key", "value"])
    def do_setparam(self, key, value):
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
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        param=self.params[key]
        validate(value, param)
        param["value"]=value
        print ("%s=%s" % (key, param["value"]))

    @wrap_action
    @parse_line(keys=["key"])
    def do_getparam(self, key):
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        param=self.params[key]
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
