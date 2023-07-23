"""
- https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
"""

def fourfloor(q, i, d, k):
    if i % 4 == 0 and q.random() < d:
        return (k, 0.9)
    elif i % 2 == 0 and q.random() < 0.1*d:
        return (k, 0.6)

def electro(q, i, d, k):
    if i == 0 and q.random() < d:
        return (k, 1)
    elif ((i % 2 == 0 and i % 8 != 4 and q.random() < 0.5*d) or
          q.random() < 0.05*d):
        return (k, 0.9*q.random())

def triplets(q, i, d, k):
    if i % 16  in [0, 3, 6, 9, 14] and q.random() < d:
        return (k, 1)

def backbeat(q, i, d, k):
    if i % 8 == 4 and q.random() < d:
        return (k, 1)

def skip(q, i, d, k):
    if i % 8 in [3, 6] and q.random() < d:
        return (k, 0.6+0.4*q.random())
    elif i % 2 == 0 and q.random() < 0.2*d:
        return (k, 0.4+0.2*q.random())
    elif q.random() < 0.1*d:
        return (k, 0.2+0.2*q.random())

def offbeats(q, i, d, ko, kc):
    if i % 4 == 2 and q.random() < d:
        return (ko, 0.4)
    elif q.random() < 0.3*d:
        k = ko if q.random() < 0.5 else kc
        return (kc, 0.2*q.random())

def closed(q, i, d, k):
    if i % 2 == 0 and q.random() < d:
        return (k, 0.4)
    elif q.random() < 0.5*d:
        return (k, 0.3*q.random())

if __name__=="__main__":
    pass
