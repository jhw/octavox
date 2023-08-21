from octavox.modules.cli import random_filename

from octavox.modules.model import SVTrigs, SVNoteTrig, SVFXTrig

from octavox.modules.project import SVProject

import os, random, yaml

Modules=yaml.safe_load("""
- name: Generator
  class: rv.modules.analoggenerator.AnalogGenerator
  defaults:
    waveform: 2 # square
    attack: 0
    sustain: 0
    release: 256
    filter: 1 # LP
    f_envelope: 1
    f_attack: 0
    f_release: 192
    f_exponential_freq: 0
    f_freq_hz: 4096
    f_resonance: 1350
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 32
    delay: 36
    delay_unit: 3 # tick
- name: Distortion
  class: rv.modules.distortion.Distortion
  defaults:
    power: 64
- name: Reverb
  class: rv.modules.reverb.Reverb
  defaults:
    wet: 4
""")

Links=yaml.safe_load("""
- - Generator
  - Echo
- - Echo
  - Distortion
- - Distortion
  - Reverb
- - Reverb
  - Output
""")

def acid_bass(wavefn,
              trigfn,
              notefn,
              velfn,
              relfn,
              freqfn,
              resfn,
              nbeats=16):
    def note_trig(trigs, target, note, vel, i):
        trigs.append(SVNoteTrig(mod=target,
                                note=note,
                                vel=vel,
                                i=i))
    def fx_trig(trigs, target, value, i):
        trigs.append(SVFXTrig(target=target,
                              value=value,
                              i=i))
    wave, resonance = wavefn(), resfn()
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if trigfn(i):
            note_trig(trigs, "Generator", notefn(), velfn(), i)
            fx_trig(trigs, "Generator/waveform", wave, i)
            fx_trig(trigs, "Generator/f_release", relfn(), i)
            fx_trig(trigs, "Generator/f_freq_hz", freqfn(), i)
            fx_trig(trigs, "Generator/f_resonance", resonance, i)
    return trigs.tracks

def spawn_patches(npatches=32):
    def wavefn():
        return random.choice([1, 2]) # saw, square
    def trigfn(i):
        return random.random() < 0.5
    def notefn(basenote=12):
        q=random.random()
        if q < 0.7:
            return basenote
        elif q < 0.8:
            return basenote-2
        elif q < 0.9:
            return basenote+7
        else:
            return basenote+12
    def velfn():
        return 1 if random.random() < 0.3 else 0.8
    def spawn_relfn():
        values=random.choice([[int("%s000" % h, 16)/2
                               for h in H]
                              for H in "89ab|abcd|8ace|47ad".split("|")])
        def wrapped():
            return random.choice(values)
        return wrapped
    def spawn_freqfn():
        values=random.choice([[int("%s000" % h, 16)/2
                               for h in H]
                              for H in "123|123|1234|1234|3456|1357".split("|")])
        def wrapped():
            return random.choice(values)
        return wrapped
    def resfn():
        return random.choice([int("%s000" % h, 16)/2
                              for h in "bcdeee"])
    return [acid_bass(wavefn=wavefn,
                      trigfn=trigfn,
                      notefn=notefn,
                      velfn=velfn,
                      relfn=spawn_relfn(),
                      freqfn=spawn_freqfn(),
                      resfn=resfn)
            for i in range(npatches)]

if __name__=="__main__":
    try:
        if not os.path.exists("tmp/demos"):
            os.makedirs("tmp/demos")
        patches=spawn_patches()
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   bpm=120)
        destfilename="tmp/demos/%s.sunvox" % random_filename("acidbass")        
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
