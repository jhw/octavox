if __name__=="__main__":
    from pydub import AudioSegment
    patches=AudioSegment.from_wav("dev/hello-world.wav")
    patches[:2000].export("tmp/fragment.wav", format="wav")
