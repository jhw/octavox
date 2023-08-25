from octavox.modules.banks import SVBanks

from octavox.modules.pools import SVPool, SVSample

import boto3, os, yaml

"""
- could use dev/search_pool.py here (see grainpad.py) but 
  - loads of false negatives (some bass sounds don't have bass in description)
  - loads of false positives (a lot of bass sounds are kick drum sounds)
- so the sounds below have been hand curated
"""

BassStems=yaml.safe_load("""
- pico-baseck/03
- pico-baseck/34
- pico-baseck/37
- pico-clipping/32
- pico-dj-raitis-vinyl-cuts/47
- pico-ib-magnetic-saturation/51
- pico-legowelt/29
- pico-nero-bellum/62
- pico-pitch-black/27
- pico-pitch-black/30
- pico-pitch-black/32
- pico-syntrx/09
- pico-syntrx/19
- pico-syntrx/24
- pico-syntrx/26
- pico-syntrx/53
- pico-syntrx/60
""")

def init_pool(banks, terms):
    pool=SVPool()
    for term in terms:
        bankstem, filestem = term.split("/")
        try:
            bankname=banks.lookup(bankstem)
        except RuntimeError:
            print ("WARNING: couldn't find bank %s" % bankstem)
            pass
        bank=banks[bankname]
        try:
            filename=bank.lookup(filestem)
        except RuntimeError:
            print ("WARNING: couldn't find file %s in %s" % (filestem,
                                                             bankname))
        sample=SVSample({"bank": bankname,
                         "file": filename})
        pool.append(sample)
    return pool

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        """
        - this expression below will no ponger work as bank.spawn_cutoffs() and banls.filter() have been removed
        """
        banks=SVBanks.initialise(s3, bucketname)
        pool=init_pool(banks, terms=BassStems)
        for sample in pool:
            print ("- %s" % sample)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
