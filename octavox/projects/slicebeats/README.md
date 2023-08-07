### Octavox::Slicebeats

There is currently just a single Octavox project `Slicebeats` which takes samples from Erica Synths Pico System II and lays out beat sequences with them 

https://www.ericasynths.lv/shop/eurorack-systems/pico-system-ii/

http://data.ericasynths.lv/picodrum/pack_list.json

Once you have started the CLI there are three main methods -

- `randomise()` -> generate a series of random patches

- `mutate(i)` -> generate a series of mutations from patch `i`

- `chain(i)` -> generate a track chain for patch `i` for export

See `/octavox/projects/slicebeats/cli.py` for other methods

I am indebted to `@vitling` for his `Endless Acid Banger` project, from whence I took inspiration for the beat patterns 

https://github.com/vitling/acid-banger

### Usage

```
(env) jhw@Justins-Air octavox % python octavox/projects/slicebeats/cli.py 
Welcome to Slicebeats :)
>>> list_pools
  baseck-free
  clipping-free
  complex-waveforms-free
  default-curated
  default-free
  dj-raitis-vinyl-cuts-curated
  dj-raitis-vinyl-cuts-free
> global-curated
  global-free
  ib-magnetic-saturation-free
  legowelt-curated
  legowelt-free
  nero-bellum-curated
  nero-bellum-free
  otto-von-schirach-curated
  otto-von-schirach-free
  pitch-black-curated
  pitch-black-free
  richard-devine-free
  syntrx-curated
  syntrx-free

>>> randomise_patches
INFO: 2023-07-15-07-45-27-random-happy-anything
>>> mutate_patch 0
INFO: 2023-07-15-07-45-43-mutation-practical-access
>>> 
```

(now fire up Sunvox and go look in `/tmp/slicebeats/sunvox`)

