import io, zipfile

from pydub import AudioSegment

if __name__=="__main__":
    zf=zipfile.ZipFile("octavox/banks/pico/default.zip")
    wavfile=zf.open("63 FUGUE.wav", 'r')
    audio=AudioSegment.from_file(io.BytesIO(wavfile.read()))
    print (audio.duration_seconds)
    audio[:1000].export("tmp/fugue.wav", format="wav")
