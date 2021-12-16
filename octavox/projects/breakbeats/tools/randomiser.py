from octavox.modules.sampler import SVBanks

from octavox.projects.breakbeats.dom import Patches

from octavox.projects.breakbeats.trigs import Channels, Instruments

import random, yaml

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
                  instruments=Instruments,
                  channels=Channels):
        return {instrument: getattr(self, "random_%s" % instrument)()
                for instrument in instruments}

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: kksvdrum
          description: "svdrum(kk)"
          type: float
          min: 0
          max: 1
          default: 0.45
        - key: kksamples
          description: "samples(kk)"
          type: float
          min: 0
          max: 1
          default: 0.45
        - key: snsamples
          description: "samples(sn)"
          type: float
          min: 0
          max: 1
          default: 0.45
        - key: cpsamples
          description: "samples(cp)"
          type: float
          min: 0
          max: 1
          default: 0.45
        - key: ohsvdrum
          description: "svdrum(oh)"
          type: float
          min: 0
          max: 1
          default: 0.25
        - key: ohsamples
          description: "samples(oh)"
          type: float
          min: 0
          max: 1
          default: 0.25
        - key: chsvdrum
          description: "svdrum(ch)"
          type: float
          min: 0
          max: 1
          default: 0.25
        - key: chsamples
          description: "samples(ch)"
          type: float
          min: 0
          max: 1
          default: 0.25
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
        curated=yaml.safe_load(open("octavox/projects/breakbeats/pico-curated.yaml").read())
        npatches, nbeats = kwargs.pop("npatches"), kwargs.pop("nbeats")
        randomisers={"samples": SampleRandomiser(banks=banks,
                                                 curated=curated,
                                                 thresholds=kwargs)}
        patches=Patches.randomise(controllers=Controllers,
                                  randomisers=randomisers,
                                  n=npatches)
        patches.render(suffix="randomiser",
                       banks=banks,
                       nbeats=nbeats)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
