import boto3, os

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        for filename in os.listdir("archive/slicebeats"):
            print (filename)
            s3key="archive/slicebeats/%s" % filename
            body=open(s3key).read() # local filename the same as s3key
            s3.put_object(Bucket=bucketname,
                          Key=s3key,
                          Body=body,
                          ContentType="application/json")
    except RuntimeError as error:
        print ("Error: %s" % str(error))
