from pydub import AudioSegment

import io, zipfile

if __name__=="__main__":
    zf=zipfile.ZipFile("tmp/banks/default.zip")
    wavfile=zf.open("63 FUGUE.wav", 'r')
    audio=AudioSegment.from_file(io.BytesIO(wavfile.read()))
    print (audio.duration_seconds)
    buf=io.BytesIO()
    audio[:1000].fade_out(20).export(buf, format="wav")
    with open("tmp/fugue.wav", 'wb') as f:
        f.write(buf.getvalue())
