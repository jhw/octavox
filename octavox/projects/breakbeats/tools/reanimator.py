from octavox.samples.banks import Banks

from octavox.projects.breakbeats.dom import Patches

import os, random, yaml

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
        banks=Banks.load("tmp/banks/pico")
        for filename in os.listdir("archive/breakbeats"):
            src="archive/breakbeats/%s" % filename
            patches=Patches(yaml.safe_load(open(src).read()))
            suffix="reanimator-%i" % int(random.random()*1e8)
            print ("%s -> %s" % (filename, suffix))
            patches.render(suffix=suffix,
                           banks=banks,
                           nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
