from octavox.modules import is_abbrev, list_s3_keys

from octavox.modules.banks.pools import SVPool, SVPools

from octavox.modules.model import SVSampleKey

import io, os, re, yaml, zipfile

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
                pool.add(samplekey)
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
                        pool.add(samplekey)
        return pool

class SVBanks(dict):

    @classmethod
    def initialise(self,
                   s3,
                   bucketname,
                   prefix="banks",
                   cachedir="tmp/banks"):
        def list_existing(cachedir):
            existing=[]
            for item in os.listdir(cachedir):
                if item.endswith(".zip"):
                    bankname=item.split(".")[0]
                    existing.append(bankname)
            return sorted(existing)
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        s3keys, existing = (list_s3_keys(s3, bucketname, prefix),
                            list_existing(cachedir))
        banks={}
        for s3key in s3keys:
            bankname=s3key.split("/")[-1].split(".")[0]
            cachefilename="%s/%s.zip" % (cachedir, bankname)
            if bankname not in existing:
                print ("INFO: fetching %s" % s3key)
                buf=io.BytesIO(s3.get_object(Bucket=bucketname,
                                             Key=s3key)["Body"].read())
                with open(cachefilename, 'wb') as f:
                    f.write(buf.getvalue())
                zf=zipfile.ZipFile(buf, "r")
            else:
                zf=zipfile.ZipFile(cachefilename)
            bank=SVBank(bankname, zf)
            banks[bankname]=bank
        return SVBanks(banks)

    """
    - START TEMP CODE
    - because Gadlys wifi terrible
    """
    
    @classmethod
    def initialise(self,
                   s3,
                   bucketname,
                   prefix="banks",
                   cachedir="tmp/banks"):
        def list_existing(cachedir):
            existing=[]
            for item in os.listdir(cachedir):
                if item.endswith(".zip"):
                    bankname=item.split(".")[0]
                    existing.append(bankname)
            return sorted(existing)
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        existing=list_existing(cachedir)
        banks={}
        for bankname in existing:
            cachefilename="%s/%s.zip" % (cachedir, bankname)
            zf=zipfile.ZipFile(cachefilename)
            bank=SVBank(bankname, zf)
            banks[bankname]=bank
        return SVBanks(banks)

    """
    - END TEMP CODE
    - because Gadlys wifi terrible
    """

    def __init__(self, item={}):
        dict.__init__(self, item)
                    
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
