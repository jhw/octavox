import yaml

if __name__=="__main__":
    try:
        from octavox.tools.cli import cli
        cliconf=yaml.safe_load("""
        - key: src
          description: source
          type: file
          root: tmp/samplebeats/wavs
        - key: nbeats
          description: "n(beats)"
          type: int
          min: 4
          default: 16
        - key: npatches
          description: "n(patches)"
          type: int
          min: 1
          default: 16
        """)
        import sys
        if len(sys.argv) >= 2:
            cliconf[0]["pattern"]=sys.argv[1]
        kwargs=cli(cliconf)
        from pydub import AudioSegment
        slices=AudioSegment.from_wav(kwargs["src"])
        print (len(slices))
        compressed=AudioSegment.empty()
        for i in range(3*kwargs["npatches"]):
            length=int(1000*kwargs["nbeats"]/8)
            offset=int(i*2*length)
            compressed+=slices[offset:offset+length]
        print (len(compressed))
        destfilename="%s-compressed.wav" % kwargs["src"].split(".")[0]
        compressed.export(destfilename,
                          format="wav")
    except RuntimeError as error:
        print ("Error: %s" % str(error))
