### short [picobeats]

- model samples.randomise must be passed banks and pool
- cli to initialise pools
- variable to switch pool

### medium

- make nbeats an environment variable
- avoid glitch match in curation of default pool
- degrade
- custom sample pools

### thoughts

- clean up raw pico wav names?
  - not clear it's required
- sample similarity clustering?

### done

- remove cli profile variable
- curation script
- remove s3 stuff
- download into local banks directory with unchanged names
- rename slicebeats as picobeats
- remove save
- insert nbreaks automatically but for chain only
  - remove parameter
- define instruments and solos
- chainer to force samples to be the same as mute
- saving
- chainer with mutes
- refactor breaks so they are not voids
- complete load function
- add breaks variable
- add bool support
- simplify os.makedirs
- don't store self.filenmae
- remove pico- prefix from saved s3 files
  - test upload/download again
- include generator in filename
- remove stack
- fix need to remove pico- when downloading sample files
- save patches to json
- remove blender
- maintain internal stack of patches
