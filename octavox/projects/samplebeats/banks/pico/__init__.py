from octavox.modules.sampler import SVBanks

import random, yaml

class PicoBanks(SVBanks):

    def __init__(self,
                 profile,
                 root="tmp/banks/pico",
                 indexfile="octavox/projects/samplebeats/banks/pico/curated.yaml"):
        SVBanks.__init__(self, root)
        self.index=yaml.safe_load(open(indexfile).read())
        self.profile=profile
        
    @property
    def random_kk(self):
        return random.choice(self.index["kick"]+self.index["bass"]) if random.random() < self.profile["kk"] else self.random_key

    @property
    def random_sn(self):
        return random.choice(self.index["snare"]+self.index["clap"]) if random.random() < self.profile["sn"] else self.random_key

    @property
    def random_oh(self):
        return random.choice(self.index["hat"]+self.index["perc"]) if random.random() < self.profile["oh"] else self.random_key

    @property
    def random_ch(self):
        return random.choice(self.index["hat"]+self.index["perc"]) if random.random() < self.profile["ch"] else self.random_key

    def randomise(self,
                  keys="kk|sn|oh|ch".split("|")):
        return {key: getattr(self, "random_%s" % key)
                for key in keys}
    
if __name__=="__main__":
    pass
