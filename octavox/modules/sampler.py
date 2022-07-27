from rv.modules.sampler import Sampler as RVSampler

from rv.note import NOTE as RVNOTE

import os, random, re, warnings, zipfile

# from scipy.io import wavfile
from octavox.modules.utils import wavfile

warnings.simplefilter("ignore", wavfile.WavFileWarning)

Sampler="Sampler"

class SVBanks(dict):

    def __init__(self,
                 root,
                 filterfn=lambda x: x.endswith(".zip")):
        dict.__init__(self)        
        def keyfn(item):
            return item.split(".")[0]
        for filename in os.listdir(root):
            if not filterfn(filename):
                continue
            key=keyfn(filename)
            path="%s/%s" % (root, filename)
            self[key]=zipfile.ZipFile(path)
        
    """
    - find sample wavfile associated with particular bank and id
    - note is an index, not the name of the wavfile itself
    - note wavfiles are sorted by name in this index
    - this is done so you can index samples from zero, rather than the pico filename convention which starts them at one
    """
        
    def get_wavfile(self, key):
        def sorter(zf):
            stub=zf.filename.split(".")[0]
            return int(stub) if re.search("^\\d+$", stub) else stub
        def lookup(self, bank, id):
            if bank not in self:
                raise RuntimeError("bank %s not found" % bank)
            wavfiles=sorted(self[bank].infolist(),
                            key=sorter)
            if id >= len(wavfiles):
                raise RuntimeError("id %i exceeds bank size" % id)
            return wavfiles[id]
        bank, id = key.split(":")
        wavfile=lookup(self, bank, int(id))
        return self[bank].open(wavfile, 'r')

    @property
    def random_key(self):
        modnames=list(self.keys())
        mod=random.choice(modnames)
        n=len(self[mod].infolist())
        i=random.choice(range(n))
        return "%s:%i" % (mod, i)
    
class SVSampler(RVSampler):

    def __init__(self, samplekeys,  maxslots=120, *args, **kwargs):                
        RVSampler.__init__(self, *args, **kwargs)
        if len(samplekeys) > maxslots:
            raise RuntimeError("sampler max slots exceeded")
        self.samplekeys=samplekeys

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

    def initialise(self, banks, patches):
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        for i, samplekey in enumerate(self.samplekeys):
            self.note_samples[notes[i]]=i
            src=banks.get_wavfile(samplekey)
            self.load(src, i)
            sample=self.samples[i]
            sample.relative_note+=(root-i)

if __name__=="__main__":
    print (SVBanks.load("tmp/banks/pico"))
            
