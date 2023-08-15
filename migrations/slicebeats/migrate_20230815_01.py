"""
- add params field to Modulator
"""

from octavox.projects.slicebeats.cli import Machines

import json, os

Params={machine["class"]:machine["params"]
        for machine in Machines}

if __name__=="__main__":
    if not os.path.exists("tmp/slicebeats/migrations"):
        os.makedirs("tmp/slicebeats/migrations")
    for filename in os.listdir("archive/slicebeats"):
        print (filename)
        patches=json.loads(open("archive/slicebeats/%s" % filename).read())
        for patch in patches:
            for machine in patch["machines"]:
                if machine["class"]=="octavox.projects.slicebeats.model.Modulator":
                    machine["params"]=Params[machine["class"]]
        with open("tmp/slicebeats/migrations/%s" % filename, 'w') as f:
            f.write(json.dumps(patches,
                               indent=2))
