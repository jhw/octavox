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
        
    def load(self, src, slot, **kwargs):
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
        self.samplestrings=[str(samplekey)
                            for samplekey in samplekeys]
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        segments={}
        for i, samplekey in enumerate(self.samplekeys):
            self.note_samples[notes[i]]=i
            src=banks.get_wavfile(samplekey)
            if "params" in samplekey:
                segkey=str(samplekey)
                if segkey not in segments:
                    segments[segkey]=AudioSegment.from_file(src)                
                segment=segments[segkey]
                buf=io.BytesIO()
                """
                - include slice/cutoff info here ie segment[j:k]
                """
                ext=samplekey["file"].split(".")[-1]
                segment.export(buf, format=ext)            
                self.load(buf, i)
            else:
                self.load(src, i)
            sample=self.samples[i]
            sample.relative_note+=(root-i)

    def lookup(self, samplekey):
        return self.samplestrings.index(str(samplekey))
        
if __name__=="__main__":
    pass
            
