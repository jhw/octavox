### show samples 02/02/24

- the main problem here is that 
  - each track uses a different sampler
  - each sampler holds samples for every single patch for the track in question
  - the sunvox view only shows you a slot reference
  - because of the generative nature of the machines, it's hard to get hold of the actual notes (although possible if you render the track)
  - a rendered patch doesn't make use of all the defined samples
  
- can imagine a action which takes a patch index
- you probably have to render a project to get the samplers and the notes which are actually played
- is there a pre- render stage prior to a sunvox render stage?
- yes because you have the whole model thing

- start with randomise task
- instead of rendering a project, just generate the internal model
- see what access you have to actual notes plus sampler mapping

### reanimate archives 02/02/24

```
(env) jhw@Justins-MacBook-Air octavox % python octavox/projects/samplebeats/__init__.py
INFO: pool=pico-richard-devine-default
Welcome to Samplebeats :)
>>> reanimate_archives
2024-01-02-07-47-15-random-hour-many
EXCEPTION: Traceback (most recent call last):
  File "/Users/jhw/work/octavox/octavox/core/cli/parse.py", line 58, in wrapped
    return fn(self, **kwargs)
  File "/Users/jhw/work/octavox/octavox/core/cli/__init__.py", line 64, in wrapped
    return fn(self, *args, **kwargs)
  File "/Users/jhw/work/octavox/octavox/core/cli/__init__.py", line 201, in do_reanimate_archives
    project=SVProject().render(patches=patches,
TypeError: SVProject.render() missing 1 required positional argument: 'nbreaks'
```

### slicebeats refactoring 26/11/23

- the seeds are no use because the seed model is completely different
- patterns are no good because they are no longer stored at the slice level, they are randomised depending on seed
- so really the only things worth preserving are the samples
- and then probably only the root sample as remember slicebeats are all mutations
- so maybe generate some kind of ranomised patterns and then splash the samples from the root into them

### slicebeats mapping 10/11/23

- use vitling sequencers with styles
- forget seeds; generated some new ones
- use root sample only; rest are mutated clones
- figure out how oh/ch now managed
- try and map samples in the order they are currently mapped
- push to archives and reanimate

### chain action 05/11/23

- not sure it should be called chain
- take a series of patterns you like
- create all the different mute permutations
- save to 8/16/24/32/48 size
- random selections from the set

### euclid patterns 01/11/23

- https://club.tidalcycles.org/t/week-1-lesson-5-mini-notation-part-3/449
- https://www.jakerichterdrums.com/13randomwords/2022/4/13/euclidean-rhythm
- http://cgm.cs.mcgill.ca/~godfried/publications/banff.pdf

      - [2, 5] # A thirteenth century Persian rhythm called Khafif-e-ramal
      - [3, 4] # The archetypal pattern of the Cumbia from Colombia, as well as a Calypso rhythm from Trinidad
      - [3, 5, 2] # Another thirteenth century Persian rhythm by the name of Khafif-e-ramal, as well as a Rumanian folk-dance rhythm
      - [3, 7] # A Ruchenitza rhythm used in a Bulgarian folk-dance
      - [3, 8] # The Cuban tresillo pattern
      - [4, 7] # Another Ruchenitza Bulgarian folk-dance rhythm
      - [4, 9] # The Aksak rhythm of Turkey
      - [4, 11] # The metric pattern used by Frank Zappa in his piece titled Outside Now
      - [5, 6] # Yields the York-Samai pattern, a popular Arab rhythm
      - [5, 7] # The Nawakhat pattern, another popular Arab rhythm
      - [5, 8] # The Cuban cinquillo pattern
      - [5, 9] # A popular Arab rhythm called Agsag-Samai
      - [5, 11] # The metric pattern used by Moussorgsky in Pictures at an Exhibition
      - [5, 12] # The Venda clapping pattern of a South African children’s song
      - [5, 16] # The Bossa-Nova rhythm necklace of Brazil
      - [7, 8] # A typical rhythm played on the Bendir (frame drum)
      - [7, 12] # A common West African bell pattern
      - [7, 16, 14] # A Samba rhythm necklace from Brazil
      - [9, 16] # A rhythm necklace used in the Central African Republic
      - [11, 24, 14] # A rhythm necklace of the Aka Pygmies of Central Africa
      - [13, 24, 5] # Another rhythm necklace of the Aka Pygmies of the upper Sangha

### per sampler pools 03/09/23

- instead of passing a single pool to sampler and having it optimisitically look for tags, what about passing different pools to samplers?
- would mean existing pool cli code is redundant
- would mean sample lookup no longer looks at tags, it just looks at whatever samples it is presented with
- this is might be desirable; tags are used only at the project level, not the core level; it would also give the cli more power to create pools
- randomise could allocate different pools to different channels
- you wouldn't need the global stuff any more
- you probaby don't need the free pools stuff any more 
- as free pools are really a hack, stuffing all samples in each channel
- so you just have curated pools
- sample lookup looks for tags optimistically, but otherwise selects from all
- cli randomly selects three (curated) pools
- but you have the option of fixing pools

### roadmap 30/08/23

- one euclid and vitling are abstracted into modules/sequencers, opens up the possibilty that you just have a single top level api and that a patch is just a yaml file like machines.yaml
- then you can mix and match a lot of these different machines together, since they all render independently
- they are rather like tracker or digitakt instruments, except you have the possibility of pushing large amounts of stuff through them in parallel
- you might have a couple of beats modules, and a whole series of bass modules; then whatever other pads and glitches you want
- a patch might start with focus on a particular instrument; beats or bass for example
- eg you might work on a bass patch but then augment it with some simple vitling beats
- the next question is how you export it to other hardware like the play or the digitakt
- might want export_xxx which exports into particular formts for different machines
- they you start to "augment" one of these stems with whatever the particular machine offers, maybe before passing it to the octa for live performance
- it's a whole different world out there

### samplebeats 30/08/23

- complete euclidbeats as far as possible
- refactor slicebeats along the lines of euclid
  - remove fixes
  - remove slices
  - replace oh/ch support with simple ht
  - replace slices with euclid style modulation on note and pattern
- combine euclid and vitling projects into a single samplebeats project
- that way you can mix euclid and vitling generators 
- sequencers can be moved to modules
- clis are then combined; no need to abstract pool generating code
- should be able to seamlessly save projects with different generators
- opens up the possibiity of a dedicated hats sampler

### python demos 22/08/23

- pitch shifting
  -  http://zulko.github.io/blog/2014/03/29/soundstretching-and-pitch-shifting-in-python/
  
- timestretching
  -  http://zulko.github.io/blog/2014/03/29/soundstretching-and-pitch-shifting-in-python/

- split on silence
  - https://stackoverflow.com/questions/45526996/split-audio-files-using-silence-detection

- pitch detection
- autotune
- vocoder

### banks 20/08/23

- dataline juno
- polyend tracker
- perkons

### s3 banks 15/08/23

- dump_pico_banks to push to s3
- banks initialisation to load from s3
- local banks cache 

### 01-s3-banks 13/08/23

- dump_pico_banks.py to push to s3 bucket
  - with pico prefix
  - https://stackoverflow.com/a/44946732/124179
- bank loading to load from s3
  - flat structure, ignore pico prefix
- local tmp bank cache
  - save to tmp if stuff doesn't exist
  - load from tmp if it does exist

### banned 09/08/23

- nero-bellum/59 Nightmare in Monochrome Candy.wav

### mutate and arrange 08/08/23

- mutate seeds only
- mutate seeds and styles
- try mutating densities only
- pass arrangement expression
- pass lists of roots and fills
- try mutes as overlay in separate action

### s3 capabilities 06/08/23

- requirements.txt
- setenv.sh AWS_CONFIG, PROJECT_NAME etc
- create bucket on cli initialisation
- action to put existing filename to bucket
- action to list/sync bucket based on prefix

### pitch shifting 06/08/23

- http://zulko.github.io/blog/2014/03/29/soundstretching-and-pitch-shifting-in-python/

### refactor archives 05/08/23

- replace sequencer key with id [mod]
- samples is now a list with tags field [array values]
- mutes are no longer part of structure
- density (0.75) is now contained at the root patch level
- replace lfo key with id [mod/ctrl]

### cutoff sampler 05/08/23

- existing sampler is bank sampler
- but you could have a wav cutoff sampler also
- takes a bank class, a filename a number of samples
- used pyaudio to do different cutuffs and insert into diifferent slots
- all this should be done in memory and without creation of more zipfiles, in memory or not 
- test script to create a sample project
- remember that for randomise purposea you want a single sampler
- so you have to pass a list of root samples and then do a small number of cutoffs for each 
- should make it much easier to do picobass

### arrange 05/08/23

- arrange1() -> take a list of root and a list of fills, and mix them
- arrange2() -> take a single root and apply differential densities to fills like aphex twin

### config classes 04/08/23

- main point of doing this would be to add config validation
- but kind of feels very enterprisey and negates the quick-and-dirty (but organised) ethos
- also remember that cli operates in a protected try/catch environment
- and if you were to do this then the class naming would probably have to change all over the place
- SVClass would have to become PBClass and config classes would then need to be renamed as something else
- seems a lot of work for relatively little value

### arrange 30/07/23

- take an array input
- define a random set of patterns and mutes
- iterate over blocks
- select random pattern and mute
- choose random set of patches consistent with pattern
- insert patches
- override mutes
- no mutations!

### slicebeats api 26/07/23

- randomise patches
- mutate patch
- chain patches
- load project
- set param
- show params
- set pool
- show pools
- copy pool
- show patch
- show samples
- clear projects

- fix/unfix/ban/unban sample 
- show fixes/bans
- clear fixes/bans 

### sampler samples indexation 25/07/24

- each sampler only has a limited set of slots
- so it's important to render only those which will be used

- the pattern/slice structure used by the slicebeats model ensures there is some redundancy here
- ie samples may be defined but not used, because a slice may not be part of a pattern
- randomising slices this gives some scope for introducing new samples

- samplers are defined on a per- track basis so you have more sample slots
- each sampler is passed a list of samples, and maintains the list of samplekeys in state
- the sampler then has a lookup() method which takes the sample and returns an index
- lookup() is called if SVTrig finds a key field in the trig, else it just uses id
- this is a sensible way of distinguishing between an extended module (sampler) and a standard RV unextended module (others)
- all modules are instantiated dynamically; a sampler will require samplekeys and banks, whereas a standard module doesn't need anything
- but once instantiated, they can all be called seamlessly/dynamically

- samplekeys is a dict of key (kk|sn|ht) to samples
- check what happens to oh|ch samples, but I think they are both listed under hats
- the bit that may need changing is the way the name of the module has to be a certain type ("XXSampler") and may need some runtime validation

### samples structure 08/07/23

- SVBanks is a dict of bank keyword keys and zipfile values
- feels like entire SVBanks class should be part of slicebeats
- random_key property needs to be removed and become part of pool
- get_wavfile is passed a key of "#{bank}:#{id}" form
- second half of this will need to change as going to use real names rather than ids
- will be using [bankfile, wavfile] list/tuple
- returns zf.open(wavfile, 'r') 
- which sampler then passes to wavfile.read

- using real wavfiles rather than ids simplifies things because you no longer need to look anything up
- together with removal of random_id, means this class could be much smaller and removed to slicebeats module

- you probably have a pool interface and multiple sub classes
- a (single) bank pool probably just returns anything from the bank, althought maybe it's worth curating
- a curated pool only returns stuff mapped to specific groups
- you might have strict curated and glitch curated as two different curated pools
- curated mappings need to be stored as yaml files


