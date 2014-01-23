import unittest,logging
from tests.test_image import ImageTestCase
from tests.test_video import VideoTestCase
from tests.test_shotdetector import ShotDetectorTestCase
from tests import test_shotdetector,test_goodshotdetector
from tests.test_cbr import CBRTestCase
from tests.test_video_clustering import VideoClusteringTestCase
from tests.test_frameextractor import FrameExtractorTestCase


logging.basicConfig(level=logging.DEBUG)

imagesuite = unittest.TestLoader().loadTestsFromTestCase(ImageTestCase)
videosuite = unittest.TestLoader().loadTestsFromTestCase(VideoTestCase)
shotdetectorsuite = unittest.TestLoader().loadTestsFromTestCase(test_shotdetector.ShotDetectorTestCase)
goodshotdetectorsuite = unittest.TestLoader().loadTestsFromTestCase(test_goodshotdetector.ShotDetectorTestCase)
CBRsuite  = unittest.TestLoader().loadTestsFromTestCase(CBRTestCase)
frameextractorsuite = unittest.TestLoader().loadTestsFromTestCase(FrameExtractorTestCase)
videoclustsuite = unittest.TestLoader().loadTestsFromTestCase(VideoClusteringTestCase)

alltests = unittest.TestSuite([videosuite,
                               imagesuite,
                               goodshotdetectorsuite,
                               shotdetectorsuite,
                               CBRsuite,
                               frameextractorsuite,
                               videoclustsuite])

if __name__ == '__main__':
    unittest.main()

