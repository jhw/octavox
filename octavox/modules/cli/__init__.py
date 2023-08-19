from octavox.modules import is_abbrev, list_s3_keys, has_internet

from octavox.modules.banks import SVPool

from octavox.modules.cli.parse import parse_line

from octavox.modules.model import SVPatch

from octavox.modules.project import SVProject

from datetime import datetime

import boto3, cmd, json, os, random, readline, yaml

def load_yaml(filename):
    return yaml.safe_load(open(os.path.join(os.path.dirname(__file__), filename)).read())

Nouns, Adjectives = (load_yaml("nouns.yaml"),
                     load_yaml("adjectives.yaml"))

HistorySize=100

def random_filename(prefix):
    ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    return "%s-%s-%s-%s" % (ts,
                            prefix,
                            random.choice(Adjectives),
                            random.choice(Nouns))

def assert_internet(fn):
    def wrapped(self, *args, **kwargs):
        if not has_internet():
            raise RuntimeError("not connected")
        return fn(self, *args, **kwargs)
    return wrapped

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
                 s3,
                 projectname,
                 bucketname,
                 params,
                 modules,
                 links,
                 historysize=HistorySize):
        cmd.Cmd.__init__(self)
        self.s3=s3
        self.projectname=projectname
        self.bucketname=bucketname
        self.outdir="tmp/%s" % projectname
        self.init_subdirs()
        self.modules=modules
        self.links=links
        self.env=SVEnvironment(params)
        self.patches=None
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
        for filename in sorted(os.listdir(self.outdir+"/json")):
            print (filename.split(".")[0])

    @parse_line(config=[{"name": "stem",
                         "type": "str"}])
    def do_load_project(self, stem):
        matches=[filename
                 for filename in sorted(os.listdir(self.outdir+"/json"))
                 if stem in filename]
        if matches==[]:
            print ("WARNING: no matches")
        elif len(matches)==1:
            filename=matches.pop()
            print ("INFO: %s" % filename)
            abspath="%s/json/%s" % (self.outdir, filename)
            patches=json.loads(open(abspath).read())
            self.patches=[SVPatch(**patch)
                          for patch in patches]
        else:
            print ("WARNING: multiple matches")

    @parse_line()
    @assert_internet
    def do_archive_project(self):
        if not self.patches:
            print ("ERROR: no patches found")
        else:
            s3key="archive/%s/%s.json" % (self.projectname,
                                          self.filename)
            self.s3.put_object(Bucket=self.bucketname,
                               Key=s3key,
                               Body=json.dumps(self.patches),
                               ContentType="application/json")
            
    @parse_line()
    def do_clean_projects(self):
        os.system("rm -rf %s" % self.outdir)
        self.init_subdirs()

    @parse_line()
    @assert_internet
    def do_reanimate_archives(self):
        prefix="archive/%s" % self.projectname
        for s3key in list_s3_keys(s3=self.s3,
                                  bucketname=self.bucketname,
                                  prefix=prefix):
            stem=s3key.split("/")[-1].split(".")[0]
            print (stem)
            struct=json.loads(self.s3.get_object(Bucket=self.bucketname,
                                                 Key=s3key)["Body"].read())
            filename="%s/json/%s.json" % (self.outdir, stem)
            with open(filename, 'w') as f:
                f.write(json.dumps(struct,
                                   indent=2))
            patches=[SVPatch(**patch).render(nbeats=self.env["nbeats"])
                     for patch in struct]
            project=SVProject().render(patches=patches,
                                       modconfig=self.modules,
                                       links=self.links,
                                       banks=self.banks,
                                       bpm=self.env["bpm"])
            filename="%s/sunvox/%s.sunvox" % (self.outdir, stem)
            with open(filename, 'wb') as f:
                project.write_to(f)
                    
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

    @parse_line()
    def do_randomise_pool(self):
        self.poolname=random.choice(list(self.pools.keys()))
        print ("INFO: pool=%s" % self.poolname)
        
if __name__=="__main__":
    pass
