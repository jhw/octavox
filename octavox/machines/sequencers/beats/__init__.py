import random

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

if __name__=="__main__":
    pass
