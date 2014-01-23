import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
from tests.multimedia_data import multimediaData as md
from pimpy.video import Video
from pimpy.video.cbr import ContentBasedRetrieval


class CBRTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        video_uri = md().video_uri
        video = Video(video_uri)
        self.video_req = Video(video_uri,begin=60,end=70)
        self.cbr = ContentBasedRetrieval(video)

    def test_cbr(self):
        res = self.cbr.find(self.video_req)
        self.assertEqual(res,[1438])
    
if __name__ == '__main__':
    unittest.main()
