from octavox.samples.banks import Banks

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

    def random_wild(self, banks):
        modnames=[self.SVDrum]+list(banks.keys())
        mod=random.choice(modnames)
        n=len(banks[mod].infolist()) if mod!=self.SVDrum else 120
        i=random.choice(range(n))
        return "%s:%i" % (mod, i)

    def random_kk(self,
                  banks,
                  samples,
                  prob_svdrum=0.45,
                  prob_samples=0.45):
        q=random.random()
        if q < prob_svdrum:
            return random.choice(self.SVDrumBass)
        elif q < prob_svdrum+prob_samples:
            return random.choice(samples["kick"]+samples["bass"])    
        else:
            return self.random_wild(banks)

    def random_sn(self,
                  banks,
                  samples,
                  prob_samples_sn=0.45,
                  prob_samples_cp=0.45):
        q=random.random()
        if q < prob_samples_sn:
            return random.choice(samples["snare"])
        elif q < prob_samples_sn+prob_samples_cp:
            return random.choice(samples["clap"])
        else:
            return self.random_wild(banks)

    def random_oh(self,
                  banks,
                  samples,
                  prob_svdrum=0.25,
                  prob_samples=0.25):
        q=random.random()
        if q < prob_svdrum:
            return random.choice(self.SVDrumHats)
        elif q< prob_svdrum+prob_samples:
            return random.choice(samples["hat"]+samples["perc"])    
        else:
            return self.random_wild(banks)

    def random_ch(self,
                  banks,
                  samples,
                  prob_svdrum=0.25,
                  prob_samples=0.25):
        q=random.random()
        if q < prob_svdrum:
            return random.choice(self.SVDrumHats)
        elif q< prob_svdrum+prob_samples:
            return random.choice(samples["hat"]+samples["perc"])    
        else:
            return self.random_wild(banks)        

    def init_sample(self,
                    instrument,
                    banks,
                    samples):
        fn=getattr(self, "random_%s" % instrument)
        return fn(banks, samples)        

    def randomise(self,
                  banks,
                  samples,
                  instruments=Instruments,
                  channels=Channels):
        return {instrument:self.init_sample(instrument,
                                            banks,
                                            samples)
                for instrument in instruments}

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
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
        banks=Banks.load("tmp/banks/pico")
        samples=yaml.safe_load(open("octavox/projects/breakbeats/pico-samples.yaml").read())
        randomisers={"samples": SampleRandomiser}
        patches=Patches.randomise(banks=banks,
                                  samples=samples,
                                  controllers=Controllers,
                                  randomisers=randomisers,
                                  n=kwargs["npatches"])
        patches.render(suffix="randomiser",
                       banks=banks,
                       nbeats=kwargs["nbeats"])
    except RuntimeError as error:
        print ("Error: %s" % str(error))
