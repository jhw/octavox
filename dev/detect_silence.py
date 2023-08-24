"""
- script to see how well pydub captures silence, forward and reversed
"""

from octavox.modules.banks import SVBanks

from pydub import AudioSegment, silence

import boto3, os

if __name__=="__main__":
    try:
        bucketname=os.environ["OCTAVOX_ASSETS_BUCKET"]
        if bucketname in ["", None]:
            raise RuntimeError("OCTAVOX_ASSETS_BUCKET does not exist")
        s3=boto3.client("s3")
        banks=SVBanks.initialise(s3, bucketname)
        pool=banks.filter_pool({"ht": "hat"})
        for sample in pool:
            print ("--- %s ---" % str(sample))
            src=banks.get_wavfile(sample)
            seg=AudioSegment.from_file(src)
            rev=seg.reverse()
            print ("length: %i" % len(rev))
            print ("silent: %s" % silence.detect_silence(rev))
            print ("non-silent: %s" % silence.detect_nonsilent(rev))
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
        

