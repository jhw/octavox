from botocore.exceptions import ClientError

import boto3, json, os

def list_keys(s3, bucketname, prefix="archive/slicebeats"):
    s3=boto3.client("s3")
    paginator=s3.get_paginator("list_objects_v2")
    pages=paginator.paginate(Bucket=bucketname,
                             Prefix=prefix)
    keys=[]
    for struct in pages:
        if "Contents" in struct:
            for obj in struct["Contents"]:
                keys.append(obj["Key"])
    return sorted(keys)

def load_object(s3, bucketname, s3key):
    return json.loads(s3.get_object(Bucket=bucketname,
                                    Key=s3key)["Body"].read().decode("utf-8"))

def inspect_struct(struct):
    for i, patch in enumerate(struct):
        print ("====== %i ======" % i)
        print ()
        for machine in patch["machines"]:
            if machine["class"]=="octavox.projects.slicebeats.machines.Sequencer":
                print ("--- %s :: %s ---" % (machine["name"],
                                            machine["pattern"]))
                print ()
                for j, slice in enumerate(machine["slices"]):
                    samples=["%s/%s" % (sample["bank"],
                                        sample["file"])
                             for sample in slice["samples"]]                    
                    print ("%s :: %s :: %s" % (j,
                                               slice["style"],
                                               ", ".join(samples)))
                print ()
    

if __name__=="__main__":
    try:        
        s3=boto3.client("s3")
        bucketname="octavox-assets"
        s3keys=list_keys(s3, bucketname)
        for s3key in s3keys:
            struct=load_object(s3, bucketname, s3key)
            inspect_struct(struct)
            break
    except RuntimeError as error:
        print ("Error: %s" % error)
    except ClientError as error:
        print ("Error: %s" % (str(error)))
