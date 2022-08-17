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

    def wrap_action(keys=[]):
        def decorator(fn):            
            def wrapped(self, line):
                try:
                    args=[tok for tok in line.split(" ") if tok!='']
                    if len(args) < len(keys):
                        raise RuntimeError("please enter %s" % ", ".join(keys))
                    kwargs={k:v for k, v in zip(keys, args[:len(keys)])}
                    return fn(self, **kwargs)
                except RuntimeError as error:
                    print ("error: %s" % str(error))
            return wrapped
        return decorator

    @wrap_action(keys=["key", "value"])
    def do_set_param(self, key, value):
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        self.params[key]["value"]=value
        print ("%s=%s" % (key, self.params[key]["value"]))

    @wrap_action(keys=["key"])
    def do_get_param(self, key):
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        print ("%s=%s" % (key, self.params[key]["value"]))
    
    @wrap_action()
    def do_randomise(self, **kwargs):
        print ("randomise")

    @wrap_action()
    def do_mutate(self, **kwargs):
        print ("mutate")

    @wrap_action()
    def do_exit(self, **kwargs):
        return self.do_quit(arg)

    @wrap_action()
    def do_quit(self, **kwargs):
        print ("exiting")
        return True

if __name__=="__main__":
    SamplebeatsShell().cmdloop()
