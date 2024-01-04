"""
- rv/tools/export.py
"""

import numpy as np

# from scipy.io import wavfile
from octavox.core.utils import wavfile

# from sunvox import Slot
from sunvox.slot import Slot as RVSlot
from sunvox.buffered import BufferedProcess as RVBufferedProcess
from sunvox.buffered import float32, int16

from tqdm import tqdm

def export_wav(project, filename,
               data_type=float32, # int16, float32
               channels=2, # 1, 2
               freq=44100): # 44100, 48000
    p=RVBufferedProcess(freq=freq,
                        size=freq,
                        channels=channels,
                        data_type=data_type)
    slot=RVSlot(project, process=p)
    length=slot.get_song_length_frames()
    output=np.zeros((length, 2), data_type)
    position=0
    slot.play_from_beginning()
    pbar=tqdm(total=length,
              unit_scale=True,
              unit="frame",
              dynamic_ncols=True)
    with pbar as pbar:
        while position < length:
            buffer=p.fill_buffer()
            end_pos=min(position+freq, length)
            copy_size=end_pos-position
            output[position:end_pos]=buffer[:copy_size]
            position=end_pos
            pbar.update(copy_size)
    wavfile.write(filename, freq, output)
    p.deinit()
    p.kill()

if __name__ == "__main__":
    pass
