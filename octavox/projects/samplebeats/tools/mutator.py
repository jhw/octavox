from octavox.projects.samplebeats.dom import Machines, Slice, Slices, PatternMap, Tracks, Patch, Patches

from octavox.modules.sampler import SVBanks

import datetime, json, os, yaml

def randomise_patch(patch, kwargs):
    patch["tracks"].randomise_pattern(kwargs["dpat"],
                                      kwargs["slicetemp"])
    patch["tracks"].randomise_mutes(kwargs["dmute"])
    for slice in patch["tracks"]["slices"]:
        for machine in slice["machines"]:
            machine.randomise_style(kwargs["dstyle"])
            machine.randomise_seed(kwargs["dseed"])
    return patch

def randomise_patches(roots, kwargs):
    index=kwargs["index"]
    patches=[]
    for j in range(kwargs["npatches"]):
        i=index[j % len(index)]
        if i > len(roots):
            raise RuntimeError("index %i exceeds root patches length [%i]" % (i, len(roots)))
        root=roots[i]
        patch=root.clone() if j < len(index) else randomise_patch(root.clone(),
                                                                  kwargs)
        patches.append(patch)
    return Patches(patches)

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: src
          description: source
          type: file
          root: tmp/samplebeats/patches
        - key: index
          description: index
          type: intarray  
          default: [0]
          min: 0
        - key: profile
          description: "profile"
          type: enum
          options:
          - default
          - strict
          - wild
          default: default
        - key: slicetemp
          description: "slicetemp"
          type: float
          min: 0
          max: 1
          default: 1
        - key: dpat
          description: "d(pat)"
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dmute
          description: "d(mute)"
          type: float
          min: 0
          max: 1
          default: 0.2
        - key: dseed
          description: "d(seed)"
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dstyle
          description: "d(style)"
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        - key: npatches
          description: "n(patches)"
          type: int
          min: 1
          default: 64
        """)
        kwargs=cli(cliconf)
        roots=Patches(json.loads(open(kwargs["src"]).read()))
        patches=randomise_patches(roots, kwargs)
        banks=SVBanks.load("tmp/banks/pico")
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub="%s-mutator" % timestamp)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
