from octavox.samples.banks.pico import PicoBanks

from octavox.projects.samplebeats.dom import Patches

from octavox.projects.samplebeats.tools import Profiles, Randomiser

import datetime, yaml
    
if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
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
        kwargs=cli(cliconf)
        banks=PicoBanks(root="tmp/banks/pico")
        profile=Profiles[kwargs["profile"]]
        randomiser=Randomiser(banks=banks,
                              profile=profile)
        patches=Patches.randomise(randomiser=randomiser,
                                  slicetemp=kwargs["slicetemp"],
                                  n=kwargs["npatches"])
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub=timestamp)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
