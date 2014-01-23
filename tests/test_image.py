import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
import cv 
from tests.multimedia_data import multimediaData as md
from pimpy.image import Image

logging.basicConfig(level=logging.DEBUG)

class ImageTestCase(unittest.TestCase):
    def setUp(self):
        self.im = Image()
        im_path = md().image_path
        self.im.load(im_path)    

    def test_save(self):
        outfile = tempfile.NamedTemporaryFile().name
        outfile += ".jpg"
        self.im.save(outfile)
        res = zlib.crc32(open(outfile).read())
        self.assertEqual(res,-713340435,'CRC incorrect ')

    def test_list_features(self):
        lf =  self.im.list_features()
        self.assertTrue(len(lf)>0,'No Features available')

    def test_features_sift(self):    
        sifts  = self.im.get_feature('sift')#,**kwargs)
        res = numpy.array([8,23,44,10,0,0,0])
        assert_equal(sifts[0][3][0:7],res)

    def test_features_bindct(self):
        bdct = self.im.get_feature('bindct')
        res = numpy.array([1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,1,1,0,0,0,0,0,1,1,0,1,1,0,0,0,1,1,1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1,1,1],dtype=numpy.bool)
        assert_equal(bdct,res)

    def test_features_gist(self):
        u""" test first 5 values of the gist """
        gist = self.im.get_feature('gist')
        res = numpy.array([0.01281233, 0.01326025, 0.02414293, 0.03138399, 0.00965376, 0.01810894],dtype='float32')
        assert_almost_equal(gist[0:6],res)

    def test_features_histo_gray(self):
        u""" test first values of the histos"""        
        h = self.im.get_feature('histogramgray')
        res  = numpy.array([1952, 1950, 1879, 1864, 1682, 1716, 1523, 1467, 1410, 1362])
        assert_equal(h[100:110],res)

    def test_features_histo_rgb(self):
        u""" test first values of the histos"""        
        r,g,b,a = self.im.get_feature('histogramrgb')
        r_histo = r[0]
        res  = numpy.array([1418, 1384, 1319, 1342, 1156, 1120,  955,  969,  828,  782])
        assert_equal(r_histo[100:110],res)

    def test_features_histo_rgb_sampled_4d(self):
        u""" test first values of the histos"""        
        kwargs = {'mass_normed' : True}
        r,g,b,a = self.im.get_feature('histogramsampled4drgba',**kwargs)
        res  = numpy.array([ 0.27911377, 0.41459656, 0.24352646, 0.06276321],dtype='float32')
        assert_almost_equal(g,res)


    def test_features_goodfeaturestotrack(self):    
        feats = self.im.get_feature('goodfeaturestotrack')
        print len(feats)
        x1, y1 = feats[0]
        x2, y2 = feats[1]

        g = numpy.array([[x1, y1],[x2,y2]])

        #res = numpy.array([[117,308],[211,267]])
        #res = numpy.array([[157,377],[180,433]])
        #res = numpy.array([[157,377],[180,433]])
        res = numpy.array([[157,377],[180,433]])
        assert_almost_equal(g,res)

        from pimpy.image.features.goodfeaturestotrack import GoodFeaturesToTrack
        gftt = GoodFeaturesToTrack()
        gftt.get(self.im)
        gftt.save_image_with_features("/tmp/gftt.jpg")


    def test_features_surf(self):    
        #kwargs = {'mass_normed' : True}
        keypoints,descriptors  = self.im.get_feature('surf')#,**kwargs)
        from pimpy.image.features.surf import Surf
        surf = Surf()
        surf.get(self.im)
        out = tempfile.NamedTemporaryFile(suffix='.jpg').name
        surf.save_image_with_features(out)


if __name__ == '__main__':
    unittest.main()
