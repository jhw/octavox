import cmd, re, yaml

Parameters=yaml.safe_load("""
slicetemp: 
  type: float
  value: 1
dslices: 
  type: float
  value: 0.5
dpat: 
  type: float
  value: 0.5
dmute: 
  type: float
  value: 0.0
dseed: 
  type: float
  value: 0.5
dstyle: 
  type: float
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
        def parse_value(v):
            if re.match("\\-?\\d+(\\.\\d+)?", v):
                return float(v)
            elif re.match("\\-?\\d+", v):
                return int(v)
            else:
                return v
        def decorator(fn):            
            def wrapped(self, line):
                args=[tok for tok in line.split(" ") if tok!='']
                if len(args) < len(keys):
                    raise RuntimeError("please enter %s" % ", ".join(keys))
                kwargs={k:parse_value(v)
                        for k, v in zip(keys, args[:len(keys)])}
                return fn(self, *[], **kwargs)
            return wrapped
        return decorator

    @wrap_action
    @parse_line(keys=["key", "value"])
    def do_set_param(self, key, value):
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        if eval(self.params[key]["type"])!=type(value):
            raise RuntimeError("%s value [%s] is invalid type" % (key, value))
        self.params[key]["value"]=value
        print ("%s=%s" % (key, self.params[key]["value"]))

    @wrap_action
    @parse_line(keys=["key"])
    def do_get_param(self, key):
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        print ("%s=%s" % (key, self.params[key]["value"]))
    
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
