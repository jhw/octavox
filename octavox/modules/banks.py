from octavox import has_internet

from octavox.modules import is_abbreSSv, list_s3_keys

from octavox.modules.pools import SVPool, SVPools

from octavox.modules.model import SVSample

from pydub import AudioSegment

import io, os, re, zipfile

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

    @property
    def default_pool(self):
        pool, wavfiles = SVPool(), self.wavfiles
        for wavfile in wavfiles:
            stem, ext = wavfile.split(".")
            sample=SVSample({"bank": self.name,
                             "stem": stem,
                             "ext": ext})
            pool.add(sample)
        return pool

    def curate_pool(self, terms):
        pool, wavfiles = SVPool(), self.wavfiles
        for wavfile in wavfiles:
            stem, ext = wavfile.split(".")
            for tag, _terms in terms.items():
                for term in _terms:
                    if re.search(term, wavfile, re.I):
                        sample=SVSample({"bank": self.name,
                                         "stem": stem,
                                         "ext": ext,
                                         "tags": [tag]})
                        pool.add(sample)
        return pool

def list_cached(cachedir):
    if not os.path.exists(cachedir):
            os.makedirs(cachedir)
    cached=[]
    for item in os.listdir(cachedir):
        if item.endswith(".zip"):
            bankname=item.split(".")[0]
            cached.append(bankname)
    return sorted(cached)

class SVBanks(dict):

    @classmethod
    def initialise_online(self,
                          s3,
                          bucketname,
                          prefix="banks",
                          cachedir="tmp/banks"):
        s3keys, cached = (list_s3_keys(s3, bucketname, prefix),
                          list_cached(cachedir))
        banks={}
        for s3key in s3keys:
            bankname=s3key.split("/")[-1].split(".")[0]
            cachefilename="%s/%s.zip" % (cachedir, bankname)
            if bankname not in cached:
                print ("INFO: fetching %s" % s3key)
                buf=io.BytesIO(s3.get_object(Bucket=bucketname,
                                             Key=s3key)["Body"].read())
                with open(cachefilename, 'wb') as f:
                    f.write(buf.getvalue())
                zf=zipfile.ZipFile(buf, "r")
            else:
                zf=zipfile.ZipFile(cachefilename)
            bank=SVBank(name=bankname,
                        zipfile=zf)
            banks[bankname]=bank
        return SVBanks(banks)

    @classmethod
    def initialise_offline(self,
                           s3,
                           bucketname,
                           prefix="banks",
                           cachedir="tmp/banks"):
        cached=list_cached(cachedir)
        banks={}
        for bankname in cached:
            cachefilename="%s/%s.zip" % (cachedir, bankname)
            zf=zipfile.ZipFile(cachefilename)
            bank=SVBank(name=bankname,
                        zipfile=zf)
            banks[bankname]=bank
        return SVBanks(banks)

    @classmethod
    def initialise(self, s3, bucketname):
        suffix="online" if has_internet() else "offline"
        banksfn=getattr(SVBanks, "initialise_%s" % suffix)
        return banksfn(s3, bucketname)
        
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
            
    def get_wavfile(self, sample):
        return self[sample["bank"]].zipfile.open(sample.filename, 'r')
    
if __name__=="__main__":
    pass
