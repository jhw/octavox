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


if __name__=="__main__":
    pass
