import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
from tests.multimedia_data import multimediaData as md
from pimpy.video import Video   

logging.basicConfig(level=logging.DEBUG)

class VideoTestCase(unittest.TestCase):
    def setUp(self): 
        self.uri = uri = md().video_uri
        self.video = Video(uri,begin=0,end=42)
        self.short_video = Video(uri,begin=0,end=5)

    def test_crc(self):
        from urlparse import urlparse 
        res = zlib.crc32(open(urlparse(self.uri).path).read())
        self.assertEqual(res,-1733083616,'CRC incorrect ')


    def test_list_features(self):
        lf =  self.video.list_features()
        self.assertTrue(len(lf)>0,'Pb with features available')
    
    def test_features_bindct_shape(self):
        bdct = self.video.get_feature('bindct')
        self.assertEqual(bdct.shape,(1006,1,64),'Wrong BinDCT Shape ')

    def test_features_sifts(self):
        sifts = self.short_video.get_feature('sift')        

    def test_features_bindct(self):
        bdct = self.video.get_feature('bindct')        
        import numpy 
        numpy.save('/tmp/t',bdct[1000])
        res_frame1000 = numpy.array([True, False, True, False,
                                     False, True, True, False,
                                     False, True,True, False,
                                     True, False, True, False,
                                     False, True, False, True,
                                     False, True, False, False,
                                     True, True, False, True,
                                     False, True,False, True,
                                     True, True, False, True,
                                     False, True, True, False,
                                     True, True, False, True,
                                     False, True, False, False,
                                     True, False,False, True,
                                     False, True, False, True,
                                     True, True, False, False,
                                     False, True, False, False],
                                    dtype=numpy.bool)
        assert_equal(bdct[1000][0],res_frame1000)
 
    def test_features_gists(self):
        gists = self.video.get_feature('gist')        
        self.assertEqual(gists.shape,(1006,1,960),'Wrong GISTS array shape ')        
        res = numpy.array([0.121677719057,
                           0.123909182847,
                           0.125051602721,
                           0.13605068624,
                           0.0544686727226])
        assert_almost_equal(gists[1000][0][:5],res)


    def test_features_histosGray(self):
        histos = self.video.get_feature('histogramgray')        
        histoframe1000 = histos[1000][0]
        res = numpy.array([50, 63, 30, 1, 0, 2, 3, 16, 10, 5, 4, 2])
        assert_equal(histoframe1000[:12],res)        

    def test_features_histosRGB(self):
        histos = self.video.get_feature('histogramrgb')        
        histoframe1000 = histos[1000]
        r = histoframe1000[0]
        res = numpy.array([54, 38, 11, 24, 16, 1, 2, 1, 4, 5, 9, 3])
        assert_equal(r[:12],res)        

    def test_features_histosSampled4dRGBA(self):
        histos = self.video.get_feature('histogramsampled4drgbamassnormed')
        histoframe1000 = histos[1000]
        r = histoframe1000[0]
        res = numpy.array([0.258680555556, 0.48997790404, 0.179253472222, 0.0720880681818])
        assert_almost_equal(r,res)        
 
    def test_features_surf(self):
        keypoints,vectors = self.short_video.get_feature('surf')
        d = vectors[100][0]
        res = numpy.array([-0.00045469,  0.00411998,  0.00298648,  0.01315304,  0.03659671])
        assert_almost_equal(d[:5],res)        


    def test_getcuts(self):
        cuts,diss = self.video.getcuts()
        res = numpy.array([38,275,336,359,376,388,432,443,452,458,473,542,565,603])
        assert_equal(cuts[:14],res)

    def test_getdissolve(self):
        cuts,diss = self.video.getcuts()
        res=[[ 459,  465],[ 713,  718],[1293, 1301]]
        assert_equal(diss[:3],res)


if __name__ == '__main__':
    unittest.main()
