from octavox.modules import is_abbrev

import os, random, re, yaml, zipfile

Fragments=yaml.safe_load("""
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

class SVSampleKey(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    @property
    def long_label(self):
        suffix=self["file"] if "file" in self else self["id"]
        return "%s/%s" % (self["bank"],
                          suffix)

    @property
    def short_label(self, n=2):
        suffix=self["file"][:n] if "file" in self else self["id"]
        return "%s/%s" % (self["bank"][:n],
                          suffix)
        
    def __str__(self):
        return self.long_label

class SVSampleKeys(list):

    def __init__(self, items=[]):
        list.__init__(self, [SVSampleKey(item)
                             for item in items])
    
class SVPool(dict):

    def __init__(self, item={}):
        dict.__init__(self, {k:SVSampleKeys(v)
                             for k, v in item.items()})

    def is_valid(self, limit=2):
        for items in self.values():
            if len(items) < limit:
                return False
        return True

    def clone(self):
        return SVPool(self)
    
    def add(self, pool):
        for key in pool:
            self.setdefault(key, [])
            for item in pool[key]:
                if item not in self[key]:
                    self[key].append(item)
        return self

    def randomise(self, instruments=Fragments.keys()):
        return {inst:random.choice(self[inst])
                for inst in instruments}

    @property
    def size(self):
        return sum([len(list(v))
                    for v in self.values()])
    
class SVPools(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def aggregate(self, suffix):
        parent=SVPool()
        for key, pool in self.items():
            if key.endswith(suffix):
                parent.add(pool)
        return parent

    def spawn_free(self):
        return self.aggregate("free")

    def spawn_curated(self):
        return self.aggregate("curated")

    def cull(self):
        pools=SVPools()
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
        
class SVBank:

    def __init__(self, name, zipfile):
        self.name=name
        self.zipfile=zipfile

    @property
    def wavfiles(self):
        return [item.filename
                for item in self.zipfile.infolist()]

    def spawn_free(self, instruments):
        wavfiles=self.wavfiles
        return SVPool({inst:[SVSampleKey({"bank": self.name,
                                          "file": wavfile})
                             for wavfile in wavfiles]
                       for inst in instruments})

    def spawn_curated(self,
                      instruments,
                      fragments=Fragments):
        pool, wavfiles = SVPool(), self.wavfiles
        for wavfile in wavfiles:
            for inst in instruments:
                pool.setdefault(inst, [])
                for frag in fragments[inst]:
                    if re.search(frag, wavfile, re.I):
                        pool[inst].append(SVSampleKey({"bank": self.name,
                                                       "file": wavfile}))
        return pool
                
class SVBanks(dict):

    def __init__(self, root):
        dict.__init__(self)        
        for bankfile in os.listdir(root):
            name=bankfile.split(".")[0]
            path="%s/%s" % (root, bankfile)
            bank=SVBank(name, zipfile.ZipFile(path))
            self[name]=bank

    def lookup(self, abbrev):
        matches=[]
        for key in self:
            if is_abbrev(abbrev, key):
                matches.append(key)
        if matches==[]:
            raise RuntimeError("no banks found")
        elif len(matches) > 1:
            raise RuntimeError("multiple banks found")
        else:
            return matches.pop()
            
    def spawn_pools(self, instruments=Fragments.keys()):
        pools=SVPools()
        for attr in ["free", "curated"]:
            for bankname, bank in self.items():
                bankfn=getattr(bank, "spawn_%s" % attr)
                key="%s-%s" % (bankname, attr)                
                pools[key]=bankfn(instruments)
            poolsfn=getattr(pools, "spawn_%s" % attr)
            key="global-%s" % attr
            pools[key]=poolsfn()
        return pools

    def get_wavfile(self, samplekey):
        return self[samplekey["bank"]].zipfile.open(samplekey["file"], 'r')
    
if __name__=="__main__":
    banks=SVBanks("octavox/banks/pico")
    pools=banks.spawn_pools().cull()
    print (pools.keys())
    print ()
    print (pools["global-curated"].randomise())
