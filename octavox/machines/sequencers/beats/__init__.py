import random

def mean_revert(attr):
    def decorator(fn):
        def shall_revert(self, q):
            return (q[attr].random() < self.modulation[attr]["reversion"] and
                    len(self.state[attr]) > 1)
        def wrapped(self, q, *args, **kwargs):
            resp=self.state[attr][-2] if shall_revert(self, q) else fn(self, q, *args, **kwargs)
            self.state[attr].append(resp)
            return resp
        return wrapped
    return decorator

class BeatSequencer(dict):

    """
    - remember tag may not be present in pool, hence need a default catch-all
    """
    
    @classmethod
    def random_samples(self, pool, tag, n):            
        samples=pool.filter_tag(tag)
        if samples==[]:
            samples=pool
        return [random.choice(samples)
                for i in range(n)]

    @classmethod
    def random_seed(self):
        return int(1e8*random.random())
    
    def __init__(self, machine):
        dict.__init__(self, machine)
        for k, v in machine["params"].items():
            setattr(self, k, v)
        self.state={k:[] for k in "sample|pattern".split("|")}

    @mean_revert(attr="sample")
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
