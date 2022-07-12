import random, yaml

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
            return random.choice(self.curated["clap"]+self.curated["snare"])
        else:
            return self.random_wild()

    def random_oh(self):
        q=random.random()
        if q < self.thresholds["ohsvdrum"]:
            return random.choice(self.SVDrumHats)
        elif q < self.thresholds["ohsvdrum"]+self.thresholds["ohsamples"]:
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
    pass
