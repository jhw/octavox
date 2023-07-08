### notes on samples structure 08/07/23

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


