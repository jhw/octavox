from octavox.modules.sampler import SVBanks

from octavox.projects.slicebeats.dom import Patches

from octavox.projects.slicebeats.trigs import Channels, Instruments

import datetime, random, yaml

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

Profiles=yaml.safe_load("""
default:
  chsamples: 0.25
  chsvdrum: 0.25
  cpsamples: 0.45
  kksamples: 0.6
  kksvdrum: 0.3
  nbeats: 16
  npatches: 16
  ohsamples: 0.25
  ohsvdrum: 0.25
  snsamples: 0.45
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
        import sys
        if len(sys.argv) < 2:
            raise RuntimeError("please enter profile name")
        profilename=sys.argv[1]
        if profilename not in Profiles:
            raise RuntimeError("profile not found")
        profile=Profiles[profilename]
        banks=SVBanks.load("tmp/banks/pico")
        curated=yaml.safe_load(open("octavox/samples/banks/pico/curated.yaml").read())
        npatches, nbeats = profile.pop("npatches"), profile.pop("nbeats")
        randomisers={"samples": SampleRandomiser(banks=banks,
                                                 curated=curated,
                                                 thresholds=profile)}
        patches=Patches.randomise(controllers=Controllers,
                                  randomisers=randomisers,
                                  n=npatches)
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        filestub="%s-randomiser" % timestamp
        patches.render(filestub=filestub,
                       banks=banks,
                       nbeats=nbeats)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
