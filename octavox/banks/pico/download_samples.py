import boto3, os

def download_samples(s3, bucketname):
    paginator=s3.get_paginator("list_objects_v2")
    pages=paginator.paginate(Bucket=bucketname)
    for struct in pages:
        if "Contents" in struct:
            for obj in struct["Contents"]:
                print (obj["Key"])
                filename=obj["Key"].replace("pico-", "")
                s3.download_file(bucketname,
                                 obj["Key"],
                                 "tmp/banks/pico/%s" % filename)

if __name__=="__main__":
    try:
        import sys
        if len(sys.argv) < 2:
            raise RuntimeError("please enter bucket name")
        bucketname=sys.argv[1]
        s3=boto3.client("s3")
        for path in ["tmp",
                     "tmp/banks",
                     "tmp/banks/pico"]:
            if not os.path.exists(path):
                os.makedirs(path)            
        download_samples(s3, bucketname)
    except RuntimeError as error:
        print ("Error: %s" % (str(error)))
