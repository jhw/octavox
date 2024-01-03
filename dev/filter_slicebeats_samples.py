"""
- samplebeats process and file format has evolved way beyond initial slicebeats
- entire slice model has changed, you now have euclidian as well as vitling etc
- this renders most of the data in the slicebeats archives irrelevant - particularly seeds and styles
- however the sample data is probably still relevant, if it can be extracted
- main problem is that slicebeats patterns tended to favour initial items in a tagged list of samples; is this still true?
"""

import json, os

def filter_samples(patch):
    samples={}
    for machine in patch["machines"]:
        if "slices" in machine:
            for slice in machine["slices"]:
                for sample in slice["samples"]:
                    key=sample["tags"][0]
                    samples.setdefault(key, [])
                    samples[key].append((sample["bank"], sample["file"]))
    return samples

if __name__=="__main__":
    for filename in os.listdir("archives/slicebeats"):
        print ("--- %s ---" % filename.split(".")[0])
        patches=json.loads(open("archives/slicebeats/%s" % filename).read())
        print (filter_samples(patches.pop()))

