from octavox.projects.picobeats.samples import Banks
from octavox.projects.picobeats.model import Patches

import json

def test_patch(pool):
    p0=Patches.randomise(pool=pool,
                         n=1).pop()
    r0=json.dumps(p0, sort_keys=True)
    p1=p0.clone()
    p1.mutate(limits={"pat": 1,
                      "slices": 0,
                      "style": 0,
                      "seed": 0})
    r1=json.dumps(p1, sort_keys=True)
    print (r0==r1)
    

if __name__=="__main__":
    banks=Banks("octavox/banks/pico")
    pools=banks.spawn_pools().cull()
    test_patch(pools["global-curated"])
