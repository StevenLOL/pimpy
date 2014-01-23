import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
from tests.multimedia_data import multimediaData as md
from pimpy.video import Video   

logging.basicConfig(level=logging.DEBUG)

class HDF5VideoTestCase(unittest.TestCase):
    def setUp(self):
        video_uri = md().video_uri
        #self.video = Video(video_uri,begin=10,end=11)
        self.video = Video(video_uri,begin=10,end=11)
        print "HDF5 file %s " % self.video.hdf5.filename

    def test_features(self):
        self.video.get_feature('histogramrgb')        
        self.video.get_feature('histogramsampled4drgbamassnormed')
        self.video.get_feature('bindct')      
        if "surf" in self.video.list_features():
            self.video.get_feature('surf')        
        if "sift" in self.video.list_features():
            self.video.get_feature('sift')        
        if "gist" in self.video.list_features():
            self.video.get_feature('gist')        

    def test_full_video(self):
        video_uri = md().video_uri
        self.video = Video(video_uri,hdf5file="test.hdf5")
        self.video.get_feature('bindct')        

if __name__ == '__main__':
    unittest.main()
