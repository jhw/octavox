from octavox.projects import is_abbrev

import os, random, re, yaml, zipfile

Instruments="kk|sn|oh|ch".split("|")

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
  - rim
  - plip
  - rs
oh:
  - open
  - hat
  - ht 
  - oh
  - perc
  - ussion
  - prc
ch:
  - closed
  - hat
  - ht 
  - " ch" # else will match glitch; but still matches chord unfortunately
  - perc
  - ussion
  - prc
""")

class Pool(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def is_valid(self, limit=2):
        for items in self.values():
            if len(items) < limit:
                return False
        return True

    def clone(self):
        return Pool(self)
    
    def add(self, pool):
        for key in pool:
            self.setdefault(key, [])
            self[key]+=pool[key]
        return self

    def randomise(self, instruments=Instruments):
        return {inst:random.choice(self[inst])
                for inst in instruments}

    @property
    def size(self):
        return sum([len(list(v))
                    for v in self.values()])
    
class Pools(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def aggregate(self, suffix):
        parent=Pool()
        for key, pool in self.items():
            if key.endswith(suffix):
                parent.add(pool)
        return parent

    def spawn_free(self):
        return self.aggregate("free")

    def spawn_curated(self):
        return self.aggregate("curated")

    def cull(self):
        pools=Pools()
        for k, v in self.items():
            if v.is_valid():
                pools[k]=v
        return pools

    def lookup(self, abbrev):
        matches=[]
        for key in self:
            if is_abbrev(abbrev, key):
                matches.append(key)
        if matches==[]:
            raise RuntimeError("no pools found")
        elif len(matches) > 1:
            raise RuntimeError("multiple pools found")
        else:
            return matches.pop()
        
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
                        # break
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
        pools=Pools()
        for attr in ["free", "curated"]:
            for bankname, bank in self.items():
                bankfn=getattr(bank, "spawn_%s" % attr)
                key="%s-%s" % (bankname, attr)
                pools[key]=bankfn()
            poolsfn=getattr(pools, "spawn_%s" % attr)
            key="global-%s" % attr
            pools[key]=poolsfn()
        return pools

    def get_wavfile(self, item):
        bankfile, wavfile = item
        return self[bankfile].zipfile.open(wavfile, 'r')
    
if __name__=="__main__":
    banks=Banks("octavox/projects/picobeats/banks")
    pools=banks.spawn_pools().cull()
    print (pools.keys())
    print ()
    print (pools["global-curated"].randomise())
