### short

- remove refs to "trigs" from dom
- import TrigStyles as Instruments
- add random conditions to offbeats open/closed
- ensure all random numbers are pre- called in offbeats_open/closed
- group seeds at dom level and pass to trigs
- offbeats_open/closed will also need linked fx seeding

### medium

- patch breaks
- slice temperature
- new expander script
  - based on mutator
  - each patch copied and includes per- track mutes
  - include breaks in output
  - check octatrack max number of slices
- new compressor script
  - takes wav file
  - removes breaks

### long

### thoughts

### done

- get rid of trigmap
- rename trigs as instruments
- track mutes
- convert blender to use new file lookup
- change cli file stuff to accept pattern
- add profile as enum
- move profiles into randomiser
