from octavox.modules import is_abbrev

from octavox.modules.banks import SVPool

from octavox.modules.cli.parse import parse_line

from octavox.modules.project import SVProject

from datetime import datetime

import cmd, json, os, random, readline, yaml

def load_yaml(filename):
    return yaml.safe_load(open("octavox/modules/cli/%s" % filename).read())

Nouns, Adjectives = (load_yaml("nouns.yaml"),
                     load_yaml("adjectives.yaml"))

HistorySize=100

def random_filename(prefix):
    ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    return "%s-%s-%s-%s" % (ts,
                            prefix,
                            random.choice(Adjectives),
                            random.choice(Nouns))


def render_patches(prefix):
    def decorator(fn):
        def dump_json(self):
            filename="%s/json/%s.json" % (self.outdir,
                                          self.filename)
            with open(filename, 'w') as f:
                f.write(json.dumps(self.patches,
                                   indent=2))
        def dump_sunvox(self):
            project=SVProject().render(patches=[patch.render(nbeats=self.env["nbeats"])
                                                for patch in self.patches],
                                       modconfig=self.modules,
                                       links=self.links,
                                       banks=self.banks,
                                       bpm=self.env["bpm"])
            filename="%s/sunvox/%s.sunvox" % (self.outdir,
                                              self.filename)
            with open(filename, 'wb') as f:
                project.write_to(f)
        def wrapped(self, *args, **kwargs):
            self.filename=random_filename(prefix)
            print ("INFO: %s" % self.filename)
            self.patches=fn(self, *args, **kwargs)
            dump_json(self)
            dump_sunvox(self)
        return wrapped
    return decorator

class SVEnvironment(dict):

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
        return matches.pop()

class SVBaseCli(cmd.Cmd):

    prompt=">>> "

    def __init__(self,
                 projectname,
                 params,
                 modules,
                 links,
                 historysize=HistorySize):
        cmd.Cmd.__init__(self)
        self.projectname=projectname
        self.outdir="tmp/%s" % projectname
        self.init_subdirs()
        self.modules=modules
        self.links=links
        self.env=SVEnvironment(params)
        self.project=None
        self.filename=None
        self.historyfile=os.path.expanduser("%s/.clihistory" % self.outdir)
        self.historysize=historysize

    def init_subdirs(self, subdirs=["json", "sunvox"]):
        for subdir in subdirs:
            path="%s/%s" % (self.outdir, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
        
    def preloop(self):
        if os.path.exists(self.historyfile):
            readline.read_history_file(self.historyfile)

    @parse_line()
    def do_show_params(self):
        for key in sorted(self.env.keys()):
            print ("%s: %s" % (key, self.env[key]))
    
    @parse_line(config=[{"name": "pat",
                         "type": "str"},
                        {"name": "value",
                         "type": "number"}])
    def do_set_param(self, pat, value):
        key=self.env.lookup(pat)
        self.env[key]=value
        print ("INFO: %s=%s" % (key, self.env[key]))

    @parse_line()
    def do_list_projects(self):
        for filename in os.listdir(self.outdir+"/json"):
            print (filename.split(".")[0])

    @parse_line()
    def do_clean_projects(self):
        os.system("rm -rf %s" % self.outdir)
        self.init_subdirs()
        
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

    @parse_line(config=[{"name": "frag",
                         "type": "str"}])
    def do_show_bank(self, frag):
        bankname=self.banks.lookup(str(frag))
        bank=self.banks[bankname]
        for wavfile in bank.wavfiles:
            print (wavfile)

    @parse_line()
    def do_list_pools(self):
        for poolname in sorted(self.pools.keys()):
            prompt=">" if poolname==self.poolname else " "
            print ("%s %s [%i]" % (prompt,
                                   poolname,
                                   len(self.pools[poolname])))
            
    @parse_line(config=[{"name": "poolname",
                         "type": "str"}])
    def do_set_pool(self, poolname):
        self.poolname=self.pools.lookup(poolname)
        print ("INFO: pool=%s" % self.poolname)

    @parse_line(config=[{"name": "fsrc",
                         "type": "str"},
                        {"name": "fdest",
                         "type": "str"}])
    def do_copy_pool(self, fsrc, fdest):
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
        self.poolname=dest
        print ("INFO: pool=%s" % dest)
                           
if __name__=="__main__":
    pass
