from octavox.projects.samplebeats.dom import Machines, Slice, Slices, PatternMap, Tracks, Patch, Patches

from octavox.projects.samplebeats.randomiser import SampleRandomiser, Profiles

from octavox.modules.sampler import SVBanks

import datetime, json, os, yaml

def randomise(patch, kwargs, randomiser):
    samples=randomiser.randomise()
    for slice in patch["tracks"]["slices"]:
        slice["samples"].randomise_samples(kwargs["dsample"],
                                           samples)
    patch["tracks"].randomise_pattern(kwargs["dpat"],
                                      kwargs["slicetemp"])
    patch["tracks"].randomise_mutes(kwargs["dmute"])
    for slice in patch["tracks"]["slices"]:
        for machine in slice["machines"]:
            machine.randomise_style(kwargs["dstyle"])
            machine.randomise_seed(kwargs["dseed"])
    return patch

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
          type: int  
          min: 0
          default: 0
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
        - key: dsample
          description: "d(sample)"
          type: float
          min: 0
          max: 1
          default: 0.2
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
        banks=SVBanks.load("tmp/banks/pico")
        curated=yaml.safe_load(open("octavox/samples/banks/pico/curated.yaml").read())
        thresholds=Profiles[kwargs["profile"]]
        randomiser=SampleRandomiser(banks=banks,
                                    curated=curated,
                                    thresholds=thresholds)
        roots=Patches(json.loads(open(kwargs["src"]).read()))
        if kwargs["index"] >= len(roots):        
            raise RuntimeError("index exceeds root patches length")
        root=roots[kwargs["index"]]    
        patches=Patches([root if i==0 else randomise(root.clone(), 
                                                     kwargs,
                                                     randomiser)
                         for i in range(kwargs["npatches"])])
        banks=SVBanks.load("tmp/banks/pico")
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub="%s-mutator" % timestamp)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
