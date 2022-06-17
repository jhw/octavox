import os, re

def cli_base(item, matcher, parser):
    while True:
        resp=input("%s: " % item["description"])
        if resp=="":
            if "default" in item:
                print ("INFO: using %s %s" % (item["key"],
                                              item["default"]))
                return item["default"]
        elif matcher(resp, item):
            value=parser(resp, item)
            if value!=None:
                return value
        elif resp in "qQ":
            raise RuntimeError("exit")

def cli_enum(item):
    def matcher(resp, item):
        return True
    def parser(resp, item):
        if resp not in item["options"]:
            print ("WARNING: %s is not a valid option" % resp)
            return None
        return resp
    return cli_base(item, matcher, parser)
        
def cli_int(item):
    def matcher(resp, item):
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
    def matcher(resp, item):
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
    def matcher(resp, item):
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
    def matcher(resp, item):
        return re.search("^\\s*y|n\\s*$", resp, re.I)!=None
    def parser(resp, item):
        return resp.lower()=="y"
    return cli_base(item, matcher, parser)

def cli_file(item):
    if not os.path.isdir(item["root"]):
        raise RuntimeError("%s root is not a directory" % item["key"])
    def matcher(resp, item):
        matches=[filename
                 for filename in os.listdir(item["root"])
                 if resp in filename]
        if len(matches) > 1:
            print ("WARNING: multiple matches found [%s]" % ", ".join(matches))
            return False
        elif matches==[]:
            print ("WARNING: no matches found")
            return False
        else:
            return True
    def parser(resp, item):
        matches=[filename 
                 for filename in os.listdir(item["root"])
                 if resp in filename]
        filename=matches.pop()
        print ("INFO: using %s" % filename)
        return "%s/%s" % (item["root"],
                          filename)
    return cli_base(item, matcher, parser)

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
        - key: my_enum
          description: my_enum
          type: enum
          options:
          - hello
        - key: my_int
          description: my_int
          type: int
        """)
        resp=cli(conf)
        print ()
        print (resp)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
