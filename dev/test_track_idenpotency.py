from octavox.projects.picobeats.samples import Banks

from octavox.projects.picobeats.model import Patches, Slice, Sequence

import json

def test_patch(pool):
    p0=Patches.randomise(pool=pool,
                         n=1).pop()
    r0=json.dumps(p0, sort_keys=True)
    p1=p0.clone()
    p1.mutate(limits={"pat": 0,
                      "slices": 0,
                      "style": 0,
                      "seed": 1})
    r1=json.dumps(p0, sort_keys=True) # NB p0
    print (r0==r1)

def test_slice(key, pool):
    s0=Slice.randomise(key, pool)
    r0=json.dumps(s0, sort_keys=True)
    s1=s0.clone()
    s1.randomise_seed(limit=1)
    r1=json.dumps(s0, sort_keys=True) # NB s0
    print (r0==r1)

def test_sequence(key, pool, shuffle):
    s0=Sequence.randomise(key, pool)
    r0=json.dumps(s0, sort_keys=True)
    s1=s0.clone()
    s1.randomise_pattern(limit=1)
    if shuffle:
        s1.shuffle_slices(limit=1)
    r1=json.dumps(s0, sort_keys=True) # NB s0
    print (r0==r1)

if __name__=="__main__":
    banks=Banks("octavox/banks/pico")
    pools=banks.spawn_pools().cull()
    test_patch(pools["global-curated"])
    test_slice("kk", pools["global-curated"])
    for shuffle in [True, False]:
        test_sequence("kk", pools["global-curated"], shuffle)
