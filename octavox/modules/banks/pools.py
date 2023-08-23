from octavox.modules import is_abbrev

import random, re

def parse_filename(sample):
    stem, ext = sample["file"].split(".")
    tokens=[tok for tok in stem.split(" ")
            if tok!=[]]
    root=" ".join([tok for tok in tokens
                  if not tok.startswith("#")])            
    tags=[tok for tok in tokens
          if tok.startswith("#")]
    return {"root": root,
            "tags": tags}

class SVPool(list):

    def __init__(self, items=[]):
        list.__init__(self, items)
        self.keys=[]
        self.groups={}

    def clone(self):
        return SVPool(self)

    def add(self, sample):
        key=str(sample)
        if key not in self.keys:
            self.append(sample)
            self.keys.append(key)
            params=parse_filename(sample)
            self.groups.setdefault(params["root"], {})
            for tag in params["tags"]:
                self.groups[params["root"]][tag]=sample
            
    def filter(self, tag):
        pool=SVPool()
        for sample in self:
            for sktag in sample["tags"]:
                if tag==sktag:
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
