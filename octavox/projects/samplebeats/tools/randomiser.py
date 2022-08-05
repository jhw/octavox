from octavox.projects.samplebeats.dom import Patches

from octavox.projects.samplebeats.pico import PicoBanks

from octavox.projects.samplebeats.tools import Profiles

from octavox.projects import Nouns, Adjectives

import datetime, random, yaml

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
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
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        - key: npatches
          description: "n(patches)"
          type: int
          min: 1
          default: 32
        """)
        kwargs=cli(cliconf)
        profile=Profiles[kwargs["profile"]]
        banks=PicoBanks(profile=profile,
                        root="tmp/banks/pico")
        patches=Patches.randomise(banks=banks,
                                  slicetemp=kwargs["slicetemp"],
                                  n=kwargs["npatches"])
        filename="%s-%s-%s" % (datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"),
                               random.choice(Adjectives),
                               random.choice(Nouns))
        patches.render(banks=banks,
                       nbeats=kwargs["nbeats"],
                       filename=filename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
