from rv.modules.sampler import Sampler as RVSampler

from rv.note import NOTE as RVNOTE

from pydub import AudioSegment

# from scipy.io import wavfile
from octavox.modules.sampler import wavfile

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

MaxSlots=120
    
class SVSampler(SVBaseSampler):

    def __init__(self, banks, pool, maxslots=MaxSlots, *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        if len(pool) > maxslots:
            raise RuntimeError("SVBankSampler max slots exceeded")
        self.pool, self.segments = pool, {}
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]]=i
            src=banks.get_wavfile(sample)
            buf=self.slice_sample(sample, src) if sample.has_mod else src
            self.load_sample(buf, i)
            svsample=self.samples[i]
            svsample.relative_note+=(root-i)+sample["pitch"]

    def init_segment(fn):
        def wrapped(self, sample, src):
            segkey=sample["file"]
            if segkey not in self.segments:
                self.segments[segkey]=AudioSegment.from_file(src)
            return fn(self, sample, src)
        return wrapped

    @init_segment
    def slice_sample(self, sample, src):
        seg0=self.segments[sample["file"]]
        modfn=getattr(self, "apply_%s" % sample["mod"])
        seg1=modfn(seg0, **sample["ctrl"])
        buf=io.BytesIO()
        seg1.export(buf, format=sample["file"].split(".")[-1])
        return buf

    def apply_cutoff(self, seg, cutoff, fadeout):
        return seg[:cutoff].fade_out(fadeout)

    def apply_granular(self, seg, offset, sz, n, fadeout, padding):
        buf=seg[offset:offset+sz].fade_in(padding).fade_out(padding)
        for i in range(n-1):
            buf+=seg[offset:offset+sz].fade_in(padding).fade_out(padding)
        return buf.fade_out(fadeout)

    def lookup(self, sample):
        return self.pool.keys.index(str(sample))
        
if __name__=="__main__":
    pass
            
