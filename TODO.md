### short

- replace floor/ceil with limits

- investigate why modclasses needs RV/SV key prefix

- pass kk/sn/ht/sh as cli options
- patch breaks
- slice temperature

### medium

- expander script
  - based on mutator
  - each patch copied and includes per- track mutes
  - include breaks in output
  - check octatrack max number of slices

- compressor script
  - takes wav file
  - removes breaks
  
- arranger script

- validator
  - trig formats
  - module references

- tune down loud SVDrum bass

### long

- vitling 303
- euclidian beats
- sunvox reverb chords
- city dreams bass
- city dreams noise
- librosa

### thoughts

- trig format validator ?
  - probably overkill as octavox unlikely to have other users
- move pattern expansion into slice constructor ?
  - no because it's fine as things are
- per- machine SVDrum/Sampler modules ?
  - probably overkill
  - would be useful for sv- level muting but that's really the OT's job
- initialise vitling generator with specific set of styles ? 
  - no because style info is part of machine
- mutes ?
  - don't think its consistent with cli options for different channels
- degrade ?
  - don't think it's really consistent with slices

### done

- abstract renderer
- rename modular as modconfig
- pass new modclasses arg as string:class dict
- abstract project as module
  - import sv classes into dom
- refactor effect note :value attribute
  - what does trig use ?
- test echo wet
- add echo feedback
- check renderer attr vs ctrl
- complete sample_hold implementation
- complete add implementation
- define echo machine
- convert machines to list
- remove styles from machine
- per- machine patterns
- add back patterns from master
- renamed pattern initialise as pattern expand
- pattern initialise
- pattern dsl
- reduce n to 1 by default
- include n within pattern definition
- add back irregular patterns
- pattern class and multipler
- n(slice)beats to be set at Tracks level
- simplify slice rendering
- embed styles in machine
- remove machines key
- machines as dict
- move slice iteration into tracks
- vitling should add explicit key
- notes should be a list not dict
- genericise passing of kwargs to generators
- include generators within mapping
- rename generator
- rename struct
- replace iteration over hardcoded keys with machine config
- add back sampler protection against fx trigs
- hats 
- rename struct as notes
- refactor generator / notes relationship so notes are passed to generator and generator is stateless
- notes.add method
- remove eval/hungarorise
- merge mapping and styles
- remove trig key (name/type) and replace with key
- merge offbeats open/closed
- trig patterns must pass key to add() function
- replace trignote with standard dict
- replace nested notes with single dict
- required trig names 
  - remove default name
- remove machine key from expansion keys
- remove machine.initialise
- single machine class
- remove machine classes
- generator to be passed as a closure
- generator to return type and notes.expand() to group according to type
- TrigNote to add type variable
- Notes to cluster and render based on type variable
- TrigNote class
- add basic notes class
- add intermediate representation with separate() method
- remove tracks
- remove hats
- re- merge trig rendering code
- simplify patch nomenclature
- remove fx
- reduce reverb to 4
- hungarorise machine names
- add fx pattern randomisation to mutator
- check if/why FX generator needs step
- pass different max levels to echo wet and feedback
- simplify s&h machine
- check mutator still works
- dual patterns
- combine slice render_trigs/effects
  - need to fix id issue
- combine track render_trigs/effects
- fx seeds not being reset
  - check if EffectPattern is required
- re- test mutator
- remove player keys; iterate over machine.players
- move trig rendering into slice and then into machine 
- allow machines to render both notes and fx
- embed rendering in machines
- remove randomise_style
- see if machine classes can be simplified
- simplify MachineConfig
- refactor init_machine
- check randomiser yaml output
- check mutator works
- refactor machines contructor
  - must be able to take json input
  - randomisation to randomise inputs only
- check saved yaml file
- do you still need a Players class
  - what happens to to_map
- replace rootstyle with style
  - all machines to take constructor args
- test mutator
- comment out closed/empty and offbeats open initial beat, check offbeats open/closed are synchronised properly
- kick and snare samples seem to be the same
- remove TrigStyles
- clients to iterate over Machines.flatten
- Machines.flatten to return list of players
- add hats- specific logic to MachineGroup.randomise_styles/seed
  - maybe HatsMatchineGroup class ?
- Machines.randomise to genereate joint hats group
- Machines.randomise to generate one MachineGroup per Machine
- move Machine sample/seed randomisations into MachineGroup
  - no direct access to machine
- new MachineGroup class 
  - extends list
- move trigs and FX into dom and simplify
- remove refs to "trigs" from dom
- get rid of trigmap
- rename trigs as instruments
- track mutes
- convert blender to use new file lookup
- change cli file stuff to accept pattern
- add profile as enum
- move profiles into randomiser
