import os, random, zipfile

Instruments="kk|sn|ht".split("|")

class Pool(dict):

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

    def spawn_free(self, keys=Instruments):
        wavfiles=self.wavfiles
        return Pool({key:wavfiles
                     for key in keys})

    def spawn_curated(self, patterns=Patterns):
        pool, wavfiles = Pool(), self.wavfiles
        for key in Instruments:
            pool.setdefault(key, [])
            for wavfile in wavfiles:
                if matches(wavfiles, patterns[key]):
                    pool[key].append(wavfile)
        return pool
                
class Banks(dict):

    def __init__(self, root):
        dict.__init__(self)        
        for bankfile in os.listdir(root):
            name=bankfile.split(".")[0]
            path="%s/%s" % (root, bankfile)
            bank=Bank(name, zipfile.ZipFile(path))
            self[name]=bank

    def lookup(self, item):
        bankfile, wavfile = item
        return self[bankfile].open(wavfile, 'r')

if __name__=="__main__":
    banks=Banks("octavox/projects/picobeats/banks")
    print (banks["default"].spawn_free())
