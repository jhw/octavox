from octavox.samples.banks.pico import PicoBanks

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

    def __init__(self, banks, profile):
        self.banks=banks
        self.profile=profile

    @property
    def random_kk(self):        
        return self.banks.random_kk if random.random() < self.profile["kk"] else self.banks.random_key

    @property
    def random_sn(self):
        return self.banks.random_sn if random.random() < self.profile["sn"] else self.banks.random_key

    @property
    def random_oh(self):
        return self.banks.random_ht if random.random() < self.profile["oh"] else self.banks.random_key

    @property
    def random_ch(self):
        return self.banks.random_ht if random.random() < self.profile["ch"] else self.banks.random_key

    def randomise(self,
                  keys="kk|sn|oh|ch".split("|")):
        return {key: getattr(self, "random_%s" % key)
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
        banks=PicoBanks(root="tmp/banks/pico")
        profile=Profiles[kwargs["profile"]]
        randomiser=Randomiser(banks=banks,
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
