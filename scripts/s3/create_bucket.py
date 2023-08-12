from botocore.exceptions import ClientError

import boto3, os

def create_bucket(s3, bucketname, region):
    location={"LocationConstraint": region}
    print (s3.create_bucket(Bucket=bucketname,
                            CreateBucketConfiguration=location))
    
if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        region=os.environ["AWS_REGION"]
        if region in ["", None]:
            raise RuntimeError("AWS_REGION does not exist")
        s3=boto3.client("s3")
        create_bucket(s3, bucketname, region)
    except RuntimeError as error:
        print ("Error: %s" % (str(error)))
    except ClientError as error:
        print ("Error: %s" % (str(error)))
