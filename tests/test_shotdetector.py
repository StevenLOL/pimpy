import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
from tests.multimedia_data import multimediaData as md
from pimpy.video import Video
from pimpy.video.shotdetector import ShotDetector


class ShotDetectorTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        video_uri = md().video_uri
        self.video = Video(video_uri,begin=0,end=42)
        self.sd = ShotDetector()

    def test_dctcuts(self):
        cuts = self.sd.detect(self.video)
        res = numpy.array([  0,  39, 276, 337, 360, 377, 389, 433, 444, 453, 459, 474, 543, 553])
        assert_equal(cuts[:14],res)
        
    def test_cuts_histo_smooth(self):
        self.sd.detect(self.video)
        cuts = self.sd.smoothbyhisto()
        res = numpy.array([  0,  39, 276, 337, 360, 377, 389, 433, 444, 453, 459, 474, 543, 553])
        assert_equal(cuts[:14],res)
    

if __name__ == '__main__':
    unittest.main()
