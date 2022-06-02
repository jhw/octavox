from octavox.modules.sampler import SVBanks

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

import random, yaml

class SampleRandomiser:

    SVDrum= "svdrum"

    def svdrum(offsets, n=10):
        return ["svdrum:%i" % (i*12+j)
                for i in range(n)
                for j in offsets]

    SVDrumBass=svdrum(range(4))
    SVDrumHats=svdrum(range(4, 7))

    def __init__(self, banks, curated, thresholds):
        self.banks=banks
        self.curated=curated
        self.thresholds=thresholds

    def random_wild(self):
        modnames=[self.SVDrum]+list(self.banks.keys())
        mod=random.choice(modnames)
        n=len(self.banks[mod].infolist()) if mod!=self.SVDrum else 120
        i=random.choice(range(n))
        return "%s:%i" % (mod, i)

    def random_kk(self):
        q=random.random()
        if q < self.thresholds["kksvdrum"]:
            return random.choice(self.SVDrumBass)
        elif q < self.thresholds["kksvdrum"]+self.thresholds["kksamples"]:
            return random.choice(self.curated["kick"]+self.curated["bass"])    
        else:
            return self.random_wild()

    def random_sn(self):
        q=random.random()
        if q < self.thresholds["snsamples"]:
            return random.choice(self.curated["snare"])
        elif q < self.thresholds["snsamples"]+self.thresholds["cpsamples"]:
            return random.choice(self.curated["clap"])
        else:
            return self.random_wild()

    def random_oh(self):
        q=random.random()
        if q < self.thresholds["ohsvdrum"]:
            return random.choice(self.SVDrumHats)
        elif q< self.thresholds["ohsvdrum"]+self.thresholds["ohsamples"]:
            return random.choice(self.curated["hat"]+self.curated["perc"])    
        else:
            return self.random_wild()

    def random_ch(self):
        q=random.random()
        if q < self.thresholds["chsvdrum"]:
            return random.choice(self.SVDrumHats)
        elif q< self.thresholds["chsvdrum"]+self.thresholds["chsamples"]:
            return random.choice(self.curated["hat"]+self.curated["perc"])    
        else:
            return self.random_wild()        

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
        - key: breaks
          description: "breaks?"
          type: bool
          default: false
        """)
        import sys
        if len(sys.argv) >= 2:
            cliconf[0]["pattern"]=sys.argv[1]
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
                                  randomisers=randomisers,
                                  slicetemp=kwargs["slicetemp"],
                                  n=npatches)
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-randomiser" % timestamp
        nbreaks=int(kwargs["breaks"])
        patches.render(banks=banks,
                       nbeats=nbeats,
                       filestub=filestub,
                       nbreaks=nbreaks)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
