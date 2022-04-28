### short

- check randomiser yaml output
- check mutator works
- refactor init_machine
- see if machine classes can be simplified
- simplify MachineConfig

### medium

- setting SnareStyles to [Kick, Electro] seems to result in Kick samples being used
  - accidentally copied reference ?
  
- check handling of [0, 0, 0, 1] pattern
  - is 0 rendered for 1x12 or 3x4 beats ?
  - should overlay

- re- check vitling patterns

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

- librosa for python audio similarity

### thoughts

### done

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
