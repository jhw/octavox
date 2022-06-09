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

def init_layout(config, n=1000):
    class Grid(dict):
        @classmethod
        def randomise(self, modnames):
            sz=int(math.ceil(len(modnames)**0.5))
            coords=sorted([(x, y)
                           for y in range(sz)
                           for x in range(sz)],
                          key=lambda x: random.random())[:len(modnames)]
            return Grid({mod:xy
                         for mod, xy in zip(modnames, coords)})
        def __init__(self, item={}):
            dict.__init__(self, item)
        def rms_distance(self, links):
            total=0
            for link in links:
                a, b = [self[modname]
                        for modname in link]
                distance=((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
                total+=distance
            return total
        def normalise(self):
            return {k: tuple([v1-v0
                              for v1, v0 in zip(v, self["Output"])])
                    for k, v in self.items()}
    def randomise(modnames, links):
        grid=Grid.randomise(modnames)
        distance=grid.rms_distance(links)
        return (grid.normalise(), distance)
    modnames=[mod["name"] for mod in config["modules"]]
    modnames.append("Output")
    return sorted([randomise(modnames, config["links"])
                   for i in range(n)],
                  key=lambda x: -x[1]).pop()[0]
    
if __name__=="__main__":
    try:
        print (init_layout(ModConfig))
    except RuntimeError as error:
        print ("Error: %s" % str(error))
