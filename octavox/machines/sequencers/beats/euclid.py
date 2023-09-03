from octavox.core.model import SVNoteTrig, SVFXTrig

from octavox.core.pools import SVSample

from octavox.machines import Q

from octavox.machines.sequencers.beats import BeatSequencer, mean_revert

import yaml

"""
- https://club.tidalcycles.org/t/week-1-lesson-5-mini-notation-part-3/449
- https://www.jakerichterdrums.com/13randomwords/2022/4/13/euclidean-rhythm
- http://cgm.cs.mcgill.ca/~godfried/publications/banff.pdf
"""

Patterns=[{"pulses": pat[0],
           "steps": pat[1]}
          for pat in yaml.safe_load("""
- [2, 5] # A thirteenth century Persian rhythm called Khafif-e-ramal
- [3, 4] # The archetypal pattern of the Cumbia from Colombia, as well as a Calypso rhythm from Trinidad
- [3, 5, 2] # Another thirteenth century Persian rhythm by the name of Khafif-e-ramal, as well as a Rumanian folk-dance rhythm
- [3, 7] # A Ruchenitza rhythm used in a Bulgarian folk-dance
- [3, 8] # The Cuban tresillo pattern
- [4, 7] # Another Ruchenitza Bulgarian folk-dance rhythm
- [4, 9] # The Aksak rhythm of Turkey
- [4, 11] # The metric pattern used by Frank Zappa in his piece titled Outside Now
- [5, 6] # Yields the York-Samai pattern, a popular Arab rhythm
- [5, 7] # The Nawakhat pattern, another popular Arab rhythm
- [5, 8] # The Cuban cinquillo pattern
- [5, 9] # A popular Arab rhythm called Agsag-Samai
- [5, 11] # The metric pattern used by Moussorgsky in Pictures at an Exhibition
- [5, 12] # The Venda clapping pattern of a South African children’s song
- [5, 16] # The Bossa-Nova rhythm necklace of Brazil
- [7, 8] # A typical rhythm played on the Bendir (frame drum)
- [7, 12] # A common West African bell pattern
- [7, 16, 14] # A Samba rhythm necklace from Brazil
- [9, 16] # A rhythm necklace used in the Central African Republic
- [11, 24, 14] # A rhythm necklace of the Aka Pygmies of Central Africa
- [13, 24, 5] # Another rhythm necklace of the Aka Pygmies of the upper Sangha
""")]

"""
- https://raw.githubusercontent.com/brianhouse/bjorklund/master/__init__.py
"""

def bjorklund(steps, pulses, **kwargs):
    steps = int(steps)
    pulses = int(pulses)
    if pulses > steps:
        raise ValueError    
    pattern = []    
    counts = []
    remainders = []
    divisor = steps - pulses
    remainders.append(pulses)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level = level + 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)    
    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)         
        else:
            for i in range(0, counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)    
    build(level)
    i = pattern.index(1)
    pattern = pattern[i:] + pattern[0:i]
    return pattern
            
class EuclidSequencer(BeatSequencer):
    
    @classmethod
    def randomise(self,
                  machine,
                  pool):
        samples=BeatSequencer.random_samples(pool=pool,
                                             tag=machine["params"]["tag"],
                                             n=machine["params"]["nsamples"])
        seeds={k:BeatSequencer.random_seed()
               for k in "sample|trig|pattern|volume".split("|")}
        return EuclidSequencer({"name": machine["name"],
                                "class": machine["class"],
                                "params": machine["params"],
                                "samples": samples,
                                "seeds": seeds})

    def __init__(self, machine):
        BeatSequencer.__init__(self, machine)
                            
    def clone(self):
        return EuclidSequencer(self)

    @mean_revert(attr="pattern")
    def random_pattern(self, q,
                       patterns=Patterns):
        return bjorklund(**q["pattern"].choice(patterns))

    """
    - for the moment it's either/or in terms of sample/pattern switching
    """
    
    def render(self, nbeats):
        q={k:Q(v) for k, v in self["seeds"].items()}
        sample, pattern = (self.random_sample(q),
                           self.random_pattern(q))
        for i in range(nbeats):
            if self.switch_sample(q, i):
                sample=self.random_sample(q)
            elif self.switch_pattern(q, i):
                pattern=self.random_pattern(q)
            beat=bool(pattern[i % len(pattern)])
            if q["trig"].random() < self.density and beat:
                volume=self.volume(q["volume"], i)
                yield SVNoteTrig(mod=self["name"],
                                 sample=sample,
                                 vel=volume,
                                 i=i)

    def volume(self, q, i, n=5, var=0.1, drift=0.1):
        for j in range(n+1):
            k=2**(n-j)
            if 0 == i % k:
                sigma=q.gauss(0, var)
                return 1-max(0, min(1, j*drift+sigma))
                
if __name__=="__main__":
    pass
