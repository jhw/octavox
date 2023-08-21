import boto3, io, json, os, re, urllib.request, zipfile

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

def clean_filename(filename, i):
    tokens=filename.split(".")
    handle, fileext = ".".join(tokens[:-1]), tokens[-1]
    tokens=[re.sub("^\\d+", "", re.sub("\\W", "", tok))
            for tok in re.split("\\s", handle)]
    prefix="0%i" % i if i < 10 else str(i)
    cleanhandle=" ".join([prefix]+[tok for tok in tokens
                                   if tok!=''])
    return "%s.%s" % (cleanhandle, fileext)

def upload(s3, bucketname, packname, packfile):
    s3key="banks/pico-%s.zip" % packname.replace(" ", "-").lower()
    blocks=filter_blocks(fetch_bin(packfile))
    buf=io.BytesIO()
    with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False) as zf:
        for i, blockname, block in blocks:
            filename=clean_filename(blockname.decode("utf-8"), i)
            zf.writestr(filename, block)
    body=buf.getvalue()
    print ("%s [%i]" % (s3key, len(body)))
    s3.put_object(Bucket=bucketname,
                  Key=s3key,
                  Body=body,
                  ContentType="application/zip")

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        for packname, packfile in pack_list().items():
            upload(s3, bucketname, packname, packfile)
            # break # TEMP
    except RuntimeError as error:
        print ("Error: %s" % str(error))
        

