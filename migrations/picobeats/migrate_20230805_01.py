"""
- replace sequencer key with id [mod]
- replace lfo key with id [mod/ctrl]
- mutes are no longer part of structure
- density (0.75) is now contained at the root patch level
- samples is now a list with tags field [array values]
"""

import json, os

Ids={"kk": "KickSampler",
     "sn": "SnareSampler",
     "ht": "HatSampler",
     "ec0": "Echo/wet",
     "ec1": "Echo/feedback"}

if __name__=="__main__":
    if not os.path.exists("tmp/picobeats/migrations"):
        os.makedirs("tmp/picobeats/migrations")
    for filename in os.listdir("archive/picobeats"):
        print (filename)
        patches=json.loads(open("archive/picobeats/%s" % filename).read())
        for patch in patches:
            for seq in patch["sequencers"]:
                if ("key" in seq and
                    "id" not in seq):
                    tag=seq.pop("key")
                    seq["id"]=Ids[tag]
                for slice in seq["slices"]:
                    samplekeys=[]
                    for tag, samplekey in slice["samples"].items():
                        samplekey["tags"]=[tag]
                        samplekeys.append(samplekey)
                    slice["samples"]=samplekeys
            for lfo in patch["lfos"]:
                if ("key" in lfo and
                    "id" not in lfo):
                    tag=lfo.pop("key")
                    lfo["id"]=Ids[tag]
            patch["density"]=0.75
            patch.pop("mutes")
        with open("tmp/picobeats/migrations%s" % filename, 'w') as f:
            f.write(json.dumps(patches,
                               indent=2))
