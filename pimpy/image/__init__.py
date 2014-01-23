#-*- coding:utf-8 -*-

"""
pimpy.image Image class object

.. module:: image
   :synopsis: Tools for image description 
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
from PIL import Image as pilImage 
from factory import FeatureFactory
import numpy 
import logging 

class Image(object):
    u"""
    This base class describes an image
    :param kwargs: an optional dict
    
    The constructor sets instance attributes from *kwargs*
    
    :class attributes:
        * .. attribute:: format
            The format of the image like x-raw-rgb, or x-raw-gray ( see gstreamer format)
        * .. attribute:: data
            The raw data of the image
        * .. attribute:: width
            The width  of the image
        * .. attribute:: height
            The width  of the image        
    """       
    format = ""
    width = -1
    height = -1
    data = None 

    def __init__(self,**kwargs):
	self.__dict__.update( kwargs )
        self.log = logging.getLogger('pimpy.image.image')

    def get_feature(self,name,**kwargs):
	f = FeatureFactory.get_feature(name,**kwargs)
	return f.get(self)

    def list_features(self):
        u"""
        Return list of available features 

        :rtype: list of string
        """
	return FeatureFactory.list()

    def save(self,outfile):
        u"""
        save frame in a file 

        :param filename: file path
        :type: string
        """
        self.log.debug("Save image to %s" % outfile)
        self.get_pil_object().save(outfile)

    def load(self,infile):
        u"""
        load frame from  a file 

        :param filename: file path
        :type:  string
        """
        self.log.debug("opening file %s" % infile)
        im = pilImage.open(infile)
        im = im.convert('RGBA')
        ld = list(im.getdata())
        nd = numpy.array(ld,dtype=numpy.uint8)
        nd = nd.flatten()
        self.format = "x-raw-rgb"
        self.width = im.size[0]
        self.height = im.size[1]
        self.data = nd.tostring()
        
    def convert2gray(self):
        self.log.debug("lenght data before gray conversion : %i" % len(self.data))
        im = self.get_pil_object()
        im = im.convert('L')
        ld = list(im.getdata())
        nd = numpy.array(ld,dtype=numpy.uint8)
        nd = nd.flatten()
        self.format = "x-raw-gray"
        self.data = nd.tostring()

    def get_pil_object(self):
        u"""
        get image object from pil library
        
        :rtype:  PIL Image
        """
	mode = {
            'x-raw-rgb' : 'RGBA',
            'x-raw-gray': 'L'
	}[self.format]

	return pilImage.frombuffer(mode,(self.width, self.height),\
                                    self.data, "raw",mode, 0, 1)

    def get_numpy_object(self):
        u"""
        get image representation in a numpy array
        for example result[x][y] = [r, g, b, a]
        r,g,b,a range values  0..255 
        where : 
        * x represent horizontal image axis 
        * y represent vertical   image axis 

        :rtype: numpy.array
        """
        n = numpy.fromstring(self.data,dtype=numpy.uint8)
        n = n.reshape((self.height,self.width,-1))
        #n = n.swapaxes(0,1)
        return n


    def get_opencv_object(self):
        u"""
        get image representation in a opencv
        :rtype: numpy.array
        """
        import cv
        img = self.get_numpy_object()
        return cv.fromarray(img)

