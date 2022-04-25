SampleHold="sample_hold"

FXStyles=[SampleHold]

class FXGenerator(dict):
    
    def __init__(self, ctrl, offset=0):
        dict.__init__(self)
        self.ctrl=ctrl
        self.offset=offset

    def generate(self, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)
        return self

    def add(self, i, v):
        j=i+self.offset
        self[j]={"value": v,
                 "mod": self.ctrl["mod"],
                 "attr": self.ctrl["attr"]}
    
    def sample_hold(self, q, i):
        kwargs=self.ctrl["kwargs"][SampleHold]
        step=kwargs["step"]
        floor=kwargs["min"] if "min" in kwargs else 0
        ceil=kwargs["max"] if "max" in kwargs else 1
        inc=kwargs["inc"] if "inc" in kwargs else 0.25
        if 0 == i % step:
            v0=floor+(ceil-floor)*q.random()
            v=inc*int(0.5+v0/inc)
            self.add(i, v)
    
if __name__=="__main__":
    pass
