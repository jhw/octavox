from botocore.exceptions import ClientError

import boto3, json, os

def clean_bucket(s3, bucketname, prefix="archive/samplebeats"):
    s3=boto3.client("s3")
    paginator=s3.get_paginator("list_objects_v2")
    pages=paginator.paginate(Bucket=bucketname,
                             Prefix=prefix)
    for struct in pages:
        if "Contents" in struct:
            for obj in struct["Contents"]:
                # print (obj["Key"])
                print (s3.delete_object(Bucket=bucketname,
                                        Key=obj["Key"]))

if __name__=="__main__":
    try:
        s3=boto3.client("s3")
        clean_bucket(s3, "octavox-assets")
    except RuntimeError as error:
        print ("Error: %s" % error)
    except ClientError as error:
        print ("Error: %s" % (str(error)))
