from octavox.modules.sampler import SVBanks

from octavox.projects.samplebeats.dom import Patches

import datetime, random, yaml

Profiles=yaml.safe_load("""
default:
  kk: 0.8
  sn: 0.8
  oh: 0.5
  ch: 0.5
strict:
  kk: 0.9
  sn: 1.0
  oh: 0.8
  ch: 0.8
wild:
  kk: 0.4
  sn: 0.4
  oh: 0.2
  ch: 0.2
""")

class Randomiser:

    def __init__(self, banks, curated, profile):
        self.banks=banks
        self.curated=curated
        self.profile=profile

    def random_kk(self):
        q=random.random()
        if q < self.profile["kk"]:
            return random.choice(self.curated["kick"]+self.curated["bass"])    
        else:
            return self.banks.random_key

    def random_sn(self):
        q=random.random()
        if q < self.profile["sn"]:
            return random.choice(self.curated["clap"]+self.curated["snare"])
        else:
            return self.banks.random_key

    def random_oh(self):
        q=random.random()
        if q < self.profile["oh"]:
            return random.choice(self.curated["hat"]+self.curated["perc"])    
        else:
            return self.banks.random_key

    def random_ch(self):
        q=random.random()
        if q < self.profile["ch"]:
            return random.choice(self.curated["hat"]+self.curated["perc"])    
        else:
            return self.banks.random_key

    def randomise(self,
                  keys="kk|sn|oh|ch".split("|")):
        return {key: getattr(self, "random_%s" % key)()
                for key in keys}

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
          default: 16
        """)
        kwargs=cli(cliconf)
        banks=SVBanks.load("tmp/banks/pico")
        curated=yaml.safe_load(open("octavox/samples/banks/pico/curated.yaml").read())
        profile=Profiles[kwargs["profile"]]
        randomiser=Randomiser(banks=banks,
                              curated=curated,
                              profile=profile)
        patches=Patches.randomise(randomiser=randomiser,
                                  slicetemp=kwargs["slicetemp"],
                                  n=kwargs["npatches"])
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-randomiser" % timestamp
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filestub=filestub)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
