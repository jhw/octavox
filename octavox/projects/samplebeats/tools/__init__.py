import random, yaml

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
    pass
