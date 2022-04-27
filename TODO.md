### short

- clients to iterate over Machines.flatten
- rename "machines" as "players"
- remove TrigStyles
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
