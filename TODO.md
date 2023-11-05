### short

- chain action w/ mutes

### medium

- migrate slicebeats archives

### thoughts

- 3rd euclid arg?
  - probably not worth it
- machine mutation?
  - probably not required if you can iterate through depth of attributes
- separate sn/kk/ht patterns according to density?
  - not worth it

### done

- mutes
- pattern breaks > b738a77daf39fe52f393eb6611a324c16dda4121
- add back env and param lookup
  - 796ba065a28bd7767b6b0bb508752b7c49b3298c
- add temperature parameter
- modify env variables
- loading and them mutating fails because sample classes are not being created on project/machine load
- check ability to load a prior file
- multiple mutations
  - level 
  - level|trig|pattern|volume
  - level|trig|pattern|volume|sample
- simplified seed setting
- multiple migration actions with different attributes
- seed initialisation and clone is fucked up
- rendered root patch getting mutated even when seeds not changed
  - looks to be pattern and note
  - doesn't seem to be a function of sequencer
  - doesn't feel like modulator affected
- remove unused cli imports
- randomising a cloned patches seed seems to affect the original version also
- eliminate fixes
- randomise machines on per patch basis
- move euclid patterns into config
- simplify euclid patterns
- remove samples subdir from sequencers
- single sequencers list
- abstract sequencer yaml config
