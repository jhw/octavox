### short [picobeats]

- check what original Banks.randomise fn returned
- cli to initialise pools
- cli poolname variable
- pass banks and pool to model

### medium

- make nbeats an environment variable
- custom sample pools
- degrade

### thoughts

- clean up raw pico wav names?
  - not clear it's required
- sample similarity clustering?

### done

- banks function to return file handle for bankname/wavfile
- pools.trim to reject anything too small
- pools.spawn_free/curated to add global pools
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
