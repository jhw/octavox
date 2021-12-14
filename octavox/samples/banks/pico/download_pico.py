"""
- downloads Pico samples to tmp
"""

import boto3, os

def download_pico(s3, bucketname):
    paginator=s3.get_paginator("list_objects_v2")
    pages=paginator.paginate(Bucket=bucketname)
    for struct in pages:
        if "Contents" in struct:
            for obj in struct["Contents"]:
                print (obj["Key"])
                s3.download_file(bucketname,
                                 obj["Key"],
                                 "tmp/banks/%s" % obj["Key"])

if __name__=="__main__":
    try:
        import sys
        if len(sys.argv) < 2:
            raise RuntimeError("please enter bucket name")
        bucketname=sys.argv[1]
        s3=boto3.client("s3")
        for path in ["tmp",
                     "tmp/banks"]:
            if not os.path.exists(path):
                os.makedirs(path)            
        download_pico(s3, bucketname)
    except RuntimeError as error:
        print ("Error: %s" % (str(error)))
