from octavox.modules.sampler import SVBanks

from octavox.projects.samplebeats.randomiser import SampleRandomiser, Profiles

from octavox.projects.samplebeats.dom import Patches

import datetime, random, yaml

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
        - key: degrade
          description: "degrade"
          type: float
          min: 0
          max: 1
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
          default: 16
        """)
        kwargs=cli(cliconf)
        banks=SVBanks.load("tmp/banks/pico")
        curated=yaml.safe_load(open("octavox/samples/banks/pico/curated.yaml").read())
        thresholds=Profiles[kwargs["profile"]]
        randomiser=SampleRandomiser(banks=banks,
                                    curated=curated,
                                    thresholds=thresholds)
        patches=Patches.randomise(randomiser=randomiser,
                                  slicetemp=kwargs["slicetemp"],
                                  degrade=kwargs["degrade"],
                                  n=kwargs["npatches"])
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-randomiser" % timestamp
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub=filestub)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
