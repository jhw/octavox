### short

- check if/why FX generator needs step
- add fx pattern randomisation to mutator
- hungarorise machine names

### medium

- re- check vitling patterns

- blender
- patch breaks
- slice temperature
- mute
- degrade

- expander script
  - based on mutator
  - each patch copied and includes per- track mutes
  - include breaks in output
  - check octatrack max number of slices
- compressor script
  - takes wav file
  - removes breaks

### long

- euclidian beats
- vitling 303
- sunvox reverb chords
- city dreams bass
- city dreams noise

### thoughts

- add fx, trig globals ?
- rename players as tracks  ?
- librosa for python audio similarity ?

### done

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
