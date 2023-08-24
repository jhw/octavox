from octavox.modules import is_abbrev

import random, re, urllib.parse

def sample_default_kwargs(fn):
    def wrapped(self, item):
        for attr, defaultval in [("pitch", 0),
                                 ("tags", [])]:
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
                "pitch": self["pitch"],
                "tags": list(self["tags"])}
        if ("mod" in self and
            "ctrl" in self):
            kwargs["mod"]=self["mod"]
            kwargs["ctrl"]=dict(kwargs["ctrl"])
        return SVSample(kwargs)

    @property
    def has_mod(self):
        return "mod" in self and "ctrl" in self
            
    @property
    def has_tags(self):
        return self["tags"]!=[]
    
    def add_tag(self, tag):
        if tag not in self["tags"]:
            self["tags"].append(tag)

    @property
    def pitchstr(self):
        fmtstr="(+%i)" if self["pitch"] > 0 else "(%i)"
        return fmtstr % self["pitch"]

    @property
    def modstr(self):
        return "#%s?%s" % (self["mod"],
                           urllib.parse.urlencode(self["ctrl"]))
    
    @property
    def tagstr(self):
        return "[%s]" % ", ".join(sorted(self["tags"]))

    def __str__(self):
        tokens=[]
        tokens.append("%s/%s" % (self["bank"],
                                 self["file"])),
        tokens.append(self.pitchstr)
        if self.has_mod: 
            tokens.append(self.modstr)
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
