from octavox.modules import is_abbrev

from collections import OrderedDict

class SVPool(OrderedDict):

    def __init__(self, item={}):
        OrderedDict.__init__(self, item)        

    def clone(self):
        return SVPool(self)

    def add(self, samplekey):
        self[samplekey.full_key]=samplekey
    
    def filter(self, tag):
        pool=SVPool()
        for samplekey in self.values():
            for sktag in samplekey["tags"]:
                if tag==sktag:
                    pool.add(samplekey)
        return pool

    @property
    def samplekeys(self):
        return list(self.values())

    @property
    def tags(self):
        tags=set()
        for samplekey in self.values():
            for tag in samplekey["tags"]:
                tags.add(tag)
        return sorted(list(tags))
    
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
        
if __name__=="__main__":
    pass
