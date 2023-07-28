from octavox.projects import SVEnvironment

import cmd, os, re, readline

HistorySize=100

def parse_line(config):
    def parse_array(line):
        values=[]
        for chunk in line.split("|"):
            if "x" in chunk:
                n, v = [int(tok) for tok in chunk.split("x")]
                values+=[v for i in range(n)]
            else:
                values.append(int(chunk))
        return values
    def parse_value(V):
        if re.search("^\\-?\\d+\\.\\d+$", V): # float
            return float(V)
        elif re.search("^\\-?\\d+$", V): # int
            return int(V)
        elif re.search("^(\\d+(x\\d+)?\\|)*\\d+(x\\d+)?$", V): # array
            return parse_array(V)
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

class SVCli(cmd.Cmd):

    prompt=">>> "

    def __init__(self,
                 outdir,
                 params,
                 subdirs=["json", "sunvox"],
                 historysize=HistorySize):
        cmd.Cmd.__init__(self)        
        self.outdir=outdir
        for subdir in subdirs:
            path="%s/%s" % (outdir, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
        self.env=SVEnvironment(params)
        self.historyfile=os.path.expanduser("%s/.clihistory" % self.outdir)
        self.historysize=historysize
        self.project=None
        self.filename=None

    def preloop(self):
        if os.path.exists(self.historyfile):
            readline.read_history_file(self.historyfile)
        
    def do_show_params(self, _):
        for key in sorted(self.env.keys()):
            print ("%s: %s" % (key, self.env[key]))
    
    @parse_line(config=[{"name": "pat"},
                        {"name": "value"}])
    def do_set_param(self, pat, value):
        try:
            key=self.env.lookup(pat)
            self.env[key]=value
            print ("INFO: %s=%s" % (key, self.env[key]))
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))

    def do_list_projects(self, _):
        for filename in os.listdir(self.outdir+"/json"):
            print (filename.split(".")[0])
                        
    @parse_line(config=[{"name": "frag"}])
    def do_load_project(self, frag):
        matches=[filename for filename in os.listdir(self.outdir+"/json")
                 if str(frag) in filename]
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
            
    def do_clear_projects(self, _):
        os.system("rm -rf %s" % self.outdir)
    
    def do_exit(self, _):
        return self.do_quit(None)

    def do_quit(self, _):
        print ("INFO: exiting")
        return True

    def postloop(self):
        readline.set_history_length(self.historysize)
        readline.write_history_file(self.historyfile)
                
if __name__=="__main__":
    pass
