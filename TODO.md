### short

- replace flatten2

### medium

- librosa demo

### demos

- kickers
- risers 
- drops

### thoughts

- cli sample fixing
  - think this is a bit of a misnomer
  - you'd be better working with mutate_patch_3
- undo/redo?
  - don't think it's worth it as this tends to be an in- memory model
  - problem is you always have to render to see anything
  - and every time you render you need a neew name
  - so undo is really just load a prior name
- add bpm to output filename?
  - not sure is worth it
- 3rd euclid arg?
  - probably not worth it
- machine mutation?
  - probably not required if you can iterate through depth of attributes
- separate sn/kk/ht patterns according to density?
  - not worth it

### done

- replace flatten2
- modify pool code to iterate through directories
- script to dump slicebeats pools
- script to dump curated pools
- script to dump default pools
- investigate if chaining is generating mutes
- see if wav dump to file can be replaced with in- memory operation
- move stems stuff into core cli
- combine wav export and stems
- why aren't chains visible in M8?
- adjust stem generation for breaks
- formatter for slice indexes
- slicing code
- generate_stems skeleton
- calculate term based on nticks/tpb/bpm
- add decorator to check if wav exists
- add tbp=4
- refactor nbeats as nticks
- add usepatterns option to slicebeats pool
- stem slicing
- export wav to proper filename
- test project export
- export requirements
- abstract wav export code
- abstract sunvox project rendering code
- check json.dumps indent
- rename json dir as dsl
- why does filename appear to be missing on project import
- slicebeats pool to use samples mentioned in patterns only
- slicebeats pool to use set to avoid duplicates
- script to randomise patches and insert slicebeats samples
- pass banned list to banks pools generation
- complete rendering of dump_samples grid
- remove trigs.grid
- action to show sample keys
- get rid of chord support
- script to filter slicebeats samples
- reanimate fails on nbreaks [notes]
- test project archive lifecycle
- remove pitch info
- remove pydub slicing stuff
- check breaks are still in place
- script to load slicebeats and extract (migrate) relevant information
- delete samplebeats archives
- script to refactor slicebeats name as samplebeats
- use constructor during chaining
- json error

```
EXCEPTION: Traceback (most recent call last):
  File "/Users/jhw/work/octavox/octavox/core/cli/parse.py", line 58, in wrapped
    return fn(self, **kwargs)
  File "/Users/jhw/work/octavox/octavox/core/cli/__init__.py", line 71, in wrapped
    return fn(self, *args, **kwargs)
  File "/Users/jhw/work/octavox/octavox/core/cli/__init__.py", line 55, in wrapped
    dump_json(self)
  File "/Users/jhw/work/octavox/octavox/core/cli/__init__.py", line 35, in dump_json
    f.write(json.dumps(self.patches,
  File "/Users/jhw/.pyenv/versions/3.10.12/lib/python3.10/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
  File "/Users/jhw/.pyenv/versions/3.10.12/lib/python3.10/json/encoder.py", line 201, in encode
    chunks = list(chunks)
  File "/Users/jhw/.pyenv/versions/3.10.12/lib/python3.10/json/encoder.py", line 429, in _iterencode
    yield from _iterencode_list(o, _current_indent_level)
  File "/Users/jhw/.pyenv/versions/3.10.12/lib/python3.10/json/encoder.py", line 325, in _iterencode_list
    yield from chunks
  File "/Users/jhw/.pyenv/versions/3.10.12/lib/python3.10/json/encoder.py", line 405, in _iterencode_dict
    yield from chunks
  File "/Users/jhw/.pyenv/versions/3.10.12/lib/python3.10/json/encoder.py", line 438, in _iterencode
    o = _default(o)
  File "/Users/jhw/.pyenv/versions/3.10.12/lib/python3.10/json/encoder.py", line 179, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type set is not JSON serializable
```

- randomise chained mutations
- truncate length
- mute combinations
- mutate and chain must assert project
- skeleton action which takes multiple roots
- figure out how to pass mutes to project render
  - should you even use @render_project
- mutes
- pattern breaks > b738a77daf39fe52f393eb6611a324c16dda4121
- add back env and param lookup
  - 796ba065a28bd7767b6b0bb508752b7c49b3298c
- add temperature parameter
- modify env variables
- loading and them mutating fails because sample classes are not being created on project/machine load
- check ability to load a prior file
- multiple mutations
  - level 
  - level|trig|pattern|volume
  - level|trig|pattern|volume|sample
- simplified seed setting
- multiple migration actions with different attributes
- seed initialisation and clone is fucked up
- rendered root patch getting mutated even when seeds not changed
  - looks to be pattern and note
  - doesn't seem to be a function of sequencer
  - doesn't feel like modulator affected
- remove unused cli imports
- randomising a cloned patches seed seems to affect the original version also
- eliminate fixes
- randomise machines on per patch basis
- move euclid patterns into config
- simplify euclid patterns
- remove samples subdir from sequencers
- single sequencers list
- abstract sequencer yaml config
