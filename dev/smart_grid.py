import math, random, yaml

Output="Output"

class ModGrid(dict):

    @classmethod
    def all(self, sz):
        return [(x, y)
                for y in range(sz)
                for x in range(sz)]
    
    @classmethod
    def randomise(self, modnames):
        sz=int(math.ceil(len(modnames)**0.5))
        coords=sorted(ModGrid.all(sz),
                      key=lambda x: random.random())[:len(modnames)]
        return ModGrid(sz=sz,
                       item={mod:xy
                             for mod, xy in zip(modnames, coords)})
    
    def __init__(self, sz, item):
        dict.__init__(self, item)
        self.sz=sz

    def clone(self):
        return ModGrid(sz=self.sz,
                       item={k:v for k, v in self.items()})

    @property
    def allocated(self):
        return list(self.values())

    @property
    def unallocated(self):
        all, allocated = ModGrid.all(self.sz), self.allocated
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

ModConfig=yaml.safe_load("""
modules:
  - name: KKSampler
    classname: SVSampler
  - name: SNSampler
    classname: SVSampler
  - name: HTSampler
    classname: SVSampler
  - name: KKEqualiser
    classname: RVEqualiser
  - name: SNEqualiser
    classname: RVEqualiser
  - name: HTEqualiser
    classname: RVEqualiser
  - name: Echo
    classname: RVEcho
    defaults:
      dry: 256
      wet: 256
      delay: 192
  - name: Distortion
    classname: RVDistortion
    defaults:
      power: 64
  - name: Reverb
    classname: RVReverb
    defaults:
      wet: 4
links:
  - - KKSampler
    - KKEqualiser
  - - SNSampler
    - SNEqualiser
  - - HTSampler
    - HTEqualiser
  - - KKEqualiser
    - Echo
  - - SNEqualiser
    - Echo
  - - HTEqualiser
    - Echo
  - - Echo
    - Distortion
  - - Distortion
    - Reverb
  - - Reverb
    - Output
""")

def optimise(modnames, links, n=50):
    def shuffle(grid, links, q=3):
        clone=grid.clone()
        clone.shuffle(q)
        distance=clone.rms_distance(links)
        return (clone, distance)
    grid=ModGrid.randomise(modnames)
    best=grid.rms_distance(links)
    for i in range(n):
        clones=sorted([shuffle(grid, links)
                       for i in range(10)],
                      key=lambda x: -x[1])
        newgrid, newbest = clones[-1]
        if newbest < best:
            grid, best = newgrid, newbest
    print (best)
            
if __name__=="__main__":
    modnames=[Output]+[mod["name"]
                       for mod in ModConfig["modules"]]
    links=ModConfig["links"]
    optimise(modnames, links)
    
