import re, traceback

def matches_number(value):
    return re.search("^\\-?\\d+(\\.\\d+)?$", value)!=None

def matches_int(value):
    return re.search("^\\-?\\d+$", value)!=None

def matches_array(value):
    return re.search("^(\\d+(x\\d+)?\\|)*\\d+(x\\d+)?$", value)!=None

def matches_str(value):
    return True

def parse_number(value):
    return int(value) if matches_int(value) else float(value)

def parse_int(value):
    return int(value)

def parse_array(line):
    values=[]
    for chunk in line.split("|"):
        if "x" in chunk:
            n, v = [int(tok) for tok in chunk.split("x")]
            values+=[v for i in range(n)]
        else:
            values.append(int(chunk))
    return values

def parse_str(value):
    return value

def parse_line(config=[]):
    def decorator(fn):
        def wrapped(self, line):
            try:
                args=[tok for tok in line.split(" ") if tok!='']
                if len(args) < len(config):
                    raise RuntimeError("please enter %s" % ", ".join([item["name"]
                                                                      for item in config]))
                kwargs={}
                for item, argval in zip(config, args[:len(config)]):
                    matcherfn=eval("matches_%s" % item["type"])
                    if not matcherfn(argval):
                        raise RuntimeError("%s must be a(n) %s" % (item["name"],
                                                                   item["type"]))
                    parserfn=eval("parse_%s" % item["type"])
                    kwargs[item["name"]]=parserfn(argval)
                return fn(self, **kwargs)
            except RuntimeError as error:
                print ("ERROR: %s" % str(error))
            except Exception as error:
                print ("EXCEPTION: %s" % ''.join(traceback.TracebackException.from_exception(error).format()))
        return wrapped
    return decorator

if __name__=="__main__":
    pass
