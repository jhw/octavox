from octavox.core.banks import SVBanks

from octavox.core.pools import SVPool, SVPools, SVSample

import boto3, json, os, yaml

MinPoolSize=12
    
def filter_pool(bank, banned):
    pool, wavfiles = SVPool(), bank.wavfiles
    for wavfile in wavfiles:
        key="%s/%s" % (bank.name, wavfile)
        if key not in banned:
            sample=SVSample({"bank": bank.name,
                             "file": wavfile})
            pool.add(sample)
    return pool

def init_pools(banks, banned, limit=MinPoolSize):
    pools, globalz = SVPools(), SVPools()
    for bankname, bank in banks.items():
        pool=filter_pool(bank=bank,
                         banned=banned)
        if len(pool) > limit:
            pools["%s-default" % bankname]=pool
    globalz["pico-global-default"]=pools.flatten2()
    pools.update(globalz)
    return pools

def dump_pools(pools, dirname="octavox/projects/samplebeats/pools"):
    if not os.path.exists(dirname):        
        os.mkdir(dirname)
    for poolname, pool in pools.items():
        print (poolname)
        with open("%s/%s.yaml" % (dirname, poolname), 'w') as f:
            f.write(yaml.safe_dump(json.loads(json.dumps(pool)), # yuk but hey
                                   default_flow_style=False))

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        banned=yaml.safe_load(open("octavox/projects/samplebeats/banned.yaml").read())
        pools=init_pools(banks=banks,
                         banned=banned)
        dump_pools(pools)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))

