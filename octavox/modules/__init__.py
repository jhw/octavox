import importlib, random

def load_class(path):
    try:
        tokens=path.split(".")            
        modpath, classname = ".".join(tokens[:-1]), tokens[-1]
        module=importlib.import_module(modpath)
        return getattr(module, classname)
    except:
        raise RuntimeError("error importing %s" % path)

"""
- https://stackoverflow.com/questions/7331462/check-if-a-string-is-a-possible-abbrevation-for-a-name
"""

def is_abbrev(abbrev, text):
    abbrev=abbrev.lower()
    text=text.lower()
    words=text.split()
    if not abbrev:
        return True
    if abbrev and not text:
        return False
    if abbrev[0]!=text[0]:
        return False
    else:
        return (is_abbrev(abbrev[1:],' '.join(words[1:])) or
                any(is_abbrev(abbrev[1:],text[i+1:])
                    for i in range(len(words[0]))))

if __name__=="__main__":
    pass
