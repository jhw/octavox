import os, random, zipfile

Instruments="kk|sn|ht".split("|")

class Banks(dict):

    def __init__(self, root):
        dict.__init__(self)        
        for bankfile in os.listdir(root):
            path="%s/%s" % (root, bankfile)
            self[bankfile]=zipfile.ZipFile(path)

    def lookup(self, item):
        bankfile, wavfile = item
        return self[bankfile].open(wavfile, 'r')
            
class PoolBase:

    def __init__(self):
        pass

    def randomise(self, banks, instrument):
        return random.choice(self.mapping[instrument])
    
class SimplePool(PoolBase):

    def __init__(self, banks, bankfile, instruments=Instruments):
        PoolBase.__init__(self)
        samplekeys=[[bankfile, item.filename]
                    for item in banks[bankfile].infolist()]
        self.mapping={instrument:samplekeys
                      for instrument in instruments}

class CuratedPool(PoolBase):

    def __init__(self, banks, bankfile):
        PoolBase.__init__(self)
                        
if __name__=="__main__":
    def test_simple_pool(banks, bankfile="default.zip"):
        pool=SimplePool(banks, bankfile)
        item=pool.randomise(banks, "kk")        
        with open("tmp/%s" % item[1], 'wb') as f:
            f.write(banks.lookup(item).read())    
    banks=Banks("octavox/projects/picobeats/banks")
    test_simple_pool(banks)

