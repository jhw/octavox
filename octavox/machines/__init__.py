import random

def random_seed():
    return int(1e8*random.random())

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

if __name__=="__main__":
    pass
