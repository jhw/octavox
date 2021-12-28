### short

- move curated
- move wavfile
- add mute option back to mutator

### medium

- breakbeats2
  - no slices
  - change samples within different slice ranges
  
- degrading
- reanimator date range
- SVSampler pull request

### thoughts

- arranger ?
  - don't think it makes sense
  - better to scan entire mutator chain into octatrack and set trig points manually
- chainmaker/mutes ?
  - think covered by mutator
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

### done

- use filestub not filename
- reanimator to use single datetime
- reanimator to use original timestamp slug
- move banks into sampler
- rename samples as curated
- reanimator to reanimate all within dates
- add link to load sample code
- remove mutator mutes
- pattern temperature control
- pass kwargs to sample randomiser
- expose sample randomiser params to cli
- pass randomiser class to samples and move SampleRandomiser into randomiser
- rename enginename as suffix
- move colours into pattern
- rename engine as project
- sampler class
- consider moving init_sampler to /sampler
- notes re recorder buffer
- notes re octa -> hermod -> sunvox trigger
- dearchiver
- archive
- github project
- new sampler directory with wavfile, sampler_utils
- rename trigs/fx as generators
- todo
- test breakbeats
- check all imports
- fix samples references
- fix pico banks paths
- core breakbeats project
- banks
- complete pico sample management
