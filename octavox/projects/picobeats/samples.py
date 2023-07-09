import os, random, re, yaml, zipfile

Instruments="kk|sn|ht".split("|")

Patterns=yaml.safe_load("""
kk:
  - kick
  - kik
  - kk
  - bd
  - bass
sn:
  - snare
  - sn
  - sd
  - clap
  - clp
  - cp
  - hc
ht:
  - open
  - closed
  - hat
  - ht 
  - oh
  - " ch" # else will match glitch
  - perc
  - prc
""")

class Pool(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def is_valid(self, limit=4):
        for items in self.values():
            if len(items) < limit:
                return False
        return True

class Pools(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)
    
class Bank:

    def __init__(self, name, zipfile):
        self.name=name
        self.zipfile=zipfile

    @property
    def wavfiles(self):
        return [item.filename
                for item in self.zipfile.infolist()]

    def spawn_free(self, instruments=Instruments):
        wavfiles=self.wavfiles
        return Pool({inst:[[self.name, wavfile]
                          for wavfile in wavfiles]
                     for inst in instruments})

    def spawn_curated(self,
                      instruments=Instruments,
                      patterns=Patterns):
        pool, wavfiles = Pool(), self.wavfiles
        for wavfile in wavfiles:
            for inst in Instruments:
                pool.setdefault(inst, [])
                for pat in patterns[inst]:
                    if re.search(pat, wavfile, re.I):
                        pool[inst].append([self.name, wavfile])
                        break
        return pool
                
class Banks(dict):

    def __init__(self, root):
        dict.__init__(self)        
        for bankfile in os.listdir(root):
            name=bankfile.split(".")[0]
            path="%s/%s" % (root, bankfile)
            bank=Bank(name, zipfile.ZipFile(path))
            self[name]=bank

    def spawn_pools(self):
        pools={}
        for bankname, bank in self.items():
            for attr in ["free", "curated"]:
                poolfn=getattr(bank, "spawn_%s" % attr)
                key="%s-%s" % (bankname, attr)
                pools[key]=poolfn()
        return pools
                            
if __name__=="__main__":
    banks=Banks("octavox/projects/picobeats/banks")
    pools=banks.spawn_pools()
    print (pools.keys())
