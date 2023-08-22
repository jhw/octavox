from octavox.modules.banks import SVBanks

import boto3, os, sys

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        if len(sys.argv) < 2:
            raise RuntimeError("please enter term")
        term=sys.argv[1]
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        poolterms={term: [term]}
        pools=banks.spawn_pools(terms=poolterms)
        for sample in pools["global-curated"]:
            print ("- %s/%s" % (sample["bank"],
                                sample["file"].split(".")[0]))
    except RuntimeError as error:
        print ("Error: %s" % str(error))
