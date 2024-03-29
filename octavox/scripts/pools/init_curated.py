from octavox.core.banks import SVBanks

from octavox.core.pools import SVPool, SVPools, SVSample

import boto3, json, os, re, yaml

CurationTerms=yaml.safe_load("""
ht: (hat)|(ht)|(perc)|(ussion)|(prc)|(glitch)
kk: (kick)|(kik)|(kk)|(bd)|(bass)
sn: (snare)|(sn)|(sd)|(clap)|(clp)|(cp)|(hc)|(rim)|(plip)|(rs)
""")

MinPoolSize=12

def filter_pool(bank, terms, banned):
    pool, wavfiles = SVPool(), bank.wavfiles
    for wavfile in wavfiles:
        key="%s/%s" % (bank.name, wavfile)
        if key not in banned:
            for tag, term in terms.items():
                if re.search(term, wavfile, re.I):
                    sample=SVSample({"bank": bank.name,
                                     "file": wavfile,
                                     "tags": [tag]})
                    pool.add(sample)
    return pool

def init_pools(banks, terms, banned, limit=MinPoolSize):
    pools, globalz = SVPools(), SVPools()
    for bankname, bank in banks.items():
        pool=filter_pool(bank=bank,
                         terms=terms,
                         banned=banned)
        if len(pool) > limit:
            pools["%s-curated" % bankname]=pool
    globalz["pico-global-curated"]=pools.flatten()
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
        terms=[]
        banned=yaml.safe_load(open("octavox/projects/samplebeats/banned.yaml").read())
        pools=init_pools(banks=banks,
                         terms=CurationTerms,
                         banned=banned)
        dump_pools(pools)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))

