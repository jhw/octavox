### short

- script to splash slicebeats samples onto new randomise structure
- test project archive lifecycle
- action to show dump samples
- remove pydub slicing stuff
- remove pitch info
- check chain is working
- pydub scripts to slice a dumped wavfile
- fixing and banning

### medium

### thoughts

- 3rd euclid arg?
  - probably not worth it
- machine mutation?
  - probably not required if you can iterate through depth of attributes
- separate sn/kk/ht patterns according to density?
  - not worth it

### done

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
