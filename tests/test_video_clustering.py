import unittest,logging
import zlib,tempfile,numpy
from numpy.testing import assert_equal,assert_almost_equal
from tests.multimedia_data import multimediaData as md
from pimpy.video import Video
from pimpy.video.cluster import gistClustering,histClustering,sigClustering
from pimpy.video.dendogram import VideoDendogram

class VideoClusteringTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        video_uri = md().video_uri
        self.video = Video(video_uri,begin=0,end=42)#,hdf5file='/tmp/data')

    def test_gist_clustering(self):
        gc = gistClustering()
        clust = gc.getcluster(self.video)
        linkage_matrix = numpy.array([[20,22,0.05236782,2],
                                      [36,37,0.0781036,2]])
        assert_almost_equal(clust[:2],linkage_matrix)
 
    def test_hist_clustering(self):
        hc = histClustering()
        clust = hc.getcluster(self.video)
        linkage_matrix = numpy.array([[20,22,1.98700731e-03,2],
                                      [16,17,3.52826529e-03,2]])
        assert_almost_equal(clust[:2],linkage_matrix)

    def test_sig_clustering(self):
        sc = sigClustering()
        clust = sc.getcluster(self.video)
        linkage_matrix = numpy.array([[15,17,0,2],
                                      [24,44,0.0625,2]])
        assert_almost_equal(clust[:2],linkage_matrix)

        
    def test_dendogram(self):
        gc = gistClustering()
        clust = gc.getcluster(self.video)
        dd = VideoDendogram(gc,self.video)
        dd.drawdendogram("/tmp/test.svg") 
        
from pimpy.video.cluster import gistClustering,histClustering,sigClustering


if __name__ == '__main__':
    unittest.main()
