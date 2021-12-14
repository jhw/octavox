import re, os, zipfile

FilterFn=lambda x: x.endswith(".zip")

class Banks(dict):

    @classmethod
    def load(self,
             root="tmp/banks",
             filterfn=FilterFn):
        def keyfn(item):
            return "-".join(item.split(".")[0].split("-")[1:])

        banks=Banks()
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

if __name__=="__main__":
    print (Banks.load("tmp/banks/pico"))
