"""
- https://github.com/beats/acid-banger/blob/main/src/pattern.ts
"""

import yaml

Kick, Snare, Hats, OpenHat, ClosedHat = "kk", "sn", "ht", "oh", "ch"

Instruments = [Kick, Snare, OpenHat, ClosedHat]

Channels = [Kick, Snare, Hats]

ChannelMapping=yaml.safe_load("""
kk: 
 - kk
sn:
 - sn
ht:
 - oh
 - ch
""")

Electro, FourFloor, Triplets, Offbeats, Closed, Backbeat, Skip, Empty = "electro", "fourfloor", "triplets", "offbeats", "closed", "backbeat", "skip", "empty"

Styles={Kick: [Electro, FourFloor, Triplets],
        Snare: [Backbeat, Skip],
        Hats: [Offbeats, Closed]}

SVDrum, Drum, Sampler = "svdrum", "Drum", "Sampler"

class SampleKey:

    def __init__(self, value):
        self.value=value

    def expand(self):
        tokens=self.value.split(":")
        name, id = tokens[0], int(tokens[1])
        if tokens[0]==SVDrum:
            return {"mod": Drum,
                    "id": id}
        else:
            return {"mod": Sampler,
                    "key": {"bank": name,
                            "id": id}}

class TrigGenerator(dict):
    
    def __init__(self, samples, offset=0, volume=1):
        dict.__init__(self)
        self.samples={k: SampleKey(v).expand()
                      for k, v in samples.items()}
        self.offset=offset
        self.volume=volume

    def generate(self, style, q, n):
        fn=getattr(self, style)
        for i in range(n):
            fn(q, i)
        return self
        
    def add(self, i, v):
        trig=dict(self.samples[v[0]])
        trig["vel"]=v[1]*self.volume
        self[i+self.offset]=trig

    def fourfloor(self, q, i, k=Kick):
        if i % 4 == 0:
            self.add(i, (k, 0.9))
        elif i % 2 == 0 and q.random() < 0.1:
            self.add(i, (k, 0.6))

    def electro(self, q, i, k=Kick):
        if i == 0:
            self.add(i, (k, 1))
        elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5) or
              q.random() < 0.05):
            # self.add(i, (k, 0.9*q.random()))
            self.add(i, (k, 0.2+0.7*q.random()))

    def triplets(self, q, i, k=Kick):
        if i % 16  in [0, 3, 6, 9, 14]:
           self.add(i, (k, 1))
           
    def backbeat(self, q, i, k=Snare):
        if i % 8 == 4:
            self.add(i, (k, 1))

    def skip(self, q, i, k=Snare):
        if i % 8 in [3, 6]:
            self.add(i, (k, 0.6+0.4*q.random()))
        elif i % 2 == 0 and q.random() < 0.2:
            self.add(i, (k, 0.4+0.2*q.random()))
        elif q.random() < 0.1:
            self.add(i, (k, 0.2+0.2*q.random()))

    def offbeats(self, q, i,
                 ko=OpenHat,
                 kc=ClosedHat):
        if i % 4 == 2:
            self.add(i, (ko, 0.4))
        elif q.random() < 0.3:
            k = kc if q.random() < 0.5 else ko
            # self.add(i, (k, 0.2*q.random()))
            self.add(i, (k, 0.1+0.1*q.random()))

    def closed(self, q, i,
               k=ClosedHat):
        if i % 2 == 0:
            self.add(i, (k, 0.4))
        elif q.random() < 0.5:
            # self.add(i, (k, 0.3*q.random()))
            self.add(i, (k, 0.1+0.2*q.random()))
        
if __name__ == "__main__":
    pass
