from octavox.modules.sampler import SVBanks

from octavox.modules.sample_randomiser import SampleRandomiser, Profiles

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
        - key: kk
          description: "kk?"
          type: bool
          default: true
        - key: sn
          description: "sn?"
          type: bool
          default: true
        - key: ht
          description: "ht?"
          type: bool
          default: true
        - key: ec
          description: "ec?"
          type: bool
          default: true
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
        keys=[k for k in "kk|sn|ht|ec".split("|")
              if k in kwargs and kwargs[k]]
        patches=Patches.randomise(keys=keys,
                                  mutes=[],
                                  randomiser=randomiser,
                                  slicetemp=kwargs["slicetemp"],
                                  n=kwargs["npatches"])
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-randomiser" % timestamp
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub=filestub)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
