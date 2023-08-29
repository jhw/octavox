import re, urllib.parse

def parse_qs(qs):
    def parse_value(v):
        if re.search("^\\-?\\d+\\.\\d+$", v):
            return float(v)
        elif re.search("^\\-?\\d+$", v):
            return int(v)
        else:
            return v
    url=urllib.parse.urlparse("?"+qs)    
    return {k:parse_value(v)
            for k, v in urllib.parse.parse_qsl(url.query)}
    
if __name__=="__main__":    
    print (parse_qs("a=1&b=2"))
    
