from rv.modules.sampler import Sampler as RVSampler

from rv.note import NOTE as RVNOTE

import re, os, warnings, zipfile

# from scipy.io import wavfile
from octavox.modules.utils import wavfile

warnings.simplefilter("ignore", wavfile.WavFileWarning)

Sampler="Sampler"

class SVBanks(dict):

    @classmethod
    def load(self,
             root="tmp/banks",
             filterfn=lambda x: x.endswith(".zip")):
        def keyfn(item):
            return item.split(".")[0]
        banks=SVBanks()
        for filename in os.listdir(root):
            if not filterfn(filename):
                continue
            key=keyfn(filename)
            path="%s/%s" % (root, filename)
            banks[key]=zipfile.ZipFile(path)
        return banks
    
    def __init__(self):
        dict.__init__(self)        

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
        def lookup(self, key):        
            if key["bank"] not in self:
                raise RuntimeError("bank %s not found" % key["bank"])
            wavfiles=sorted(self[key["bank"]].infolist(),
                            key=sorter)
            if key["id"] >= len(wavfiles):
                raise RuntimeError("id %i exceeds bank size" % key["id"])
            return wavfiles[key["id"]]
        wavfile=lookup(self, key)
        bankname=key["bank"]
        return self[bankname].open(wavfile, 'r')

class SVPatches(list):

    def ___init__(self, patches):
        list.__init__(self, patches)

    """
    - returns list of all unique sample keys listed in patches
    - so you only need to load used samples from banks, thereby reducing overall sunvox file size
    - order not important because patch is updated with note of whatever slot a particular sample is inserted into
    """
            
    @property
    def sample_keys(self):
        def keyfn(key):
            return "%s:%i" % (key["bank"],
                              key["id"])
        keys={}
        for patch in self:
            for track in patch["tracks"]:
                if track["type"]=="trig":
                    trigs=track["notes"]
                    for trig in trigs.values():
                        if trig and trig["mod"]==Sampler:
                            keys[keyfn(trig["key"])]=trig["key"]
        return list(keys.values())

    def add_sample_ids(self, mapping):
        for patch in self:
            for track in patch["tracks"]:
                if track["type"]=="trig":
                    trigs=track["notes"]
                    for trig in trigs.values():
                        if trig and trig["mod"]==Sampler:
                            trig["id"]=mapping.index(trig["key"])

class SVSampler(RVSampler):

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

    def initialise(self, banks, patches,
                   maxslots=120,
                   debug=False):
        patches=SVPatches(patches)
        notes=list(RVNOTE)
        root=notes.index(RVNOTE.C5)
        samplekeys=patches.sample_keys
        if len(samplekeys) > maxslots:
            raise RuntimeError("sampler max slots exceeded")
        if debug:
            print ("%i sampler slots used" % len(samplekeys))
        patches.add_sample_ids(samplekeys)
        for i, samplekey in enumerate(samplekeys):
            self.note_samples[notes[i]]=i
            src=banks.get_wavfile(samplekey)
            self.load(src, i)
            sample=self.samples[i]
            sample.relative_note+=(root-i)

if __name__=="__main__":
    print (SVBanks.load("tmp/banks/pico"))
            
