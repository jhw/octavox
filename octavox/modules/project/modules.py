import math, random

class SVModGrid(dict):

    @classmethod
    def all(self, sz):
        offset=int(sz/2)
        return [(x-offset, y-offset)
                for y in range(sz)
                for x in range(sz)]
    
    @classmethod
    def randomise(self, modnames):
        sz=1+int(math.ceil(len(modnames)**0.5)) # NB +1 to ensure decent amount of whitespace in which to move cells around
        coords=sorted(SVModGrid.all(sz),
                      key=lambda x: random.random())[:len(modnames)]
        return SVModGrid(sz=sz,
                         item={mod:xy
                               for mod, xy in zip(modnames, coords)})
    
    def __init__(self, sz, item):
        dict.__init__(self, item)
        self.sz=sz

    def clone(self):
        return SVModGrid(sz=self.sz,
                         item={k:v for k, v in self.items()})

    @property
    def allocated(self):
        allocated=set(self.values())
        allocated.add((0, 0))
        return list(allocated)

    @property
    def unallocated(self):
        all, allocated = SVModGrid.all(self.sz), self.allocated
        return [xy for xy in all if xy not in allocated]

    def shuffle(self, n):
        keys, unallocated = list(self.keys()), self.unallocated
        for i in range(min(n, len(unallocated))):
            key=random.choice(keys)
            self[key]=unallocated[i]
        return self
    
    def rms_distance(self, links):
        total=0
        for link in links:
            a, b = [self[modname]
                    for modname in link]
            distance=((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
            total+=distance
        return total

if __name__=="__main__":
    pass
    
