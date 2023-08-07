from octavox.modules import is_abbrev

from octavox.modules.sampler import SVBaseSampler

from rv.note import NOTE as RVNOTE

import os, re, yaml, zipfile

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

    def clone(self):
        return SVSampleKey({"tags": list(self["tags"]),
                            "bank": self["bank"],
                            "file": self["file"]})
        
    def __str__(self):
        tokens=[]
        tokens.append("%s/%s" % (self["bank"],
                                 self["file"]))
        if self["tags"]!=[]:
            tokens.append("[%s]" % ", ".join(sorted(self["tags"])))
        return " ".join(tokens)

class SVPool(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)        

    def clone(self):
        return SVPool(self)

    def lookup(self, tag):
        samplekeys=[]
        for samplekey in self.values():
            for sktag in samplekey["tags"]:
                if tag==sktag:
                    samplekeys.append(samplekey)
        return samplekeys
    
class SVPools(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def aggregate(self, suffix):
        parent=SVPool()
        for key, pool in self.items():
            if key.endswith(suffix):
                parent.update(pool)
        return parent

    def spawn_free(self):
        return self.aggregate("free")

    def spawn_curated(self):
        return self.aggregate("curated")

    def lookup(self, abbrev):
        matches=[]
        for key in self:
            if is_abbrev(abbrev, key):
                matches.append(key)
        if matches==[]:
            raise RuntimeError("pool not found")
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

    def lookup(self, abbrev):
        matches=[]
        for wavfile in self.wavfiles:
            if is_abbrev(abbrev, wavfile):
                matches.append(wavfile)
        if matches==[]:
            raise RuntimeError("wavfile not found")
        elif len(matches) > 1:
            raise RuntimeError("multiple wavfiles found")
        else:
            return matches.pop()
    
    def spawn_free(self, tags):
        pool, wavfiles = SVPool(), self.wavfiles
        for wavfile in wavfiles:
            for tag in tags:
                samplekey=SVSampleKey({"tags": [tag],
                                       "bank": self.name,
                                       "file": wavfile})
                pool[str(samplekey)]=samplekey
        return pool
    
    def spawn_curated(self,
                      tags,
                      fragments=Fragments):
        pool, wavfiles = SVPool(), self.wavfiles
        for wavfile in wavfiles:
            for tag in tags:
                for frag in fragments[tag]:
                    if re.search(frag, wavfile, re.I):
                        samplekey=SVSampleKey({"tags": [tag],
                                               "bank": self.name,
                                               "file": wavfile})
                        pool[str(samplekey)]=samplekey
        return pool

class SVBankSampler(SVBaseSampler):

    def __init__(self, samplekeys, banks, maxslots=120, *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        if len(samplekeys) > maxslots:
            raise RuntimeError("SVBankSampler max slots exceeded")
        self.samplekeys=samplekeys
        self.samplestrings=[str(samplekey)
                            for samplekey in samplekeys]
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        for i, samplekey in enumerate(self.samplekeys):
            self.note_samples[notes[i]]=i
            src=banks.get_wavfile(samplekey)
            self.load(src, i)
            sample=self.samples[i]
            sample.relative_note+=(root-i)

    def lookup(self, samplekey):
        return self.samplestrings.index(str(samplekey))
    
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
            raise RuntimeError("bank not found")
        elif len(matches) > 1:
            raise RuntimeError("multiple banks found")
        else:
            return matches.pop()
            
    def spawn_pools(self, tags=Fragments.keys()):
        pools=SVPools()
        for attr in ["free", "curated"]:
            for bankname, bank in self.items():
                bankfn=getattr(bank, "spawn_%s" % attr)
                key="%s-%s" % (bankname, attr)                
                pools[key]=bankfn(tags)
            poolsfn=getattr(pools, "spawn_%s" % attr)
            key="global-%s" % attr
            pools[key]=poolsfn()
        return pools

    def get_wavfile(self, samplekey):
        return self[samplekey["bank"]].zipfile.open(samplekey["file"], 'r')
    
if __name__=="__main__":
    banks=SVBanks("octavox/banks/pico")
    pools=banks.spawn_pools()
    for k, v in pools.items():
        print (k, len(v))
