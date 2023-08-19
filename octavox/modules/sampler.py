from rv.modules.sampler import Sampler as RVSampler

from rv.note import NOTE as RVNOTE

from pydub import AudioSegment

# from scipy.io import wavfile
from octavox.modules.utils import wavfile

import io, warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

class SVBaseSampler(RVSampler):

    def __init__(self, *args, **kwargs):
        RVSampler.__init__(self, *args, **kwargs)

    """
    - https://github.com/metrasynth/gallery/blob/master/wicked.mmckpy#L497-L526
    """
        
    def load_sample(self, src, slot, **kwargs):
        sample = self.Sample()
        freq, snd = wavfile.read(src)
        if snd.dtype.name == 'int16':
            sample.format = self.Format.int16
        elif snd.dtype.name == 'float32':
            sample.format = self.Format.float32
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
        self.samples[slot] = sample
        return sample

class SVSampler(SVBaseSampler):

    def __init__(self, banks, pool, maxslots=120, *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        if len(pool) > maxslots:
            raise RuntimeError("SVBankSampler max slots exceeded")
        self.pool=pool
        self.segments={}
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        for i, sample in enumerate(self.pool.values()):
            self.note_samples[notes[i]]=i
            src=banks.get_wavfile(sample)
            # buf=self.slice_sample(sample, src)
            buf=self.slice_sample(sample, src) if "params" in sample else src
            self.load_sample(buf, i)
            sample=self.samples[i]
            sample.relative_note+=(root-i)

    def init_segment(fn):
        def wrapped(self, sample, src):
            segkey=sample.base_key
            if segkey not in self.segments:
                self.segments[segkey]=AudioSegment.from_file(src)
            return fn(self, sample, src)
        return wrapped

    def slice_range(self, sample, segment):
        if "params" in sample:
            params=sample["params"]
            i, n = params["i"], params["n"]
            if params["action"]=="cutoff":
                return (0, int(len(segment)*(i+1)/n))
            elif params["action"]=="slice":
                return (int(len(segment)*i/n),
                        int(len(segment)*(i+1)/n))
            else:
                raise RuntimeError("action %s not found" % params["action"])
        else:
            return (0, len(segment))
    
    @init_segment
    def slice_sample(self, sample, src):
        segment=self.segments[sample.base_key]
        start, end = self.slice_range(sample, segment)
        buf=io.BytesIO()
        segment[start:end].export(buf, format=sample.ext)
        return buf
                    
    def lookup(self, sample):
        return list(self.pool.keys()).index(sample.full_key)
        
if __name__=="__main__":
    pass
            
