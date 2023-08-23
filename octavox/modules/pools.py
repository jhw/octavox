from octavox.modules import is_abbrev

import random, re

class SVPool(list):

    def __init__(self, items=[]):
        list.__init__(self, items)
        self.keys=[]

    def clone(self):
        return SVPool(self)

    def add(self, sample):
        key=str(sample)
        if key not in self.keys:
            self.append(sample)
            self.keys.append(key)
            
    def filter(self, tag):
        pool=SVPool()
        for sample in self:
            for stag in sample["tags"]:
                if tag==stag:
                    pool.add(sample)
        return pool

class SVPools(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def flatten(self, term):
        flattened=SVPool()
        for key, pool in self.items():
            if re.search(term, key):
                flattened+=pool
        return flattened
        
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
