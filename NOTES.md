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
