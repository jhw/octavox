### short [picobeats]

- test lifecycle

```
Traceback (most recent call last):
  File "octavox/projects/picobeats/cli.py", line 296, in <module>
    Shell(banks=banks,
  File "/Users/jhw/.pyenv/versions/3.8.11/lib/python3.8/cmd.py", line 138, in cmdloop
    stop = self.onecmd(line)
  File "/Users/jhw/.pyenv/versions/3.8.11/lib/python3.8/cmd.py", line 217, in onecmd
    return func(arg)
  File "octavox/projects/picobeats/cli.py", line 90, in wrapped
    return fn(self, *args, **kwargs)
  File "octavox/projects/picobeats/cli.py", line 117, in wrapped
    return fn(self, *[], **kwargs)
  File "octavox/projects/picobeats/cli.py", line 177, in wrapped
    return fn(self, *args, **kwargs)
  File "octavox/projects/picobeats/cli.py", line 189, in wrapped
    self.project.render_sunvox(banks=self.banks,
  File "/Users/jhw/work/octavox/octavox/projects/picobeats/model.py", line 469, in wrapped
    return fn(*args, **kwargs)
  File "/Users/jhw/work/octavox/octavox/projects/picobeats/model.py", line 484, in render_sunvox
    samplekeys=self.sample_keys(nbeats)
  File "/Users/jhw/work/octavox/octavox/projects/picobeats/model.py", line 455, in sample_keys
    samplekeys[key].add(trig["key"])
TypeError: unhashable type: 'list'
```

- make nbeats an environment variable

### medium

- custom sample pools
- degrade

### thoughts

- clean up raw pico wav names?
  - not clear it's required
- sample similarity clustering?

### done

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
