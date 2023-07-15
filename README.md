### Octavox

Octavox is a project to generate and mutate interesting looking Sunvox sample chains, for slicing and performing in a hardware system like Elektron's Octatrack or Digitakt

https://www.elektron.se/en/octratrack-mkii-explorer

https://www.elektron.se/en/digitakt-explorer

This project makes heavy use of Sunvox and Radiant Voices, to whose authors `@nightradio` and  `@gldnspd` I am deeply indebted

https://www.warmplace.ru/soft/sunvox/

https://github.com/metrasynth/radiant-voices

### Octavox::Picobeats

There is currently just a single Octavox project `Picobeats` which takes samples from Erica Synths Pico System II and lays out beat sequences with them 

https://www.ericasynths.lv/shop/eurorack-systems/pico-system-ii/

http://data.ericasynths.lv/picodrum/pack_list.json

Once you have started the CLI there are three main methods -

- `randomise()` -> generate a series of random patches

- `mutate(i)` -> generate a series of mutations from patch `i`

- `chain(i)` -> generate a track chain for patch `i` for export

See `/octavox/projects/picobeats/cli.py` for other methods

I am indebted to `@vitling` for his `Endless Acid Banger` project, from whence I took inspiration for the beat patterns 

https://github.com/vitling/acid-banger

### Installation

```
jhw@Justins-Air octavox % . ./setenv.sh 
jhw@Justins-Air octavox % python -m venv env
jhw@Justins-Air octavox % . env/bin/activate
(env) jhw@Justins-Air octavox % pip install --upgrade pip
Requirement already satisfied: pip in ./env/lib/python3.8/site-packages (22.1.2)
Collecting pip
  Using cached pip-23.1.2-py3-none-any.whl (2.1 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 22.1.2
    Uninstalling pip-22.1.2:
      Successfully uninstalled pip-22.1.2
Successfully installed pip-23.1.2
(env) jhw@Justins-Air octavox % pip install -r requirements.txt 
Collecting git+https://github.com//metrasynth/radiant-voices (from -r requirements.txt (line 1))
  Cloning https://github.com//metrasynth/radiant-voices to /private/var/folders/ms/y9_pfxl16qj49c9qxg8dy76r0000gn/T/pip-req-build-pwcp8z0_
  Running command git clone --filter=blob:none --quiet https://github.com//metrasynth/radiant-voices /private/var/folders/ms/y9_pfxl16qj49c9qxg8dy76r0000gn/T/pip-req-build-pwcp8z0_
  Resolved https://github.com//metrasynth/radiant-voices to commit 13db34eb0c451748401abc8e887f3229c968fe37
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Requirement already satisfied: lxml in ./env/lib/python3.8/site-packages (from -r requirements.txt (line 2)) (4.9.1)
Requirement already satisfied: numpy in ./env/lib/python3.8/site-packages (from -r requirements.txt (line 3)) (1.21.4)
Requirement already satisfied: pyyaml in ./env/lib/python3.8/site-packages (from -r requirements.txt (line 4)) (5.4.1)
Requirement already satisfied: attrs>=19.3.0 in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (21.2.0)
Requirement already satisfied: python-slugify in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (5.0.2)
Requirement already satisfied: hexdump in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (3.3)
Requirement already satisfied: logutils in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (0.3.5)
Requirement already satisfied: networkx in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (2.6.3)
Requirement already satisfied: text-unidecode>=1.3 in ./env/lib/python3.8/site-packages (from python-slugify->radiant-voices==1.0.3->-r requirements.txt (line 1)) (1.3)
```

### Usage

```
(env) jhw@Justins-Air octavox % python octavox/projects/picobeats/cli.py 
Welcome to Octavox Picobeats :)
>>> listpools
- baseck-free
- clipping-free
- complex-waveforms-free
- default-curated
- default-free
- dj-raitis-vinyl-cuts-curated
- dj-raitis-vinyl-cuts-free
- global-curated
- global-free
- ib-magnetic-saturation-free
- legowelt-curated
- legowelt-free
- nero-bellum-curated
- nero-bellum-free
- otto-von-schirach-curated
- otto-von-schirach-free
- pitch-black-curated
- pitch-black-free
- richard-devine-free
- syntrx-curated
- syntrx-free

>>> setparam pool base
poolname=baseck-free
>>> randomise
2023-07-15-07-45-27-random-happy-anything
>>> mutate 0
2023-07-15-07-45-43-mutation-practical-access
>>> chain 0
2023-07-15-07-45-59-chain-specialist-street
>>> 
```

(now fire up Sunvox and go look in `/tmp/picobeats/sunvox`)

