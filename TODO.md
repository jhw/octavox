### short [simplify mutes]

### medium

- density
- chain to use list of roots -> intarray support
- clone, update pool

### thoughts

- sunvox stops?
- randomiser filename to include pool name?
  - feels like over- optimisation
- make (bank, wavfile) a tuple on creation?
  - but then u can't save to JSON
  - at least not without custom encode/decode
- sample similarity clustering?

### done

- env and pool to share common base with abbreviation lookup
- reduce default temperatures
- rename samples as poolname
- add poolname abbreviation matching
- replace enum support with string
  - special setparam code to validate pools
- cli variable to list pools
- make nbeats an environment variable
- move banks into /octavox/banks/pico where they can be shared
  - Banks class also
- pass banks and pool to model
- cli to initialise pools
- cli poolname variable
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
