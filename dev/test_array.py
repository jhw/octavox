import re

if __name__=="__main__":
    import sys
    print (re.search("^(\\d+(x\\d+)?\\|)*\\d+(x\\d+)?$", sys.argv[1]))
