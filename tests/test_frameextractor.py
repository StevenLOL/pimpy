import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
from tests.multimedia_data import multimediaData as md
from pimpy.video import Video
from pimpy.video.frameextractor import FrameExtractor 

class FrameExtractorTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.video_uri = md().video_uri
        video = Video(self.video_uri)
        self.fe = FrameExtractor(video)

    def test_saveframes(self):
        res = self.fe.saveframes(range(1440,1680),"/tmp")
        video = Video(self.video_uri,begin=60,end=70)
        fe = FrameExtractor(video)
        fe.saveframes(range(0,220),"/tmp")
        
if __name__ == '__main__':
    unittest.main()
