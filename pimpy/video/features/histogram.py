"""
pimpy.video.histogram enable to compute a video histogram

.. module:: histogram
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
# Founda	tion, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import numpy
import logging
from feature import Feature
from pimpy.video.decoder import decoder


class HistogramRGB(Feature):
    u"""
    compute video histogram based on rgba channels
    """
    nbdim = 256 
    dtype = numpy.uint16
    log = logging.getLogger('pimpy.image.features.histogram')

    def __init__(self,**kwargs):
        u"""
        :param framefilter: selected framenumber where we will 
        compute histogram
        :type:  array

        """        
        Feature.__init__(self,**kwargs)
        
    def _gethisto(self,frame):            
        r,g,b,a = frame.get_feature("histogramrgb")
        return numpy.array([r[0],g[0],b[0],a[0]])

    def _callback(self,frame):
        fn = frame.framenumber
        if not hasattr(self,'framefilter') : 
            h = self._gethisto(frame)
            self.ds.write(h)
        elif fn in self.framefilter:
            h = self._gethisto(frame)
            self.ds.write(h,begin=fn,end=fn+1)
        
    def get(self,video):
        """
        :param video: video objects
        :type  video:
        return array of histogram for each video frame 
        :rtype:  numpy.array
        """        
        avfs = video.hdf5.get_avfeature_set("visual",self.name)
        if not avfs :
            datatype = (self.name,self.nbdim,self.dtype)
            avfs = video.hdf5.create_avfeature_set("visual",
                                                   self.name,
                                                   (datatype,),
                                                   None)
            self.ds = avfs[self.name]
            d = decoder(video)
            d.decode_qcif_rgb(self._callback)
        return avfs[self.name].read()


class HistogramGray(HistogramRGB):
    u"""
    compute video histogram based on rgba channels
    """
    nbdim = 256
    def _gethisto(self,frame):            
        return numpy.array([frame.get_feature("histogramgray")])

    def get(self,video):
        """
        :param video: video objects
        :type  video:
        return array of histogram for each video frame 
        :rtype:  numpy.array
        """        
        avfs = video.hdf5.get_avfeature_set("visual",self.name)
        if not avfs :
            datatype = (self.name,self.nbdim,self.dtype)
            avfs = video.hdf5.create_avfeature_set("visual",
                                                   self.name,
                                                   (datatype,),
                                                   None)
            self.ds = avfs[self.name]
            d = decoder(video)
            d.decode_qcif_gray(self._callback)
        return avfs[self.name].read()

class HistogramSampled4dRGBAMassNormed(HistogramRGB):
    u"""
    compute video histogram based on rgba channels, bins on 4 values \
        [0,64,128,192,255] and mass normed
    """        
    nbdim = 4 
    dtype = numpy.float
    def _gethisto(self,frame):            
        r,g,b,a = frame.get_feature("histogramsampled4drgba",mass_normed=True)
        return numpy.array([r,g,b,a])
