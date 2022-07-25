from octavox.modules.sampler import SVBanks

import random, yaml

class PicoBanks(SVBanks):

    def __init__(self, root="tmp/banks/pico",
                 indexfile="octavox/samples/banks/pico/curated.yaml"):
        SVBanks.__init__(self, root)
        self.index=yaml.safe_load(open(indexfile).read())

    @property
    def random_kk(self):
        return random.choice(self.index["kick"]+self.index["bass"])    

    @property
    def random_sn(self):
        return random.choice(self.index["snare"]+self.index["clap"])    

    @property
    def random_ht(self):
        return random.choice(self.index["hat"]+self.index["perc"])

if __name__=="__main__":
    pass
