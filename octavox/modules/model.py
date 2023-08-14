from octavox.modules.project import SVTrigs

from octavox.modules import load_class

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
