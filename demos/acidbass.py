from octavox.core.model import SVTrigs, SVNoteTrig, SVFXTrig

from octavox.core.project import SVProject

from datetime import datetime

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
    f_resonance: 1450
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 16
    delay: 36
    delay_unit: 3 # tick
- name: Reverb
  class: rv.modules.reverb.Reverb
  defaults:
    wet: 4
""")

Links=yaml.safe_load("""
- - Generator
  - Echo
- - Echo
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
    wave=wavefn()
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if trigfn(i):
            note_trig(trigs, "Generator", notefn(), velfn(), i)
            fx_trig(trigs, "Generator/waveform", wave, i)
            fx_trig(trigs, "Generator/f_release", relfn(), i)
            fx_trig(trigs, "Generator/f_freq_hz", freqfn(), i)
    return trigs.tracks

def spawn_patches(npatches=32):
    def hexval(h, n=4):
        return int(h+"".join(["0" for i in range(n-len(h))]), 16)
    def hexvalues(H, mult=0.5):
        return [mult*hexval(h) for h in H]
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
    def relfn(H="abcd"):
        return random.choice(hexvalues(H))
    def freqfn(H="0c|0e|0f|10|11|12".split("|")):
        return random.choice(hexvalues(H))
    return [acid_bass(wavefn=wavefn,
                      trigfn=trigfn,
                      notefn=notefn,
                      velfn=velfn,
                      relfn=relfn,
                      freqfn=freqfn)
            for i in range(npatches)]

if __name__=="__main__":
    try:
        if not os.path.exists("tmp/acidbass"):
            os.makedirs("tmp/acidbass")
        patches=spawn_patches()
        project=SVProject().render(patches=patches,
                                   modconfig=Modules,
                                   links=Links,
                                   bpm=120)
        ts=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        destfilename="tmp/acidbass/%s.sunvox" % ts
        with open(destfilename, 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("Error: %s" % str(error))
