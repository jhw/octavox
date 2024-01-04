from pydub import AudioSegment

import os

if __name__=="__main__":
    if not os.path.exists("tmp/slicedemo"):
        os.makedirs("tmp/slicedemo")
    audio=AudioSegment.from_wav("tmp/samplebeats/wav/2024-01-04-06-51-27-random-official-place.wav")
    sliceduration=2000
    for i in range(32):
        starttime=i*sliceduration
        endtime=starttime+sliceduration
        segment=audio[starttime:endtime].fade_in(5).fade_out(5)
        filename="tmp/slicedemo/slice-%i.wav" % i
        segment.export(filename, format="wav")
