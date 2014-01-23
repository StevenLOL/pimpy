import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
from tests.multimedia_data import multimediaData as md
from pimpy.video import Video
from pimpy.video.goodshotdetector import ShotDetector


class ShotDetectorTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.ERROR)
        video_uri = md().video_uri
        print video_uri
        self.video = Video(video_uri,begin=0,end=42)
        self.sd = ShotDetector()
        self.cuts,self.diss = self.sd.process(self.video.uri,profile='relax')

    def test_cuts(self):
        res = numpy.array([38,275,336,359,376,388,432,443,452,458,473,542,565,603])
        assert_equal(self.cuts[:14],res)
        
    def test_dissolves(self):
        res = [[ 459,  465],
               [ 713,  718],
               [1293, 1301],
               [1515, 1519],
               [1605, 1613],
               [1937, 1943],
               [2184, 2192],                             
               [2396, 2404],
               [2439, 2444],
               [2482, 2486],
               [2488, 2494]]
        assert_equal(self.diss,res)
    
if __name__ == '__main__':
    unittest.main()
