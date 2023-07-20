from octavox.projects.picobeats.samples import Banks

from octavox.projects.picobeats.model import Patches, Slice, Sequence, Sequences, Lfo, Lfos

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

def test_sequence(key, pool):
    s0=Sequence.randomise(key, pool)
    r0=json.dumps(s0, sort_keys=True)
    s1=s0.clone()
    s1.randomise_pattern(limit=1)
    r1=json.dumps(s0, sort_keys=True) # NB s0
    print (r0==r1)

def test_sequences(pool):
    s0=Sequences.randomise(pool)
    r0=json.dumps(s0, sort_keys=True)
    s1=s0.clone()
    for sequence in s1:
        sequence.randomise_pattern(limit=1)
    r1=json.dumps(s0, sort_keys=True) # NB s0
    print (r0==r1)

def test_lfo(key):
    s0=Lfo.randomise(key)
    r0=json.dumps(s0, sort_keys=True)
    s1=s0.clone()
    s1.randomise_seed(limit=1)
    r1=json.dumps(s0, sort_keys=True) # NB s0
    print (r0==r1)

def test_lfos():
    s0=Lfos.randomise()
    r0=json.dumps(s0, sort_keys=True)
    s1=s0.clone()
    for lfo in s1:
        lfo.randomise_seed(limit=1)
    r1=json.dumps(s0, sort_keys=True) # NB s0
    print (r0==r1)

    
if __name__=="__main__":
    banks=Banks("octavox/banks/pico")
    pools=banks.spawn_pools().cull()
    test_patch(pools["global-curated"])
    test_slice("kk", pools["global-curated"])
    test_sequence("kk", pools["global-curated"])
    test_sequences(pools["global-curated"])        
    test_lfo("ec0")
    test_lfos()
