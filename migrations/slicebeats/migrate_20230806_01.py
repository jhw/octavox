"""
- refactor id as name
"""

import json, os

if __name__=="__main__":
    if not os.path.exists("tmp/slicebeats/migrations"):
        os.makedirs("tmp/slicebeats/migrations")
    for filename in os.listdir("archive/slicebeats"):
        print (filename)
        patches=json.loads(open("archive/slicebeats/%s" % filename).read())
        for patch in patches:
            for seq in patch["sequencers"]:
                seq["name"]=seq.pop("id")
            for lfo in patch["lfos"]:
                lfo["name"]=lfo.pop("id")
        with open("tmp/slicebeats/migrations/%s" % filename, 'w') as f:
            f.write(json.dumps(patches,
                               indent=2))
