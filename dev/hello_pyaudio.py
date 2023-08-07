import io, pyaudio, wave, zipfile

CHUNK=1024

"""
- https://people.csail.mit.edu/hubert/pyaudio/docs/
"""

def play_wav(wavfile):
    with wave.open(io.BytesIO(wavfile.read()), 'rb') as wf:
        print ("Number of channels", wf.getnchannels())
        print ("Sample width", wf.getsampwidth())
        print ("Frame rate.", wf.getframerate())
        print ("Number of frames", wf.getnframes())
        p=pyaudio.PyAudio()
        stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),
                      channels=wf.getnchannels(),
                      rate=wf.getframerate(),
                      output=True)
        while len(data := wf.readframes(CHUNK)): 
            stream.write(data)
        stream.close()
        p.terminate()
        
if __name__=="__main__":
    zf=zipfile.ZipFile("octavox/banks/pico/default.zip")
    play_wav(zf.open("62 JUNGLE BREAK.wav", 'r'))
