from octavox.modules import is_abbrev

import random

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
            for sktag in sample["tags"]:
                if tag==sktag:
                    pool.add(sample)
        return pool

"""
- any kind of sample manipulation (cutoff, slice) can only be stored as a separate item within a bank's zipfile; ie it's a very flat structure
- convention for a slice filename is to take the root stem followed by one or more tags, which start with a hash; eg #cutoff-500, #slice-1-8
- can split on these filename structures to cluster sliced versions under stems
"""
    
class SVSamplePool(SVPool):

    def __init__(self, *args, **kwargs):
        SVPool.__init__(self, *args, **kwargs)
        self.init_groups()

    def init_groups(self):
        groups={}
        for sample in self:
            stem, ext = sample["file"].split(".")
            tokens=[tok for tok in stem.split(" ")
                    if tok!=[]]
            key=" ".join([tok for tok in tokens
                          if not tok.startswith("#")])            
            tags=[tok for tok in tokens
                  if tok.startswith("#")]
            groups.setdefault(key, {})
            for tag in tags:
                groups[key][tag]=sample
        self.groups=groups

    def random_stem(self):
        return random.choice(list(self.groups.keys()))

    def random_slice(self, stem):
        return random.choice(list(self.groups[stem].values()))
    
class SVPools(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def aggregate(self, suffix):
        parent=SVPool()
        for key, pool in self.items():
            if key.endswith(suffix):
                parent+=pool
        return parent

    def spawn_free_pool(self):
        return self.aggregate("free")

    def spawn_curated_pool(self):
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
