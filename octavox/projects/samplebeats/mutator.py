from octavox.projects.samplebeats.dom import Machines, Slice, Slices, PatternMap, Tracks, Patch, Patches

from octavox.modules.sampler import SVBanks

import datetime, os, yaml

Profiles=yaml.safe_load("""
default:
  dtrigpat: 0.5
  dtrigseed: 0.5
  dtrigstyle: 0.5
""")

def randomise(patch, kwargs):
    patch["tracks"].randomise_pattern(kwargs["dtrigpat"],
                                      kwargs["slicetemp"])
    for slice in patch["tracks"]["slices"]:
        for track in slice["machines"]:
            track.randomise_style(kwargs["dtrigstyle"])
            track.randomise_seed(kwargs["dtrigseed"])
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
          default: default
        - key: slicetemp
          description: "slicetemp"
          type: float
          min: 0
          max: 1
          default: 1
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        - key: npatches
          description: "n(patches)"
          type: int
          min: 1
          default: 16
        - key: breaks
          description: "breaks?"
          type: bool
          default: false
        """)
        import sys
        if len(sys.argv) >= 2:
            cliconf[0]["pattern"]=sys.argv[1]
        kwargs=cli(cliconf)
        profilename=kwargs.pop("profile")
        kwargs.update(Profiles[profilename])
        roots=Patches(yaml.safe_load(open(kwargs["src"]).read()))
        if kwargs["index"] >= len(roots):        
            raise RuntimeError("index exceeds root patches length")
        root=roots[kwargs["index"]]       
        patches=Patches([root if i==0 else randomise(root.clone(), 
                                                     kwargs)
                         for i in range(kwargs["npatches"])])
        banks=SVBanks.load("tmp/banks/pico")
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        nbreaks=int(kwargs["breaks"])
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub="%s-mutator" % timestamp,
                       nbreaks=nbreaks)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
