from octavox.modules import load_class

class SVTrigs(list):

    def __init__(self, nbeats, items=[]):
        list.__init__(self, items)
        self.nbeats=nbeats

    @property
    def tracks(self):
        tracks=SVTracks(self.nbeats)
        for trig in self:
            key=trig.track_key
            tracks.setdefault(key, [])
            tracks[key].append(trig)
        return tracks

"""
- SVTracks class is locally named a patch, for post- rendering convenience
"""
    
class SVTracks(dict):

    def __init__(self, nbeats, item={}):
        dict.__init__(self)
        self.nbeats=nbeats

    def filter_pool(self, keys):
        for track in self.values():
            for trig in track:
                if (hasattr(trig, "samplekey") and trig.samplekey):
                    keys.add(trig.samplekey)

    @property
    def grid(self):
        return [{note.i:note
                 for note in track}
                for key, track in self.items()]

class Machines(list):
    
    @classmethod
    def randomise(self,
                  machines,
                  **kwargs):
        return Machines([load_class(machine["class"]).randomise(machine=machine,
                                                                **kwargs)
                          for machine in machines])

    def __init__(self, machines):
        list.__init__(self, [load_class(machine["class"])(machine=machine)
                             for machine in machines])

    def clone(self):
        return Machines([machine.clone()
                           for machine in self])
    
class Patch(dict):

    @classmethod
    def randomise(self, density, machines, **kwargs):
        return Patch(machines=Machines.randomise(machines=machines,
                                                 **kwargs),
                     density=density)
        
    def __init__(self,
                 machines,
                 density):
        dict.__init__(self, {"machines": Machines(machines),
                             "density": density})
        
    def clone(self):
        return Patch(machines=self["machines"].clone(),
                     density=self["density"])
    
    def render(self,
               nbeats):
        trigs=SVTrigs(nbeats=nbeats)
        for machine in self["machines"]:
            machine.render(nbeats=nbeats,
                           trigs=trigs,
                           density=self["density"])
        return trigs.tracks

if __name__=="__main__":
    pass
