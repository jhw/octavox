import math, random, yaml

ModConfig=yaml.safe_load("""
modules:
  - name: Sampler
    # class: RVSampler
    class: SVSampler
  - name: Drum
    class: RVDrumSynth
  - name: Echo
    class: RVEcho
    defaults:
      dry: 128
      wet: 128
      delay: 192
  - name: Distortion
    class: RVDistortion
    defaults:
      power: 64
  - name: Reverb
    class: RVReverb
    defaults:
      wet: 4
links:
  - - Sampler
    - Echo
  - - Drum
    - Echo
  - - Echo
    - Distortion
  - - Distortion
    - Reverb
  - - Reverb
    - Output
""")

Output="Output"

class Grid(list):

    @classmethod
    def randomise(self, modnames):
        sz=int(math.ceil(len(modnames)**0.5))
        coords=sorted([(x, y)
                       for y in range(sz)
                       for x in range(sz)],
                      key=lambda x: random.random())[:len(modnames)]
        return Grid(modnames, coords)

    def __init__(self, modnames, coords=[]):
        list.__init__(self, coords)
        self.modnames=modnames

    def rms_distance(self, links):
        total=0
        for link in links:
            a, b = [self[self.modnames.index(modname)]
                    for modname in link]
            distance=((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
            total+=distance
        return total

def generate(config, n):
    def randomise(modnames, links):
        grid=Grid.randomise(modnames)
        distance=grid.rms_distance(links)
        return (grid, distance)
    modnames=[mod["name"] for mod in config["modules"]]
    modnames.append(Output)
    grids=sorted([randomise(modnames, config["links"])
                  for i in range(n)],
                 key=lambda x: x[1])
    return grids[0]
    
if __name__=="__main__":
    try:
        import re, sys
        if len(sys.argv) < 2:
            raise RuntimeError("please enter n")
        n=sys.argv[1]
        if not re.search("^\\d+$|", n):
            raise RuntimeError("n is invalid")
        n=int(n)        
        grid, distance = generate(ModConfig, n)
        print (grid.modnames)
        print (grid)
        print (distance)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
