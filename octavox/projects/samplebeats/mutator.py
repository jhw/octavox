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

def decompile(patches, keys=["kk", "sn", "ht"]):
    def init_slice(slice, keys):
        machines=Machines([machine
                           for machine in slice["machines"]
                           if machine["key"] in keys])
        return Slice(samples=slice["samples"],
                     machines=machines)
    def init_patch(patch, keys):
        slices=Slices([init_slice(slice, keys)
                       for slice in patch["tracks"]["slices"]])
        patterns=PatternMap({k:v
                             for k, v in patch["tracks"]["patterns"].items()
                             if k in keys})
        tracks=Tracks(slices=slices,
                      patterns=patterns)
        return Patch(tracks=tracks)
    def decompile(patch, key):
        return [init_patch(patch, [key, "ec"])
                for key in keys]
    class Grid(list):
        def __init__(self, ncols, items=[]):
            list.__init__(self, items)
            self.ncols=ncols
        @property
        def nrows(self):
            return int(len(self)/self.ncols)
        def rotate(self):
            rotated=[]
            for j in range(self.ncols):
                for i in range(self.nrows):
                    k=j+i*self.ncols
                    rotated.append(self[k])
            return rotated
    decompiled=Grid(ncols=len(keys))
    for patch in patches:
        decompiled+=decompile(patch, keys)
    return Patches(decompiled.rotate())

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
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub="%s-mutator" % timestamp,
                       nbreaks=0)
        decompiled=decompile(patches)
        decompiled.render(banks=banks,
                          nbeats=kwargs["nbeats"],
                          filestub="%s-mutator-decompiled" % timestamp,
                          nbreaks=1)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
