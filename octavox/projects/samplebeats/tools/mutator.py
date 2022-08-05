from octavox.projects.samplebeats.dom import Patches

from octavox.projects.samplebeats.pico import PicoBanks

from octavox.projects.samplebeats.tools import Profiles

from octavox.projects import Nouns, Adjectives

import datetime, json, random, yaml

def randomise_patches(roots, kwargs):
    def init_patch(root, kwargs, mutate):
        patch=root.clone()
        if mutate:
            patch.mutate(limits={"samples": kwargs["dsamples"],
                                 "pat": kwargs["dpat"],
                                 "mute": kwargs["dmute"],
                                 "seed": kwargs["dseed"],
                                 "style": kwargs["dstyle"]},
                         slicetemp=kwargs["slicetemp"])
        return patch
    i=kwargs["index"] % len(roots)
    root=roots[i]
    return Patches([init_patch(root, kwargs, j>0)
                    for j in range(kwargs["npatches"])])

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: src
          description: source
          type: file
          root: tmp/samplebeats/patches
        - key: index
          description: index
          type: int
          default: 0
          min: 0
        - key: profile
          description: "profile"
          type: enum
          options:
          - default
          - strict
          - wild
          default: default
        - key: slicetemp
          description: "slicetemp"
          type: float
          min: 0
          max: 1
          default: 1
        - key: dsamples
          description: "d(samples)"
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dpat
          description: "d(pat)"
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dmute
          description: "d(mute)"
          type: float
          min: 0
          max: 1
          default: 0.0
        - key: dseed
          description: "d(seed)"
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: dstyle
          description: "d(style)"
          type: float
          min: 0
          max: 1
          default: 0.5
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        - key: npatches
          description: "n(patches)"
          type: int
          min: 1
          default: 64
        """)
        kwargs=cli(cliconf)
        roots=Patches(json.loads(open(kwargs["src"]).read()))
        patches=randomise_patches(roots, kwargs)
        profile=Profiles[kwargs["profile"]]
        banks=PicoBanks(profile=profile,
                        root="tmp/banks/pico")
        filename="%s-%s-%s" % (datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"),
                               random.choice(Adjectives),
                               random.choice(Nouns))
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filename=filename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
