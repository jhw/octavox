### short

- seed initialisation and clone is fucked up

### medium

- check ability to load a prior file

- machine mutation

- cli density
- pattern breaks
- mutes
- chain action
- migration of slicebeats archives
- 3rd euclid arg

### thoughts

- separate sn/kk/ht patterns according to density?
  - not worth it

### done

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
