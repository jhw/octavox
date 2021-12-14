import json, os, urllib.request, yaml

PicoDrum="http://data.ericasynths.lv/picodrum/"

Patterns=yaml.safe_load("""
kick:
  - kick
  - kik
  - kk
  - bd
bass:
  - bass
snare:
  - snare
  - sn
  - sd
clap:
  - clap
  - clp
  - cp
  - rs
  - tom
  - tm
hat:
  - open
  - closed
  - hat
  - ht
  - oh
  - ch
perc:
  - perc
  - prc
glitch:
  - blip
  - glitch
  - gltch  
  - devine
""")

def fetch_json(path):
    return json.loads(urllib.request.urlopen(PicoDrum+path).read())

def pack_list():
    return {item["name"]:item["file"]
            for item in fetch_json("pack_list.json")}

def fetch_bin(path):
    return urllib.request.urlopen(PicoDrum+path).read()

def filter_blocks(buf):
    def format_block(i, block):
        tokens=block.split(b"data")
        name=tokens[0][1:-1]
        data=(b"data".join(tokens[1:]))
        offset=data.index(b"RIFF")
        return (i, name, data[offset:])
    return [format_block(i, block.split(b"<?xpacket begin")[0])
            for i, block in enumerate(buf.split(b"\202\244name")[1:])]

def matches(text, patterns=Patterns):
    text=text.lower()
    for key in patterns:
        for pat in patterns[key]:
            if pat in text:
                return key
    return None
        
def generate(packname, packfile, samples):
    buf=fetch_bin(packfile)
    blocks=filter_blocks(buf)
    for i, blockname, block in blocks:
        blockname=str(blockname)
        key=matches(blockname)
        if key:
            samples.setdefault(key, [])
            samples[key].append("%s:%i" % (packname, i))
    return samples

if __name__=="__main__":
    try:
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        samples={}
        for packname, packfile in pack_list().items():
            print (packname)
            bankname=packname.replace(" ", "-").lower()
            generate(bankname, packfile, samples)
        for path in ["tmp",
                     "tmp/banks",
                     "tmp/banks/pico"]:
            if not os.path.exists(path):
                os.makedirs(path)            
        with open("tmp/banks/pico/samples.yaml", 'w') as f:            
            f.write(yaml.safe_dump(samples,
                                   default_flow_style=False))
    except RuntimeError as error:
        print ("Error: %s" % str(error))
        

