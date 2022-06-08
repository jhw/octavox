import random, yaml

ModConfig=yaml.safe_load("""
modules:
  - name: Sampler
    # class: RVSampler
    class: SVSampler
    position:
      x: -3
      y: -1
  - name: Drum
    class: RVDrumSynth
    position:
      x: -3
      y: 1
  - name: Echo
    class: RVEcho
    position:
      x: -3
    defaults:
      dry: 128
      wet: 128
      delay: 192
  - name: Distortion
    class: RVDistortion
    position:
      x: -2
    defaults:
      power: 64
  - name: Reverb
    class: RVReverb
    position:
      x: -1
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

def random_grid(modnames, links):
    def calc_distance(modnames, links, grid):
        total=0
        for link in links:
            a, b = [grid[modnames.index(modname)]
                    for modname in link]
            distance=((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
            total+=distance
        return total
    grid=sorted([(x, y)
                 for y in range(len(modnames))
                 for x in range(len(modnames))],
                key=lambda x: random.random())
    distance=calc_distance(modnames, links, grid)
    return (grid[:len(modnames)], distance)

def generate(config, n):
    modnames=[mod["name"] for mod in config["modules"]]
    modnames.append(Output)
    items=sorted([random_grid(modnames, config["links"])
                  for i in range(n)],
                 key=lambda x: x[1])
    return items[0]
    
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
        print (grid)
        print (distance)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
