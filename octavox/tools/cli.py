import os, re

def cli_base(item, matcher, parser):
    while True:
        resp=input("%s: " % item["description"])
        if resp=="":
            if "default" in item:
                print ("INFO: using %s %s" % (item["key"],
                                              item["default"]))
                return item["default"]
        elif matcher(resp):
            value=parser(resp, item)
            if value!=None:
                return value
        elif resp in "qQ":
            raise RuntimeError("exit")

def cli_int(item):
    def matcher(resp):
        return re.search("^\\s*\\d+\\s*$", resp)!=None
    def parser(resp, item):
        value=int(resp)
        if (("min" in item and value < item["min"]) or
            ("max" in item and value > item["max"])):
            print ("WARNING: %s exceeds limits" % item["key"])
            return None
        return value
    return cli_base(item, matcher, parser)

def cli_int_array(item):
    def matcher(resp):
        return re.search("^\\s*(\\d+\\s+)*\\d+\\s*$", resp)!=None
    def parser(resp, item):
        values=[]
        for token in re.split("\\s", resp):
            if token=='':
                continue
            value=int(token)
            if (("min" in item and value < item["min"]) or
                ("max" in item and value > item["max"])):
                print ("WARNING: %s exceeds limits" % item["key"])
                return None
            values.append(value)
        return values
    return cli_base(item, matcher, parser)
 
def cli_float(item):
    def matcher(resp):
        return re.search("^\\s*\\d+(\\.\\d+)?\\s*$", resp)!=None
    def parser(resp, item):
        value=float(resp)
        if (("min" in item and value < item["min"]) or
            ("max" in item and value > item["max"])):
            print ("WARNING: %s exceeds limits" % item["key"])
            return None        
        return value
    return cli_base(item, matcher, parser)

def cli_bool(item):
    def matcher(resp):
        return re.search("^\\s*(true)|(false)\\s*$", resp, re.I)!=None
    def parser(resp, item):
        return eval(resp.lower().capitalize())
    return cli_base(item, matcher, parser)

def cli_file(item):
    if not os.path.isdir(item["root"]):
        raise RuntimeError("%s root is not a directory" % item["key"])
    def matches(filename, item):
        return True if "pattern" not in item else re.search(item["pattern"], filename)!=None
    filenames=[filename for filename in os.listdir(item["root"])
               if matches(filename, item)]
    if filenames==[]:
        raise RuntimeError("no %s files found" % item["key"])
    for filename in reversed(sorted(filenames)):
        resp=re.sub("\\s", "", input("%s -> %s ? " % (item["description"],
                                                     filename)))
        if resp=="":
            continue
        elif resp in "yY":
            return "%s/%s" % (item["root"],
                              filename)
        elif resp in "qQ":
            raise RuntimeError("exit")
    raise RuntimeError("no file selected")
        
def cli(conf):
    values={}
    for item in conf:
        fn=eval("cli_%s" % item["type"])
        values[item["key"]]=fn(item)
    return values

if __name__=="__main__":
    try:
        import yaml
        conf=yaml.safe_load("""
        - key: my_int
          description: my_int
          type: int
        - key: my_float
          description: my_float
          type: float
        - key: my_file
          description: my_file
          type: file
          root: tmp/random/patches
        """)
        resp=cli(conf)
        print ()
        print (resp)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
