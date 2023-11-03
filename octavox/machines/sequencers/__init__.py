import random

def random_samples(pool, tag, n):            
    samples=pool.filter_tag(tag)
    if samples==[]:
        samples=pool
    return [random.choice(samples)
            for i in range(n)]

class SampleSequencer(dict):

    """
    - remember tag may not be present in pool, hence need a default catch-all
    """
    
    
    def __init__(self, machine):
        dict.__init__(self, machine)
        for k, v in machine["params"].items():
            setattr(self, k, v)
        self.state={k:[] for k in "sample|pattern".split("|")}

    def random_sample(self, q):
        return q["sample"].choice(self["samples"])
        
    def switch_sample(self, q, i):
        return (0 == i % self.modulation["sample"]["step"] and
                q["trig"].random() < self.modulation["sample"]["threshold"])

    def switch_pattern(self, q, i):
        return (0 == i % self.modulation["pattern"]["step"] and
                q["trig"].random() < self.modulation["pattern"]["threshold"])

        
if __name__=="__main__":
    pass
