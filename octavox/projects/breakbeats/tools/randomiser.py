from octavox.samples.banks import Banks

from octavox.projects.breakbeats.dom import Patches

import yaml

Controllers=yaml.safe_load("""
- mod: Echo
  attr: wet
  kwargs:
    sample_hold:
      step: 4
      max: 0.75
- mod: Echo
  attr: feedback
  kwargs:
    sample_hold:
      step: 4
      max: 0.75
""")

if __name__=="__main__":
    try:
        from cli import cli
        cliconf=yaml.safe_load("""
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
        kwargs=cli(cliconf)
        banks=Banks.load("tmp/banks/pico")
        samples=yaml.safe_load(open("samples.yaml").read())
        patches=Patches.randomise(banks=banks,
                                  samples=samples,
                                  controllers=Controllers,
                                  n=kwargs["npatches"])
        patches.render(enginename="randomiser",
                       banks=banks,
                       nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
