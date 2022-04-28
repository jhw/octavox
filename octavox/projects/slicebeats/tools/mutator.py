from octavox.modules.sampler import SVBanks

from octavox.projects.slicebeats.dom import Patches

import datetime, yaml

Profiles=yaml.safe_load("""
default:
  dfxseed: 0.5
  dtrigpat: 0.5
  dtrigseed: 0.5
  dtrigstyle: 0.5
""")

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: src
          description: source
          type: file
          root: tmp/slicebeats/patches
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
        def randomise_patch(patch, kwargs, i):
            patch["tracks"].randomise_pattern(kwargs["dtrigpat"])
            for slice in patch["tracks"]["slices"]:
                for track in slice["machines"]:
                    track.randomise_style(kwargs["dtrigstyle"])
                    track.randomise_seed(kwargs["dtrigseed"])
            for effect in patch["effects"]:
                effect.randomise_seed(kwargs["dfxseed"])
            return patch
        modpatches=Patches([root if i==0 else randomise_patch(root.clone(), 
                                                              kwargs,
                                                              i)
                            for i in range(kwargs["npatches"])])
        banks=SVBanks.load("tmp/banks/pico")
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-mutator" % timestamp
        modpatches.render(filestub=filestub,
                          banks=banks,
                          nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
