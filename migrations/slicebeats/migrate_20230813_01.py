"""
- move sequencers and lfo under ids
- add classes
"""

import json, os

if __name__=="__main__":
    if not os.path.exists("tmp/slicebeats/migrations"):
        os.makedirs("tmp/slicebeats/migrations")
    for filename in os.listdir("archive/slicebeats"):
        print (filename)
        patches=json.loads(open("archive/slicebeats/%s" % filename).read())
        for patch in patches:
            patch["machines"]=machines=[]
            for seq in patch.pop("sequencers"):
                seq["class"]="octavox.projects.slicebeats.model.Sequencer"
                machines.append(seq)
            for lfo in patch.pop("lfos"):
                lfo["class"]="octavox.projects.slicebeats.model.Modulator"
                machines.append(lfo)
        with open("tmp/slicebeats/migrations/%s" % filename, 'w') as f:
            f.write(json.dumps(patches,
                               indent=2))
