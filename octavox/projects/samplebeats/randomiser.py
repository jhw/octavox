from octavox.modules.sampler import SVBanks

from octavox.modules.sample_randomiser import SampleRandomiser

from octavox.projects.samplebeats.dom import Patches

import datetime, random, yaml

Profiles=yaml.safe_load("""
default:
  kksamples: 0.5
  kksvdrum: 0.3
  snsamples: 0.4
  cpsamples: 0.4
  ohsamples: 0.25
  ohsvdrum: 0.25
  chsamples: 0.25
  chsvdrum: 0.25
strict:
  kksamples: 0.65
  kksvdrum: 0.35
  snsamples: 0.5
  cpsamples: 0.5
  ohsamples: 0.4
  ohsvdrum: 0.4
  chsamples: 0.4
  chsvdrum: 0.4
wild:
  kksamples: 0.25
  kksvdrum: 0.15
  snsamples: 0.2
  cpsamples: 0.2
  ohsamples: 0.1
  ohsvdrum: 0.1
  chsamples: 0.1
  chsvdrum: 0.1
""")

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
        profilename=kwargs.pop("profile")
        kwargs.update(Profiles[profilename])
        banks=SVBanks.load("tmp/banks/pico")
        curated=yaml.safe_load(open("octavox/samples/banks/pico/curated.yaml").read())
        npatches, nbeats = kwargs.pop("npatches"), kwargs.pop("nbeats")
        randomisers={"samples": SampleRandomiser(banks=banks,
                                                 curated=curated,
                                                 thresholds=kwargs)}
        keys=[k for k in "kk|sn|ht|ec".split("|")
              if k in kwargs and kwargs[k]]
        patches=Patches.randomise(keys=keys,
                                  mutes=[],
                                  randomisers=randomisers,
                                  slicetemp=kwargs["slicetemp"],
                                  n=npatches)
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-randomiser" % timestamp
        patches.render(banks=banks,
                       nbeats=nbeats,
                       filestub=filestub)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
