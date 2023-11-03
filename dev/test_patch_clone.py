from octavox.core.model import SVPatch

import json, os

if __name__=="__main__":
    filename="tmp/samplebeats/json/%s" % sorted(os.listdir("tmp/samplebeats/json"))[-1]
    struct=json.loads(open(filename).read())
    patch=SVPatch(**struct[0])
    print (patch.render(nbeats=16))
    
