import os, re, zipfile

class SVBanks(dict):

    def __init__(self,
                 root,
                 filterfn=lambda x: x.endswith(".zip")):
        dict.__init__(self)        
        for filename in os.listdir(root):
            if not filterfn(filename):
                continue
            path="%s/%s" % (root, filename)
            self[filename]=zipfile.ZipFile(path)
        
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

if __name__=="__main__":
    print (SVBanks("octavox/projects/picobeats/banks"))

