import os, re, yaml, zipfile

BanksDir="octavox/projects/picobeats/banks"

Patterns=yaml.safe_load("""
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

def matches(text, patterns=Patterns):
    text=text.lower()
    for key in patterns:
        for pat in patterns[key]:
            if re.search(pat, text):
                return key
    return None

def curate_banks(dirname=BanksDir):
    pool={}
    for filename in os.listdir(dirname):
        zf=zipfile.ZipFile("%s/%s" % (dirname,
                                      filename))
        for item in zf.infolist():
            key=matches(item.filename)
            if key:
                pool.setdefault(key, [])
                pool[key].append([filename,
                                  item.filename])
    return pool
                
if __name__=="__main__":
    pool=curate_banks()
    import json
    print (json.dumps(pool,
                      indent=2))
