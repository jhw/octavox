### short

- check env variables can be modified
- env temperature

### medium

- check ability to load a prior file
- pattern breaks
- mutes
- chain action
- migration of slicebeats archives
- 3rd euclid arg

### thoughts

- machine mutation?
  - probably not required if you can iterate through depth of attributes
- separate sn/kk/ht patterns according to density?
  - not worth it

### done

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
