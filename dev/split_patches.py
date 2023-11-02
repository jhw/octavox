"""
- script to examine differences between patches[0] and patches[1] after clone() call in mutate_patch action
"""

import json, os, sys

if __name__=="__main__":
    try:
        if len(sys.argv) < 2:
            raise RuntimeError("please enter filename")
        filename=sys.argv[1]
        if not filename.endswith(".json"):
            raise RuntimeError("file must be a json file")
        if not os.path.exists(filename):
            raise RuntimeError("file does not exist")
        patches=json.loads(open(filename).read())
        if not isinstance(patches, list):
            raise RuntimeError("struct must be a list")
        for i in range (2):
            with open("tmp/patch-%i.json" % i, 'w') as f:
                f.write(json.dumps(patches[i],
                                   indent=2))
    except RuntimeError as error:
        print ("Error: %s" % str(error))
