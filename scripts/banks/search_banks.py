from octavox.modules.banks import SVBanks

import boto3, os, sys

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        if len(sys.argv) < 3:
            raise RuntimeError("please enter tag, term")
        tag, term =sys.argv[1:3]
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        for bankname, bank in banks.items():
            for sample in bank.filter_pool({tag: term}):
                print ("- %s/%s" % (sample["bank"],
                                    sample["file"].split(".")[0]))
    except RuntimeError as error:
        print ("Error: %s" % str(error))
