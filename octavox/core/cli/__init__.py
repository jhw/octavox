from octavox import has_internet

from octavox.core import is_abbrev, list_s3_keys

from octavox.core.banks import SVPool

from octavox.core.cli.parse import parse_line

from octavox.core.model import SVPatch

from octavox.core.project import SVProject

from octavox.core.utils.export import export_wav

from pydub import AudioSegment

from datetime import datetime

import boto3, cmd, json, os, random, readline, yaml

Nouns, Adjectives = (yaml.safe_load(open("octavox/core/cli/nouns.yaml").read()),
                     yaml.safe_load(open("octavox/core/cli/adjectives.yaml").read()))

HistorySize=100

def random_filename(prefix):
    ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    return "%s-%s-%s-%s" % (ts,
                            prefix,
                            random.choice(Adjectives),
                            random.choice(Nouns))
    
def render_patches(prefix):
    def decorator(fn):
        def wrapped(self, *args, **kwargs):
            self.filename=random_filename(prefix)
            print ("INFO: %s" % self.filename)
            self.patches=fn(self, *args, **kwargs)
            self.dump_dsl()
            self.dump_sunvox()
        return wrapped
    return decorator

def assert_internet(fn):
    def wrapped(self, *args, **kwargs):
        if not has_internet():
            raise RuntimeError("not connected")
        return fn(self, *args, **kwargs)
    return wrapped

def assert_project(fn):
    def wrapped(self, *args, **kwargs):
        if not self.patches:
            raise RuntimeError("no patches found")
        return fn(self, *args, **kwargs)
    return wrapped

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
                 env,
                 modules,
                 links,
                 historysize=HistorySize):
        cmd.Cmd.__init__(self)
        self.s3=s3
        self.projectname=projectname
        self.bucketname=bucketname
        self.outdir="tmp/%s" % projectname
        self.init_subdirs()
        self.core=modules
        self.links=links
        self.env=SVEnvironment(env)
        self.patches=None
        self.filename=None
        self.historyfile=os.path.expanduser("%s/.clihistory" % self.outdir)
        self.historysize=historysize

    def init_subdirs(self, subdirs=["dsl", "sunvox", "wav"]):
        for subdir in subdirs:
            path="%s/%s" % (self.outdir, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
        
    def preloop(self):
        if os.path.exists(self.historyfile):
            readline.read_history_file(self.historyfile)

    def dump_dsl(self):
        filename="%s/dsl/%s.json" % (self.outdir,
                                     self.filename)
        with open(filename, 'w') as f:
            f.write(json.dumps(self.patches,
                               indent=2))

    def render_project(self):
        rendered=[patch.render(nticks=self.env["nticks"],
                               density=self.env["density"],
                               temperature=self.env["temperature"])
                  for patch in self.patches]
        return SVProject().render(patches=rendered,
                                  modconfig=self.core,
                                  links=self.links,
                                  banks=self.banks,
                                  bpm=self.env["bpm"],
                                  nbreaks=self.env["nbreaks"])
            
    def dump_sunvox(self):
        filename="%s/sunvox/%s.sunvox" % (self.outdir,
                                          self.filename)
        with open(filename, 'wb') as f:
            project=self.render_project()
            project.write_to(f)
                        
    @parse_line()
    def do_show_params(self):
        for key in sorted(self.env.keys()):
            print ("%s: %s" % (key, self.env[key]))
    
    @parse_line(config=[{"name": "frag",
                         "type": "str"},
                        {"name": "value",
                         "type": "number"}])
    def do_set_param(self, frag, value):
        key=self.env.lookup(frag)
        if key:
            self.env[key]=value
            print ("INFO: %s=%s" % (key, self.env[key]))
        else:
            print ("WARNING: %s not found" % frag)
            
    @parse_line()
    def do_list_projects(self):
        for filename in sorted(os.listdir(self.outdir+"/dsl")):
            print (filename.split(".")[0])

    @parse_line(config=[{"name": "stem",
                         "type": "str"}])
    def do_load_project(self, stem):
        matches=[filename
                 for filename in sorted(os.listdir(self.outdir+"/dsl"))
                 if stem in filename]
        if matches==[]:
            print ("WARNING: no matches")
        elif len(matches)==1:
            self.filename=matches.pop().split(".")[0]
            print ("INFO: %s" % self.filename)
            abspath="%s/dsl/%s.json" % (self.outdir, self.filename)
            patches=json.loads(open(abspath).read())
            self.patches=[SVPatch(**patch)
                          for patch in patches]
        else:
            print ("WARNING: multiple matches")

    @parse_line()
    @assert_internet
    @assert_project
    def do_archive_project(self):
        s3key="archive/%s/%s.json" % (self.projectname,
                                      self.filename)
        self.s3.put_object(Bucket=self.bucketname,
                           Key=s3key,
                           Body=json.dumps(self.patches,
                                           indent=2),
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
            filename="%s/dsl/%s.json" % (self.outdir, stem)
            with open(filename, 'w') as f:
                f.write(json.dumps(struct,
                                   indent=2))
            patches=[SVPatch(**patch).render(nticks=self.env["nticks"],
                                             density=self.env["density"],
                                             temperature=self.env["temperature"])
                     for patch in struct]
            project=SVProject().render(patches=patches,
                                       modconfig=self.core,
                                       links=self.links,
                                       banks=self.banks,
                                       bpm=self.env["bpm"],
                                       nbreaks=self.env["nbreaks"])
            filename="%s/sunvox/%s.sunvox" % (self.outdir, stem)
            with open(filename, 'wb') as f:
                project.write_to(f)

    @parse_line()
    @assert_project
    def do_export_stems(self, fade=5):
        wavfilename="%s/wav/%s.wav" % (self.outdir,
                                       self.filename)
        project=self.render_project()
        export_wav(project=project,
                   filename=wavfilename)
        audio=AudioSegment.from_wav(wavfilename)
        nbeats=int(self.env["nticks"]/self.env["tpb"])
        duration=int(1000*60*nbeats/self.env["bpm"])       
        destdirname="%s/stems/%s" % (self.outdir,
                                     self.filename)
        if not os.path.exists(destdirname):
            os.makedirs(destdirname)
        nbreaks=self.env["nbreaks"]
        for i in range(len(self.patches)):
            starttime=(1+nbreaks)*i*duration
            endtime=starttime+duration
            stem=audio[starttime:endtime].fade_in(fade).fade_out(fade)
            stemfilename="%s/stem-%03i.wav" % (destdirname, i)
            stem.export(stemfilename, format="wav")
        
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

    @parse_line()
    def do_randomise_pool(self):
        self.poolname=random.choice(list(self.pools.keys()))
        print ("INFO: pool=%s" % self.poolname)
        
if __name__=="__main__":
    pass
