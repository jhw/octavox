import boto3, os

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        for filename in os.listdir("tmp/migrations/slicebeats"):
            print (filename)
            src="tmp/migrations/slicebeats/%s" % filename
            body=open(src).read()
            s3key="archive/slicebeats/%s" % filename
            s3.put_object(Bucket=bucketname,
                          Key=s3key,
                          Body=body,
                          ContentType="application/json")
    except RuntimeError as error:
        print ("Error: %s" % str(error))
