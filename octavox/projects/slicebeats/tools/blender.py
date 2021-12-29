from octavox.modules.sampler import SVBanks

from octavox.projects.slicebeats.dom import Patches

import datetime, yaml

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: src
          description: source
          type: file
          root: tmp/patches
        - key: indexes
          description: indexes
          type: int_array
          min: 0
          default: 0
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        - key: npatches
          description: "n(patches)"
          type: int
          min: 1
          default: 32
        """)
        import sys
        if len(sys.argv) >= 2:
            cliconf[0]["pattern"]=sys.argv[1]
        kwargs=cli(cliconf)
        banks=SVBanks.load("tmp/banks/pico")
        patches=Patches(yaml.safe_load(open(kwargs["src"]).read()))
        for index in kwargs["indexes"]:
            if index >= len(patches):        
                raise RuntimeError("index exceeds root patches length")
        samples=patches.filter_samples(kwargs["indexes"])
        for patch in patches:
            for slice in patch["tracks"]["slices"]:
                slice["samples"].randomise_samples(samples)
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-blender" % timestamp
        patches.render(filestub=filestub,
                       banks=banks,
                       nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
