#-*- coding:utf-8 -*-"""

u"""
pimpy.image.features.bindct enable to compute a binary dct 

.. module:: bindct
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
from math import sqrt
import numpy
import numpy.fft as fft
import logging 

class BinDCT(Feature):
    u"""
    A binary DCT image descriptor
    
    :param name: sigsize input signature size default 64
    :type name: int 
    """
    name = "bindct"
    description = __doc__
    sigsize=64

    def __init__(self,**kwargs):
        Feature.__init__(self,**kwargs)
        self.log = logging.getLogger('pimpy.image.features.bindct')
	
    def get(self,image):
        """
        return dct descriptor 

        :rtype:  numpy.array
        """
        if image.format != "x-raw-gray" :
            image.convert2gray()        
            self.log.warning("Gray conversion is not optimized use native decoder, original format %s" % image.format)

        #self.log.debug("Image lenght is %i" % len(image.data))
        #self.log.debug("Image size is %ix%i " % (image.height,image.width))
        im = numpy.fromstring(image.data,dtype=numpy.uint8)
        im = im.reshape((image.height,image.width))
        hs = ws = sqrt(self.sigsize)
        dct = fft.rfft2(im)
        subdct = dct[0:ws,0:hs]
        subdct[0][0] = dct[ws,hs]
        subdct = subdct.reshape(self.sigsize,)
        median = numpy.median(subdct)
        self.sig  = numpy.zeros(self.sigsize,dtype='bool')        
        self.sig[numpy.where( subdct > median )] = True
        return self.sig 

