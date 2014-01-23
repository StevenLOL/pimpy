#-*- coding:utf-8 -*-"""

u"""
pimpy.image.features.surf enable to compute a binary dct 

.. module:: surf
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
import cv

class Surf(Feature):
    u"""
    A interface to Surf opencv lib

    :param name: extented 0= 64 descriptors, 1= 128 descriptors
    :type name: int 
    :param name: hessianThreshold default 300
    :type name: double  
    """
    name = "surf"
    description = __doc__
    extented = 0 
    hessianThreshold = 100.0

    def __init__(self,**kwargs):
        Feature.__init__(self,**kwargs)
        self.log = logging.getLogger('pimpy.image.features.surf')
        	
    def get(self,image):
        """
        return goodfeatures to track descriptor 

        :rtype:  numpy.array
        """        
        if image.format != "x-raw-gray" :
            image.convert2gray()        
            self.log.warning("Gray conversion is not optimized use native decoder, original format %s" % image.format)

        cv_img = self.cv_img = image.get_opencv_object()
        (keypoints, descriptors) = cv.ExtractSURF(cv_img, None,
                                                  cv.CreateMemStorage(),
                                                  (self.extented,
                                                   self.hessianThreshold,
                                                   3,4))
        import pickle 
        pickle.dump(keypoints,open("/tmp/data2",'wb'))

        self.keypoints = numpy.array([(p[0],p[1],l,s,d,h)
                                      for p,l,s,d,h 
                                      in keypoints])
        self.descriptors = numpy.array(descriptors)

        return self.keypoints,self.descriptors


    def save_image_with_features(self,outfile):        
        for (x, y, laplacian, size, dir, hessian) in self.keypoints:
            cv.Circle(self.cv_img,(x,y), 0, cv.CV_RGB(255, 255, 255))

        cv.SaveImage(outfile,self.cv_img)
        numpy.save(outfile,self.descriptors)

