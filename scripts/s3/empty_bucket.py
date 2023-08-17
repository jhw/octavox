from botocore.exceptions import ClientError

import boto3, os, sys

def empty_bucket(s3, bucketname, prefix):
    paginator=s3.get_paginator("list_objects_v2")
    pages=paginator.paginate(Bucket=bucketname,
                             Prefix=prefix)
    for struct in pages:
        if "Contents" in struct:
            for obj in struct["Contents"]:
                print (obj["Key"])
                s3.delete_object(Bucket=bucketname,
                                 Key=obj["Key"])

if __name__=="__main__":
    try:        
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        if len(sys.argv) < 2:
            raise RuntimeError("please enter prefix")
        prefix=sys.argv[1]
        s3=boto3.client("s3")
        empty_bucket(s3, bucketname, prefix)
    except RuntimeError as error:
        print ("Error: %s" % (str(error)))
    except ClientError as error:
        print ("Error: %s" % (str(error)))
