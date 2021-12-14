from octavox.samples.banks import Banks

from octavox.projects.breakbeats.dom import Patches

import yaml

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: src
          description: source
          type: file
          root: archive/breakbeats
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        """)
        kwargs=cli(cliconf)
        patches=Patches(yaml.safe_load(open(kwargs["src"]).read()))
        banks=Banks.load("tmp/banks/pico")
        patches.render(enginename="dearchiver",
                       banks=banks,
                       nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
