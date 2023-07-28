from octavox.projects import SVEnvironment

import cmd, json, os, re, readline

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

class SVBaseCli(cmd.Cmd):

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

class SVBankCli(SVBaseCli):

    def __init__(self,
                 banks,
                 pools,
                 poolname,
                 *args,
                 **kwargs):
        SVBaseCli.__init__(self, *args, **kwargs)        
        self.banks=banks
        self.pools=pools
        self.poolname=poolname

    @parse_line(config=[{"name": "frag"}])
    def do_show_bank(self, frag):
        try:
            bankname=self.banks.lookup(str(frag))
            bank=self.banks[bankname]
            for wavfile in bank.wavfiles:
                print (wavfile)
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))
    
    def do_list_pools(self, _):
        for poolname in sorted(self.pools.keys()):
            poollabel=poolname.upper() if poolname==self.poolname else poolname
            print ("- %s [%i]" % (poollabel,
                                  self.pools[poolname].size))
            
    @parse_line(config=[{"name": "poolname"}])
    def do_set_pool(self, poolname):
        try:
            self.poolname=self.pools.lookup(poolname)
            print ("INFO: pool=%s" % self.poolname)
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))

    @parse_line(config=[{"name": "fsrc"},
                        {"name": "fdest"}])
    def do_copy_pool(self, fsrc, fdest):
        try:
            def lookup(self, frag):
                try:
                    return self.pools.lookup(str(frag))
                except RuntimeError as error:
                    return None
            src=lookup(self, fsrc)
            if not src:                
                raise RuntimeError("src does not exist")
            dest=lookup(self, fdest)
            if not dest:
                self.pools[fdest]=SVPool()
                dest=fdest
            print ("INFO: copying %s to %s" % (src, dest))
            self.pools[dest].add(self.pools[src])
        except RuntimeError as error:
            print ("ERROR: %s" % str(error))
                            
if __name__=="__main__":
    pass
