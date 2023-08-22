"""
- rename Modulator as SampleHoldModulator with new path referemce
- remove style parameter
"""

from octavox.modules import list_s3_keys

import boto3, json, os

if __name__=="__main__":
    bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
    if bucketname in ["", None]:
        raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
    s3=boto3.client("s3")    
    if not os.path.exists("tmp/migrations/slicebeats"):
        os.makedirs("tmp/migrations/slicebeats")
    for s3key in list_s3_keys(s3, bucketname, prefix="archive/slicebeats"):
        print (s3key)
        patches=json.loads(s3.get_object(Bucket=bucketname,
                                         Key=s3key)["Body"].read())
        for patch in patches:
            for machine in patch["machines"]:
                if machine["class"]=="octavox.projects.slicebeats.model.Modulator":
                    machine["class"]="octavox.modules.lfos.sample_hold.SampleHoldModulator"
                    machine["params"].pop("style")
        filename=s3key.split("/")[-1]
        with open("tmp/migrations/slicebeats/%s" % filename, 'w') as f:
            f.write(json.dumps(patches,
                               indent=2))