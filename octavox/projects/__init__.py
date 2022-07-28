import yaml

Nouns, Adjectives = (yaml.safe_load(open("octavox/config/nouns.yaml").read()),                     
                     yaml.safe_load(open("octavox/config/adjectives.yaml").read()))

