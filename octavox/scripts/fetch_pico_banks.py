import json, os, re, urllib.request, zipfile

PicoDrum="http://data.ericasynths.lv/picodrum/"

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

def clean_filename(filename):
    tokens=filename.split(".")
    handle, fileext = ".".join(tokens[:-1]), tokens[-1]
    cleanhandle=" ".join([tok for tok in [re.sub("\\W", "", tok)
                                          for tok in re.split("\\s", handle)]
                          if tok!=''])                         
    return "%s.%s" % (cleanhandle, fileext)

def generate(packname, packfile):
    zfname="tmp/picobeats/banks/%s.zip" % packname.replace(" ", "-").lower()
    zf=zipfile.ZipFile(zfname, 'w')
    buf=fetch_bin(packfile)
    blocks=filter_blocks(buf)
    for i, blockname, block in blocks:
        filename=clean_filename(blockname.decode("utf-8"))
        zf.writestr(filename, block)        

if __name__=="__main__":
    try:
        for path in ["tmp/picobeats/banks"]:
            if not os.path.exists(path):
                os.makedirs(path)            
        for packname, packfile in pack_list().items():
            print (packname)
            generate(packname, packfile)
            # break # TEMP
    except RuntimeError as error:
        print ("Error: %s" % str(error))
        

