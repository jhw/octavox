from octavox.projects.picobeats.samples import Banks

from octavox.projects.picobeats.model import Patches

import json

if __name__=="__main__":
    banks=Banks("octavox/banks/pico")
    pools=banks.spawn_pools().cull()
    p0=Patches.randomise(pool=pools["global-curated"],
                         n=32)[0]
    r0a=json.dumps(p0, sort_keys=True)
    p1=p0.clone()
    p1.mutate(limits={"pat": 1,
                      "slices": 1,
                      "style": 1,
                      "seed": 1})
    r1=json.dumps(p1, sort_keys=True)
    print (r0a!=r1)
    r0b=json.dumps(p0, sort_keys=True)
    print (r0a==r0b)

