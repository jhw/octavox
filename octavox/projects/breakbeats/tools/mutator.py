from octavox.modules.sampler import SVBanks

from octavox.projects.breakbeats.dom import Patches

import datetime, yaml

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: src
          description: source
          type: file
          root: tmp/patches
        - key: index
          description: index
          type: int
          min: 0
          default: 0
        - key: dtrigstyle
          description: dtrigstyle
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dtrigseed
          description: dtrigseed
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dtrigpat
          description: dtrigpat
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dfxseed
          description: dfxseed
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
          default: 16
        """)
        import sys
        if len(sys.argv) >= 2:
            cliconf[0]["pattern"]=sys.argv[1]
        kwargs=cli(cliconf)
        roots=Patches(yaml.safe_load(open(kwargs["src"]).read()))
        if kwargs["index"] >= len(roots):        
            raise RuntimeError("index exceeds root patches length")
        root=roots[kwargs["index"]]
        def randomise_patch(patch, kwargs, i):
            for slice in patch["tracks"]["slices"]:
                for track in slice["trigs"]:
                    track.randomise_style(kwargs["dtrigstyle"])
                    track.randomise_seed(kwargs["dtrigseed"])
            patch["tracks"].randomise_pattern(kwargs["dtrigpat"])
            for effect in patch["effects"]:
                effect.randomise_seed(kwargs["dfxseed"])
            return patch
        modpatches=Patches([root if i==0 else randomise_patch(root.clone(), 
                                                              kwargs,
                                                              i)
                            for i in range(kwargs["npatches"])])
        banks=SVBanks.load("tmp/banks/pico")
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filename="%s-mutator" % timestamp
        modpatches.render(filename=filename,
                          banks=banks,
                          nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
