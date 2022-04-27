### short

- new MachineGroup class 
  - extends list
- move Machine sample/seed randomisations into MachineGroup
  - no direct access to machine
- Machines.flatten to return list of Machines
  - all clients to iterate over Machines.flatten
- Machines.randomise to generate one MachineGroup per Machine
- Machines.randomise to genereate joint hats group
- add hats- specific logic to MachineGroup.randomise_styles/seed
  - maybe HatsMatchineGroup class ?
- refactor TrigStyles

- re- check vitling patterns

### medium

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

### thoughts

### done

- move trigs and FX into dom and simplify
- remove refs to "trigs" from dom
- get rid of trigmap
- rename trigs as instruments
- track mutes
- convert blender to use new file lookup
- change cli file stuff to accept pattern
- add profile as enum
- move profiles into randomiser
