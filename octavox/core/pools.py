from octavox.core import is_abbrev

import re

def sample_default_kwargs(fn):
    def wrapped(self, item):
        for attr, defaultval in [("tags", [])]:
            if attr not in item:
                item[attr]=defaultval
        return fn(self, item)
    return wrapped

class SVSample(dict):

    @sample_default_kwargs
    def __init__(self, item):
        dict.__init__(self, item)

    def clone(self):
        kwargs={"bank": self["bank"],
                "file": self["file"],
                "tags": list(self["tags"])}
        return SVSample(kwargs)

    @property
    def has_tags(self):
        return self["tags"]!=[]
    
    def add_tag(self, tag):
        if tag not in self["tags"]:
            self["tags"].append(tag)

    @property
    def tagstr(self):
        return "[%s]" % ", ".join(sorted(self["tags"]))

    def __str__(self):
        tokens=[]
        tokens.append("%s/%s" % (self["bank"],
                                 self["file"])),
        if self.has_tags:
            tokens.append(self.tagstr)
        return " ".join(tokens)

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
            
    def filter_tag(self, tag):
        pool=SVPool()
        for sample in self:
            for stag in sample["tags"]:
                if tag==stag:
                    pool.add(sample)
        return pool

class SVPools(dict):

    def __init__(self, item={}):
        dict.__init__(self, item)

    def flatten(self):
        flattened=SVPool()
        for poolname, pool in self.items():            
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
