### short

- rename players as tracks 
- ensure machine can render both trigs and FX
- refactor FX generation as another machine 

- consider moving vitling patterns into machine classes
- refactor fx render as per track render
- re- check vitling patterns
- change render to return beats rather than add them
- remove player keys; iterate over machine.players

### medium

- patch breaks
- slice temperature
- mutes
- add back blender
- expander script
  - based on mutator
  - each patch copied and includes per- track mutes
  - include breaks in output
  - check octatrack max number of slices
- compressor script
  - takes wav file
  - removes breaks

### long

### thoughts

- add generator reset method ?
  - no because might remove state in future
- librosa for python audio similarity ?
- change rendering root slice is rendered for full nbeats ?

### done

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
