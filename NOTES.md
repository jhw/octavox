### module instantiation 26/07/21

- sampler needs to be initialised with list of sample keys
- sampler.initialise() needs to be part of constructor routine, which requires banks and patches
- however patches only required for sample keys
- right now modclasses are created by patches, and then instantiated with args at the project render level
- feels like you will have to pass mod and kwargs as part of modklasses
- kwargs for sampler would be a list of sample keys
- when instantiating module, update kwargs with modclasses[kwargs]
- then sample_keys can be set as part of sampler
- when rendering, can lookup id using sample_keys.index(key)
- sampler also has to initialise wav files, which requires banks
- but banks can be passed to init_modules, as is already passed to init_project
- populate_sample_ids disappears because is replaced by new sample render function

### per- instrument samplers 26/07/21

- per- instrument samplers might simplify a lot of things
- for one you can include a lot more samples within the project, because you get three or four times the capability
- for two, you might be able to reduce sampler complexity (particularly the sample packing/indexing code) by pre- populating samples with specific genres
- this might then allow you to implement vitling ghost beats as a proper vca module, rather than as beat volume (which would be much closer to a midi/hardware implementation)

### cli 11/07/22

- what if you could run it in a cli
- you wouldn't need to dump yaml files, you could keep everything in state
- you could maintain a git like index of current variant, with head position etc 
- could do undo and redo etc, view current position 
- all the parameters that go into randomiser and mutator could be state variables 
- would be quicker to call randomiser and mutaror due to cli shortcuts 
- bank and sample randomiser could also be cli state variables and could be changed 

### sunvox -> octatrack workflow 16/06/22

- run randomiser
- pick favourite
- run mutator
- manually export compressed mutator from sunvox into wav dir
- run compressor
- connect octatrack
- go into file mode
- copy compressed wav in set audio directory
- eject drive and ** disconnect cable **
- load sample into flex machine
- slice sample
- check how slices play
- load sample into second flex machine
- slices should be saved with the sample so no need to re- slice
- test playing multiple parts and switching

### cloning 12/06/22

- root is list of patches
- patch has tracks (dict)
- track has patterns (dict) and slices (list)
- slice has machines (list) and samples (dict)

- ensure all dicts have consistent constructors
- ensure all lists have consistent constructors

### slicetemp 29/05/22

- float cli variable
- slice temperature cli variable
- bubble temp variable up to pattern selection
- select sample universe based on patterns
- override sample_hold pattern

### notes setup 17/05/22

- notes class
- trignote class
- vitling generator adds trignotes to notes
- notes must sort/expand into tracks
- must do this based on key
- each note type must have a key property
- is a combination of type and name
- type is mandatory and either trig or FX
- name is optional but defaults to default 
- so add name type and key fields to trignote
- could be dict properties maybe 
- when expanding, include the type from the first note 

### machine configuration ???

- so current blocker is that trigs and fx machines are configured different ways
- trigs pass samples to render, which are then used to create a trig generator
- fx uses class- level variable for mod/attr etc to create an fx generator
- somehow these two have to be harmonised, in order that render has a single signature, and also that whatever gets passed to generators is passed in a consistent manner
- feels like the fx machine class- level variables have to go
- remember that all these machines need to be instantiated with seed and style variables

### mutator and rendering 27/04/22

- machines don't need base class; kick and snare can be dicts, hats can be list
- but hats needs a renderer that makes it look like a dict with ht key
- ideally this is something like __repr__ which can be called automatically by yaml.safe_dump
- (maybe they are all just dicts?)
- confirm that a patch is dumped correctly
- then machine constructors need to take seed and style
- they (should) already do this but need to rename rootstyle as style
- then machines randomisation and constructor needs to change because classes have to be instantiated at the __init__ level
- randomise() method must send something similar to what the constructor receives when loading a file 

### linked machines 26/04/22

- so the problem appears to be that a single machine can't be randomised (either style or seed) in isolation
- because you have linked machines or machine groups
- and its really the linked machines which have styles and seeds
- eg if you decide "offbeats" then it's "offbeats_open" + "offbeats_closed"
- and in this case the two seeds *must* be the same
- and if you decide "closed" then it's "closed" + "empty"
- the two seeds don't have to be the same here but they may as well be
- then TrigStyles has to change because you don't directly influence offbeats_open and offbeats_closed; you influence "offbeats" which then calls "offbeats_open" and "offbeats_closed" under the hood
- these groups mirror the old style channels
- feels like there is a missing class here in terms of machine groups

### old notes 21/04/22

###### short

- cli to take pattern arg and not iterate thru files
- remove command line pattern passed to cli

- gaussian temperature variables
  - sample selection
  - pattern mutation

- palettes
- arranger

###### medium

- degrading

###### long

- simplebeats
- SVSampler pull request

###### thoughts

- slice ids ?
  - not enough similarity in patterns
- sunvox preroll ?
  - doesn't matter if going to do manual sampling
- render fx same way as trigs ?
  - controversial [notes]
- blender to preserve roots ?
  - no because no clones are created 
- "sticky" track/slices (heartbeat) ?
  - feels like overkill for now
- save colours ?
- harmonise fx/effects nomenclature ?
- sv drum levels ?

### projects

- polyrhythms
- sweet city dreams bass
- pads/chords/lfos
- kicker
- 303 (slide, accent)
- rumble bass
- noise hats
- noise lasers


### simplebeats 29/12/21

- simplebeat is like slicebeats but simpler
- one problem with slicebeats is it doesn't preserve long patterns, they are copied over
- simplebeats preserves that but allows you to switch samples for slices within a pattern
- this is likely to mean some kind of expanded trigs generator which allows you to pass in a list of patterns
- could then select sample using modulo len(samples) or something

### fx rendering 16/12/21

- should fx be rendered globally across track, or locally at slice level
- currently implementing former and it feels like clean solution
- but problem is it means arrangement is harder - you can concatenate slices, but no sense in which you can concatenate fx
- but maybe it doesn't matter since fx is relatively fixed, and this is a "discoverly" tool rather than an "exact replication" tool
- if you were to implement this then fx would need to sit at per- slice level, and there would have to be a lot more fx definitions, which starts to feel superfluous
- so maybe things are the right way after all, even if there are some limitations

### arranger 16/12/21

- octa seems to suck at auto- slicing long samples
- might have better luck at manual capture and slicing
- but in meantime you could have an octavox arranger
- specify patches and have octavox glue them together in longer tracks
- nice thing about this is you get the effects bleed from one slice to another
- which you don't get with octa
- also the whole arranging thing might just be simpler with octavox

- to do this you will need to concatenate tracks
- problem with this is right now fx is applied to global track rather than patch
- this needs to change

- means effects need to become part of tracks
- then track rendering needs separate render_slices, render_effects methods
- effects needs to observe tracks
- means archive will have to change and have new fx with randomly generated seeds


### practice 14/12/21

- recorder buffer demo -> http://sarm-wol.s3-website-eu-west-1.amazonaws.com/2021-08/workflow_midi_patch.html

- manual capture demo -> http://sarm-wol.s3-website-eu-west-1.amazonaws.com/2021-08/workflow_sunvox_patch.html

- octa -> hermod -> sunvox demo -> https://keep.google.com/#NOTE/1_UC8B2V2yQuw5B_wRJU8TZhYbveWMOt-F8ig3wudp6hwZ-unBl5-6n4_fIPZJKk

- slicing
- slider- driven slicing
- recording breakbeats

### blog post 14/12/21

- https://keep.google.com/#NOTE/1Xqufk40ZlznSIIV_rLsfarkSRuhfMjbBL6ewnSoo68HM8nEAS63X0ZuzgN5e_NtCYqPV

### octa -> hermod -> sunvox -> recorder trigs 14/12/21

- http://sarm-wol.s3-website-eu-west-1.amazonaws.com/2021-08/workflow_midi_patch.html
- http://sarm-wol.s3-website-eu-west-1.amazonaws.com/2021-08/workflow_sunvox_patch.html
- https://keep.google.com/#NOTE/1_UC8B2V2yQuw5B_wRJU8TZhYbveWMOt-F8ig3wudp6hwZ-unBl5-6n4_fIPZJKk
