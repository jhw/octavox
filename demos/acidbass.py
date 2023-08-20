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
              notefn,
              atkfn,
              relfn,
              freqfn,
              resfn,
              density=0.5,
              nbeats=16):
    def note_trig(trigs, target, note, i):
        trigs.append(SVNoteTrig(mod=target,
                                note=note,
                                i=i))
    def fx_trig(trigs, target, value, i):
        mod, ctrl = target.split("/")
        trigs.append(SVFXTrig(mod=mod,
                              ctrl=ctrl,
                              value=value,
                              i=i))
    wave, attack, resonance = wavefn(), atkfn(), resfn()
    trigs=SVTrigs(nbeats=nbeats)
    for i in range(nbeats):
        if random.random() < density:
            note_trig(trigs, "Generator", notefn(), i)
            fx_trig(trigs, "Generator/waveform", wave, i)
            fx_trig(trigs, "Generator/f_attack", attack, i)
            fx_trig(trigs, "Generator/f_release", relfn(), i)
            fx_trig(trigs, "Generator/f_freq_hz", freqfn(), i)
            fx_trig(trigs, "Generator/f_resonance", resonance, i)
    return trigs.tracks

def spawn_patches(destfilename,
                  modules=Modules,
                  links=Links,
                  npatches=32,
                  bpm=120):
    def rand_range(params):
        floor, ceil = 2**params["floor"], 2**(params["floor"]+params["range"])
        return floor+int(random.random()*(ceil-floor))
    def wavefn():
        return random.choice([1, 2])
    def notefn(basenote=12):
        q=random.random()
        if q < 0.75:
            return basenote
        elif q < 0.9:
            return basenote-2
        else:
            return basenote+12
    def atkfn():
        return 2**random.choice([0, 0, 0, 11, 12, 13])
    def spawn_relfn():
        params={"floor": random.choice([13.75, 14, 14.25]),
                "range": random.choice([0.25, 0.5, 0.75])}
        def wrapped():
            return rand_range(params)
        return wrapped
    def spawn_freqfn():
        params={"floor": random.choice([6, 7, 8]),
                "range": random.choice([4, 5, 6])}
        def wrapped():
            return rand_range(params)
        return wrapped
    def resfn():
        return 2**random.choice([14.4, 14.6, 14.8, 14.8])
    patches=[acid_bass(wavefn=wavefn,
                       notefn=notefn,
                       atkfn=atkfn,
                       relfn=spawn_relfn(),
                       freqfn=spawn_freqfn(),
                       resfn=resfn)
             for i in range(npatches)]
    project=SVProject().render(patches=patches,
                               modconfig=modules,
                               links=links,
                               bpm=bpm)
    with open(destfilename, 'wb') as f:
        project.write_to(f)

if __name__=="__main__":
    try:
        if not os.path.exists("tmp/demos"):
            os.makedirs("tmp/demos")
        destfilename="tmp/demos/%s.sunvox" % random_filename("acidbass")
        spawn_patches(destfilename=destfilename)
    except RuntimeError as error:
        print ("Error: %s" % str(error))