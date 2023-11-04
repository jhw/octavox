from octavox.core.model import SVPatch, SVNoteTrig, SVFXTrig

from octavox.core.pools import SVSample

import json, os, random

def note_to_dict(self):
    return {"vel": self.vel,
            "sample": self.sample}

setattr(SVNoteTrig, 'to_dict', note_to_dict)

def fx_to_dict(self):
    return {"target": self.target,
            "value": self.value}

setattr(SVFXTrig, 'to_dict', fx_to_dict)

def render_patch(patch):
    for machine in patch["machines"]:
        if "samples" in machine:            
            machine["samples"]=[SVSample(sample)
                                for sample in machine["samples"]]
    rendered=patch.render(nbeats=16,
                          density=1)
    return ({K: [v.to_dict() for v in V]
             for K, V in rendered.items()})    

def json_stringify(struct):
    return json.dumps(struct,
                      sort_keys=True,
                      indent=2)

def randomise_seeds(patch):
    for machine in patch["machines"]:
        for key in machine["seeds"]:
            machine["seeds"][key]=int(1e8*random.random())

if __name__=="__main__":
    filename="tmp/samplebeats/json/%s" % sorted(os.listdir("tmp/samplebeats/json"))[-1]
    struct=json.loads(open(filename).read())
    patch0=SVPatch(**struct[0])
    rendered0=render_patch(patch0)
    patch1=patch0.clone()
    rendered1=render_patch(patch1)
    print (json_stringify(patch0)==json_stringify(patch1),
           json_stringify(rendered0)==json_stringify(rendered1))
    randomise_seeds(patch1)
    rendered1=render_patch(patch1)
    print (json_stringify(patch0)==json_stringify(patch1),
           json_stringify(rendered0)==json_stringify(rendered1))
                          
