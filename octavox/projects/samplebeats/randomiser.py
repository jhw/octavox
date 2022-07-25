import random, yaml

Profiles=yaml.safe_load("""
default:
  kk: 0.8
  sn: 0.4
  cp: 0.4
  oh: 0.5
  ch: 0.5
strict:
  kk: 0.9
  sn: 0.5
  cp: 0.5
  oh: 0.8
  ch: 0.8
wild:
  kk: 0.4
  sn: 0.2
  cp: 0.2
  oh: 0.2
  ch: 0.2
""")

class SampleRandomiser:

    def __init__(self, banks, curated, thresholds):
        self.banks=banks
        self.curated=curated
        self.thresholds=thresholds

    def random_wild(self):
        modnames=list(self.banks.keys())
        mod=random.choice(modnames)
        n=len(self.banks[mod].infolist())
        i=random.choice(range(n))
        return "%s:%i" % (mod, i)

    def random_kk(self):
        q=random.random()
        if q < self.thresholds["kk"]:
            return random.choice(self.curated["kick"]+self.curated["bass"])    
        else:
            return self.random_wild()

    def random_sn(self):
        q=random.random()
        if q < self.thresholds["sn"]:
            return random.choice(self.curated["snare"])
        elif q < self.thresholds["sn"]+self.thresholds["cp"]:
            return random.choice(self.curated["clap"]+self.curated["snare"])
        else:
            return self.random_wild()

    def random_oh(self):
        q=random.random()
        if q < self.thresholds["oh"]:
            return random.choice(self.curated["hat"]+self.curated["perc"])    
        else:
            return self.random_wild()

    def random_ch(self):
        q=random.random()
        if q < self.thresholds["ch"]:
            return random.choice(self.curated["hat"]+self.curated["perc"])    
        else:
            return self.random_wild()        

    def randomise(self,
                  keys="kk|sn|oh|ch".split("|")):
        return {key: getattr(self, "random_%s" % key)()
                for key in keys}

if __name__=="__main__":
    pass
