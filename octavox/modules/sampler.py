from rv.modules.sampler import Sampler as RVSampler

from rv.note import NOTE as RVNOTE

# from scipy.io import wavfile
from octavox.modules.utils import wavfile

import warnings

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
        for i, samplekey in enumerate(self.samplekeys):
            self.note_samples[notes[i]]=i
            audio=banks.get_wavfile(samplekey)
            """
            - at this point you may want to modify audio for slice information, depending on what's happening with samplekey
            """
            self.load(audio, i)
            sample=self.samples[i]
            sample.relative_note+=(root-i)

    def lookup(self, samplekey):
        return self.samplestrings.index(str(samplekey))
        
if __name__=="__main__":
    pass
            
