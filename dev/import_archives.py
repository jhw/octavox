import boto3, os

if __name__=="__main__":
    if not os.path.exists("tmp/slicebeats/json"):
        os.makedirs("tmp/slicebeats/json")        
    session=boto3.session.Session()
    s3=session.resource('s3')    
    bucket_name='octavox-assets'
    source_prefix='archive/slicebeats'
    bucket=s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=source_prefix):
        print (obj.key)
        body=bucket.Object(obj.key).get()["Body"].read().decode("utf-8")
        filename="tmp/slicebeats/json/%s" % obj.key.split("/")[-1]
        with open(filename, 'w') as f:
            f.write(body)
            
        
