"""
pimpy.video :  video objects class

.. module:: video
   :synopsis: Tools for video 
   :platform: Unix, Mac, Windows

.. moduleauthor:: Sebastien Campion <sebastien.campion@inria.fr>
"""

# pimpy 
# Copyright (C) 2010 Sebastien Campion <sebastien.campion@inria.fr>
#
# pimpy is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pimpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pimpy; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

#import shotdetector as sd
import logging 
import tempfile
import numpy
from urlparse import urlparse
from pimpy.video.factory import FeatureFactory
from pimpy.video.goodshotdetector import ShotDetector
from pimpy.video.frameextractor import FrameExtractor
from pimpy.discover import GstFile
import pimpy.hdf5

class Video:

    log = logging.getLogger('pimpy.video')
    framenumber = 0
    signature = None 
    histogram = None 
    cuts = None

    def __init__(self,uri,begin=0,end=None,hdf5file=None):
        """
        Video object

        :param uri:  input uri like file:///home/...
        :type:   string
        :param begin: in second 
        :type: float
        :param end: in second 
        :type: float
        """
        self.uri = uri 
        self.begin = begin
        self.end = end
        self.log.debug("Video object created : %s" % self.uri)

        if hdf5file == None :
            hdf5file = tempfile.NamedTemporaryFile(suffix='.hdf5').name
        #elif os.path.exists(hdf5file):
        #    self.log.debug("Load data from hdf5file %s "% hdf5file)
        #    self.load(hdf5file)

        mp = uri.replace("file://","")
        self.hdf5 = pimpy.hdf5.File(hdf5file,mediafile_path=mp)
        self.log.debug("hdf5 file %s" % hdf5file)

        if begin is not None :
            self.hdf5.attrs['begin'] = begin
        if end is not None : 
            self.hdf5.attrs['end'] = end


        #discovering metadata
        mp = urlparse(uri).path
        GstFile([mp],self.hdf5.attrs).run()
        

    def list_features(self):
        u"""
        Return list of available features

        :rtype: list of string
        """
	return FeatureFactory.list()

    def get_feature(self,name,**kwargs):
        u"""
        compute feature

        :param name: feature name 
        :type string: 
        :param kwargs : optional pyofile
        (string) to produce pynocchio file (hdf5 file format
        """
	f = FeatureFactory.get_feature(name,**kwargs)
	return f.get(self)


    def getcuts(self):
        u"""
        video cut detection using GoodShotDetector class.

        :param smoothbyhisto: if true, we remove cut if histogram difference isn't sufficient 
        :type: boolean

        :rtype: list of frame number where cut was detected
        """        
        if 'goodshotdetection' not in self.hdf5['visual'].keys(): 
            sd = ShotDetector()
            cuts, diss = sd.process(self.uri)
            cuts.sort()
            diss.sort()

            gsd = self.hdf5['visual'].create_group('goodshotdetection')
            gsd.create_dataset('cuts', data=cuts)
            gsd.create_dataset('dissolves', data=diss)            
            
        gsd = self.hdf5['visual']['goodshotdetection']
        return map(numpy.array, (gsd['cuts'],gsd['dissolves']))

        
    def getkeyframesid(self,cuts=None): 
        u"""
        key frame are defined as the middle frame in a cut segment 

        :rtype: list of key frame number
        """        
        if cuts == None : 
            cuts,diss = self.getcuts()

        #middle keyframe : start_frame + duration / 2
        keys = []
        prev_cut= cuts[0]
        for i in cuts[1:] :
            key_frame = prev_cut+(i-prev_cut)/2
            if key_frame not in keys :
                keys.append(key_frame)
            prev_cut = i
        
        return keys 


    def getkeyframes(self): 
        u"""
        Useful to debug or save frame 

        :rtype: list of key frame object 
        """        
        fe = FrameExtractor(self)
        return fe.getframes(self.getkeyframesid())


# Frame Class 
from pimpy.image import Image

class Frame(Image):
    u"""
    This class describes an video frame based on Image class
    
    :class attributes:
        * .. attribute:: video
            The video instance (pimpy.video.video)where this frame come from 
        * .. attribute:: framenumber
            The raw data of the image
        * .. attribute:: width
            The width  of the image
        * .. attribute:: height
            The width  of the image        
    """        
    video = None 
    framenumber = -1 
    start = -1
    duration = -1 

