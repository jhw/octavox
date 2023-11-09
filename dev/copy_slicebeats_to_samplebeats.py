import boto3

if __name__=="__main__":
    session=boto3.session.Session()
    s3=session.resource('s3')    
    bucket_name='octavox-assets'
    source_prefix='archive/slicebeats'
    destination_prefix='archive/samplebeats'
    bucket=s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=source_prefix):
        print (obj.key)
        new_key=obj.key.replace(source_prefix, destination_prefix)
        copy_source={'Bucket': bucket_name,
                     'Key': obj.key}
        bucket.Object(new_key).copy_from(CopySource=copy_source)
