### sampler samples indexation 25/07/24

- each sampler only has a limited set of slots
- so it's important to render only those which will be used

- the pattern/slice structure used by the picobeats model ensures there is some redundancy here
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
- feels like entire SVBanks class should be part of picobeats
- random_key property needs to be removed and become part of pool
- get_wavfile is passed a key of "#{bank}:#{id}" form
- second half of this will need to change as going to use real names rather than ids
- will be using [bankfile, wavfile] list/tuple
- returns zf.open(wavfile, 'r') 
- which sampler then passes to wavfile.read

- using real wavfiles rather than ids simplifies things because you no longer need to look anything up
- together with removal of random_id, means this class could be much smaller and removed to picobeats module

- you probably have a pool interface and multiple sub classes
- a (single) bank pool probably just returns anything from the bank, althought maybe it's worth curating
- a curated pool only returns stuff mapped to specific groups
- you might have strict curated and glitch curated as two different curated pools
- curated mappings need to be stored as yaml files

### projects 02/07/23

- bjorklund beats
- vitling 303
- city dreams bass
- vordhosbn hats
- chords


