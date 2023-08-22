import random

Output= "Output"

class SVColor(list):

    @classmethod
    def randomise(self,
                  offset=64,
                  contrast=128,
                  n=16):
        def randomise(offset):
            return [int(offset+random.random()*(255-offset))
                    for i in range(3)]
        for i in range(n):
            color=randomise(offset)
            if (max(color)-min(color)) > contrast:
                return SVColor(color)
        return SVColor([127 for i in range(3)])
    
    def __init__(self, rgb=[]):
        list.__init__(self, rgb)

    def mutate(self,
               contrast=32):
        values=range(-contrast, contrast)
        return SVColor([min(255, max(0, rgb+random.choice(values)))
                        for rgb in self])

if __name__=="__main__":
    pass
    
