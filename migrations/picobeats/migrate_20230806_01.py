"""
- refactor id as name
"""

import json, os

if __name__=="__main__":
    for filename in os.listdir("archive/picobeats"):
        print (filename)
        patches=json.loads(open("archive/picobeats/%s" % filename).read())
        for patch in patches:
            for seq in patch["sequencers"]:
                seq["name"]=seq.pop("id")
            for lfo in patch["lfos"]:
                lfo["name"]=lfo.pop("id")
        with open("tmp/picobeats/%s" % filename, 'w') as f:
            f.write(json.dumps(patches,
                               indent=2))
