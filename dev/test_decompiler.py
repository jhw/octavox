from octavox.projects.samplebeats.dom import Machines, Slice, Slices, PatternMap, Tracks, Patch, Patches

import os, yaml

def decompile(patch, keys=["kk", "sn", "ht"]):
    def init_slice(slice, keys):
        machines=Machines([machine
                           for machine in slice["machines"]
                           if machine["key"] in keys])
        return Slice(samples=slice["samples"],
                     machines=machines)
    def init_patch(patch, keys):
        slices=Slices([init_slice(slice, keys)
                       for slice in patch["tracks"]["slices"]])
        patterns=PatternMap({k:v
                             for k, v in patch["tracks"]["patterns"].items()
                             if k in keys})
        tracks=Tracks(slices=slices,
                      patterns=patterns)
        return Patch(tracks=tracks)
    return [init_patch(patch, [key, "ec"])
            for key in keys]
    
if __name__=="__main__":
    try:
        filenames=sorted(os.listdir("tmp/samplebeats/patches"))
        if filenames==[]:
            raise RuntimeError("no projects found")
        src="tmp/samplebeats/patches/%s" % filenames.pop()
        patches=Patches(yaml.safe_load(open(src).read()))
        if patches==[]:
            raise RuntimeError("no patches found")
        root=patches.pop()
        for patch in decompile(root):
            print (patch)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
