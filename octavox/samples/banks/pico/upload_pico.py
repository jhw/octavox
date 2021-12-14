"""
- uploads Pico samples from tmp
"""

import boto3, os

Region="eu-west-1"

def upload_pico(s3, bucketname):
    for filename in os.listdir("tmp/banks"):
        if not (filename.startswith("pico-") and
                filename.endswith(".zip")):
            continue
        print (filename)
        s3.upload_file("tmp/banks/%s" % filename,
                       bucketname,
                            filename)
    
if __name__=="__main__":
    try:
        import sys
        if len(sys.argv) < 2:
            raise RuntimeError("please enter bucket name")
        bucketname=sys.argv[1]
        s3=boto3.client("s3")
        upload_pico(s3, bucketname)
    except RuntimeError as error:
        print ("Error: %s" % (str(error)))
