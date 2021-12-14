"""
- sampler utilities to load a sample into sunvox via RV, as provided by @gldnspud
- https://github.com/metrasynth/gallery/blob/master/wicked.mmckpy#L497-L526
- NB local wavfile.py implementation culled from scipy, as scipy is huge and currently doesn't play well with new macs
"""

from rv.modules.sampler import Sampler as RVSampler

import warnings

# from scipy.io import wavfile

import wavfile

warnings.simplefilter("ignore", wavfile.WavFileWarning)

def load_sample(src, sampler, slot, **kwargs):
    sample = sampler.Sample()
    freq, snd = wavfile.read(src)
    if snd.dtype.name == 'int16':
        sample.format = sampler.Format.int16
    elif snd.dtype.name == 'float32':
        sample.format = sampler.Format.float32
    else:
        raise RuntimeError("dtype %s Not supported" % snd.dtype.name)
    if len(snd.shape) == 1:
        size, = snd.shape
        channels = 1
    else:
        size, channels = snd.shape
    sample.rate = freq
    sample.channels = {
        1: RVSampler.Channels.mono,
        2: RVSampler.Channels.stereo,
    }[channels]
    sample.data = snd.data.tobytes()
    for key, value in kwargs.items():
        setattr(sample, key, value)
    sampler.samples[slot] = sample
    return sample

if __name__=="__main__":
    pass
