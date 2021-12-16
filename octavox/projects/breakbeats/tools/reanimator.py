from octavox.modules.sampler import SVBanks

from octavox.projects.breakbeats.dom import Patches

import os, yaml

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        """)
        kwargs=cli(cliconf)
        banks=SVBanks.load("tmp/banks/pico")
        for filename in sorted(os.listdir("archive/breakbeats")):
            src="archive/breakbeats/%s" % filename
            stub=filename.split(".")[0]
            print (stub)
            patches=Patches(yaml.safe_load(open(src).read()))
            patches.render(filename=stub,
                           banks=banks,
                           nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
