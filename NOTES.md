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
