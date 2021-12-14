import random

def new_color(offset=64, contrast=128, n=16):
    def random_color(offset):
        return [int(offset+random.random()*(255-offset))
                for i in range(3)]
    for i in range(n):
        color=random_color(offset)
        if (max(color)-min(color)) > contrast:
            return color
    return [127 for i in range(3)]

def mutate_color(color, contrast=32):
    values=range(-contrast, contrast)
    return [min(255, max(0, rgb+random.choice(values)))
            for rgb in  color]

if __name__=="__main__":
    pass
