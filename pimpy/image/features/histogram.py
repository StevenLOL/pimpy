#-*- coding:utf-8 -*-"""

u"""
pimpy.image.features.histogram : image histogram 

.. module:: features
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
# You should have received a copy of the GNU General Public License
# along with pimpy; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from feature import Feature
import numpy
import logging 

class HistogramRGB(Feature):
    u"""
    An histogram image descriptor
    """
    name = "histogram"
    description = __doc__

    def __init__(self,**kwargs):
        Feature.__init__(self,**kwargs)
        self.log = logging.getLogger('pimpy.image.features.histogram')

    def get(self,image,bins=256):
        """
        get histogram for RGBA color channel

        :rtype: list of tuple (histo,bin_edges) for r,g,b,a channels
        """
        np_img = image.get_numpy_object()
        #get flat pixel array
	#FIXME test number of channel 
        np_img = np_img.reshape(-1,4)
        #split rgba channel 
        r,g,b,a = numpy.hsplit(np_img,(1,2,3))
        h = [numpy.histogram(col,bins=bins,range=[0,bins]) \
                 for col in [r,g,b,a]]
        return h


class HistogramGray(HistogramRGB):
    u"""
    An histogram Gray image descriptor
    """
    name = "histogram gray"
    description = __doc__

    def get(self,image,bins=256):
        """
        get histogram for RGBA color channel

        :rtype: list of tuple (histo,bin_edges) for r,g,b,a channels
        """
        if image.format != "x-raw-gray" :
            image.convert2gray()        
            self.log.warning("Gray conversion is not optimized use native decoder, original format %s" % image.format)

        np_img = image.get_numpy_object()
        return numpy.histogram(np_img,bins=bins,range=[0,bins])[0]

class HistogramSampled4dRGBA(HistogramRGB):
    u"""
    An histogram sampled image descriptor
    """
    name = "histogram Sampled 4d RGBA"
    description = __doc__

    def get(self,image):
        b = [0,64,128,192,255]
        r,g,b,a = HistogramRGB.get(self,image,bins=b)
        #select only histo value of the tuple returned
        result = [h[0] for h in r,g,b,a]
        if self.mass_normed :
            nb_pixels = image.width*image.height*1.0
            result = [h/nb_pixels  for h in result]
        return result 

