### mutate and arrange 08/08/23

- mutate seeds only
- mutate seeds and styles
- try mutating densities only
- pass arrangement expression
- pass lists of roots and fills
- try mutes as overlay in separate action

### s3 capabilities 06/08/23

- requirements.txt
- setenv.sh AWS_CONFIG, PROJECT_NAME etc
- create bucket on cli initialisation
- action to put existing filename to bucket
- action to list/sync bucket based on prefix

### pitch shifting 06/08/23

- http://zulko.github.io/blog/2014/03/29/soundstretching-and-pitch-shifting-in-python/

### refactor archives 05/08/23

- replace sequencer key with id [mod]
- samples is now a list with tags field [array values]
- mutes are no longer part of structure
- density (0.75) is now contained at the root patch level
- replace lfo key with id [mod/ctrl]

### cutoff sampler 05/08/23

- existing sampler is bank sampler
- but you could have a wav cutoff sampler also
- takes a bank class, a filename a number of samples
- used pyaudio to do different cutuffs and insert into diifferent slots
- all this should be done in memory and without creation of more zipfiles, in memory or not 
- test script to create a sample project
- remember that for randomise purposea you want a single sampler
- so you have to pass a list of root samples and then do a small number of cutoffs for each 
- should make it much easier to do picobass

### arrange 05/08/23

- arrange1() -> take a list of root and a list of fills, and mix them
- arrange2() -> take a single root and apply differential densities to fills like aphex twin

### config classes 04/08/23

- main point of doing this would be to add config validation
- but kind of feels very enterprisey and negates the quick-and-dirty (but organised) ethos
- also remember that cli operates in a protected try/catch environment
- and if you were to do this then the class naming would probably have to change all over the place
- SVClass would have to become PBClass and config classes would then need to be renamed as something else
- seems a lot of work for relatively little value

### arrange 30/07/23

- take an array input
- define a random set of patterns and mutes
- iterate over blocks
- select random pattern and mute
- choose random set of patches consistent with pattern
- insert patches
- override mutes
- no mutations!

### slicebeats api 26/07/23

- randomise patches
- mutate patch
- chain patches
- load project
- set param
- show params
- set pool
- show pools
- copy pool
- show patch
- show samples
- clear projects

- fix/unfix/ban/unban sample 
- show fixes/bans
- clear fixes/bans 

### sampler samples indexation 25/07/24

- each sampler only has a limited set of slots
- so it's important to render only those which will be used

- the pattern/slice structure used by the slicebeats model ensures there is some redundancy here
- ie samples may be defined but not used, because a slice may not be part of a pattern
- randomising slices this gives some scope for introducing new samples

- samplers are defined on a per- track basis so you have more sample slots
- each sampler is passed a list of samples, and maintains the list of samplekeys in state
- the sampler then has a lookup() method which takes the sample and returns an index
- lookup() is called if SVTrig finds a key field in the trig, else it just uses id
- this is a sensible way of distinguishing between an extended module (sampler) and a standard RV unextended module (others)
- all modules are instantiated dynamically; a sampler will require samplekeys and banks, whereas a standard module doesn't need anything
- but once instantiated, they can all be called seamlessly/dynamically

- samplekeys is a dict of key (kk|sn|ht) to samples
- check what happens to oh|ch samples, but I think they are both listed under hats
- the bit that may need changing is the way the name of the module has to be a certain type ("XXSampler") and may need some runtime validation

### samples structure 08/07/23

- SVBanks is a dict of bank keyword keys and zipfile values
- feels like entire SVBanks class should be part of slicebeats
- random_key property needs to be removed and become part of pool
- get_wavfile is passed a key of "#{bank}:#{id}" form
- second half of this will need to change as going to use real names rather than ids
- will be using [bankfile, wavfile] list/tuple
- returns zf.open(wavfile, 'r') 
- which sampler then passes to wavfile.read

- using real wavfiles rather than ids simplifies things because you no longer need to look anything up
- together with removal of random_id, means this class could be much smaller and removed to slicebeats module

- you probably have a pool interface and multiple sub classes
- a (single) bank pool probably just returns anything from the bank, althought maybe it's worth curating
- a curated pool only returns stuff mapped to specific groups
- you might have strict curated and glitch curated as two different curated pools
- curated mappings need to be stored as yaml files


