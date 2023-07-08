import os, re, yaml, zipfile

BanksDir="octavox/projects/picobeats/banks"

DefaultPatterns=yaml.safe_load("""
kk:
  - kick
  - kik
  - kk
  - bd
  - bass
sn:
  - snare
  - sn
  - sd
  - clap
  - clp
  - cp
ht:
  - open
  - closed
  - hat
  - ht 
  - oh
  - ch # avoid glitch match
  - perc
  - prc
""")

def matches(text, patterns):
    text=text.lower()
    for key in patterns:
        for pat in patterns[key]:
            if re.search(pat, text):
                return key
    return None

def curate_pool(patterns, dirname=BanksDir):
    pool={}
    for filename in os.listdir(dirname):
        zf=zipfile.ZipFile("%s/%s" % (dirname,
                                      filename))
        for item in zf.infolist():
            key=matches(item.filename, patterns)
            if key:
                pool.setdefault(key, [])
                pool[key].append([filename,
                                  item.filename])
    return pool
                
if __name__=="__main__":
    for path in ["tmp/picobeats/pools"]:
        if not os.path.exists(path):
            os.makedirs(path)            
    pool=curate_pool(patterns=DefaultPatterns)
    with open("tmp/picobeats/pools/default.yaml", 'w') as f:
        f.write(yaml.safe_dump(pool,
                               default_flow_style=False))
