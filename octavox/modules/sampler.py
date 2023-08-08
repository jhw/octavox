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

    def __init__(self, samplekeys, banks, maxslots=120, *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        if len(samplekeys) > maxslots:
            raise RuntimeError("SVBankSampler max slots exceeded")
        self.samplekeys=samplekeys
        self.samplestrings=[samplekey.full_key
                            for samplekey in samplekeys]
        self.segments={}
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        for i, samplekey in enumerate(self.samplekeys):
            self.note_samples[notes[i]]=i
            src=banks.get_wavfile(samplekey)
            buf=self.slice_sample(samplekey, src)
            # buf=self.slice_sample(samplekey, src) if "params" in samplekey else src
            self.load_sample(buf, i)
            sample=self.samples[i]
            sample.relative_note+=(root-i)

    def init_segment(fn):
        def wrapped(self, samplekey, src):
            segkey=samplekey.base_key
            if segkey not in self.segments:
                self.segments[segkey]=AudioSegment.from_file(src)
            return fn(self, samplekey, src)
        return wrapped

    def slice_range(self, samplekey, segment):
        if "params" in samplekey:
            params=samplekey["params"]
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
    def slice_sample(self, samplekey, src):
        segment=self.segments[samplekey.base_key]
        start, end = self.slice_range(samplekey, segment)
        buf=io.BytesIO()
        segment[start:end].export(buf, format=samplekey.ext)
        return buf
                    
    def lookup(self, samplekey):
        return self.samplestrings.index(samplekey.full_key)
        
if __name__=="__main__":
    pass
            
