import yaml, random

from datetime import datetime

Nouns, Adjectives = (yaml.safe_load(open("octavox/config/nouns.yaml").read()),                     
                     yaml.safe_load(open("octavox/config/adjectives.yaml").read()))

def random_filename(prefix):
    ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    return "%s-%s-%s-%s" % (ts,
                            prefix,
                            random.choice(Adjectives),
                            random.choice(Nouns))

def Q(seed):
    q=random.Random()
    q.seed(seed)
    return q

def flatten(lists):
    values=[]
    for l in lists:
        values+=l
    return values

if __name__=="__main__":
    pass
