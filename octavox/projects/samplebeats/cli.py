import cmd, re, yaml

DefaultParams=[]

class SamplebeatsShell(cmd.Cmd):

    intro="Welcome to Octavox Samplebeats :)"

    prompt=">>> "

    def __init__(self, params=DefaultParams):
        cmd.Cmd.__init__(self)
        self.params=params
        self.stack=[]

    def wrap_action(params=[]):
        def parse_int(v, param):
            if not re.match("\\-?\\d+", v):
                raise RuntimeError("%s is not an int" % v)
            return int(v)
        def parse_float(v, param):
            if not re.match("\\-?\\d+(\\.\\d+)?", v):
                raise RuntimeError("%s is not a float" % v)
            return float(v)
        def parse_value(v, param):
            if "type" not in param:
                return v
            elif param["type"]=="int":
                return parse_int(v, param)
            elif param["type"]=="float":
                return parse_float(v, param)
            else:
                return v
        def decorator(fn):            
            def wrapped(self, line):
                try:
                    args=[tok for tok in line.split(" ")
                          if tok!='']
                    if len(args) < len(params):
                        paramnames=[param["name"]
                                    for param in params]
                        raise RuntimeError("please enter %s" % ", ".join(paramnames))
                    kwargs={param["name"]:parse_value(v, param)
                            for param, v in zip(params, args[:len(params)])}
                    return fn(self, **kwargs)
                except RuntimeError as error:
                    print ("error: %s" % str(error))
            return wrapped
        return decorator

    @wrap_action(params=[{"name": "key",
                          "name": "value"}])
    def do_set_param(self, key, value):
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        print (key, value)

    @wrap_action(params=[{"name": "key"}])
    def do_get_param(self, key):
        if key not in self.params:
            raise RuntimeError("%s not found" % key)
        print (key)
    
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
