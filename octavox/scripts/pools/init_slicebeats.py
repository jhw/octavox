from octavox.core.pools import SVPool, SVPools, SVSample

import json, os, yaml

def init_pool(root="archives/slicebeats",
              usepatterns=False):
    def add_samples(samples, filename):            
        patches=json.loads(open(filename).read())
        patch=patches.pop() # as a mutation, all patches have the same samples
        for machine in patch["machines"]:
            if "slices" in machine:
                n=1+max([int(tok[-1]) for tok in machine["pattern"].split("|")]) if usepatterns else len(machine["slices"])
                for i in range(n):
                    slice=machine["slices"][i]
                    for sample in slice["samples"]:
                        for attr in ["pitch", "mod"]:
                            if attr in sample:
                                sample.pop(attr)
                        if ("ch" in sample["tags"] or
                            "oh" in sample["tags"]):
                            sample["tags"]=["ht"]
                        key="%s/%s" % (sample["bank"],
                                       sample["file"])
                        samples[key]=sample
    samples={}
    for filename in os.listdir(root):
        if "mutate" not in filename:
            raise RuntimeError("slicebeats file is not a single root mutation")
        add_samples(samples, "%s/%s" % (root, filename))
    pool=SVPool()
    for sample in samples.values():
        pool.append(SVSample(sample))
    return pool

if __name__=="__main__":
    dirname="octavox/projects/samplebeats/pools"
    if not os.path.exists(dirname):      
        os.mkdir(dirname)    
    for poolname, pool in [("pico-slicebeats-strict", init_pool(usepatterns=True)),
                           ("pico-slicebeats-lenient", init_pool(usepatterns=False))]:
        print (poolname)
        with open("%s/%s.yaml" % (dirname, poolname), 'w') as f:
            f.write(yaml.safe_dump(json.loads(json.dumps(pool)), # yuk but hey
                                   default_flow_style=False))
