#-*- coding:utf-8 -*-"""

u"""
pimpy.image.features.goodfeaturestotrack enable to compute a binary dct 

.. module:: goodfeaturestotrack
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
import logging 
import cv

class GoodFeaturesToTrack(Feature):
    u"""
    A interface to GoodFeaturesToTrack opencv lib

    :param name: cornerCount default 200
    :type name: int 
    """
    name = "goodfeaturestotrack"
    description = __doc__
    cornerCount = 200

    def __init__(self,**kwargs):
        Feature.__init__(self,**kwargs)
        self.log = logging.getLogger('pimpy.image.features.goodfeaturestotrack')
	
    def get(self,image):
        """
        return goodfeatures to track descriptor 

        :rtype:  numpy.array
        """        
        if image.format != "x-raw-gray" :
            image.convert2gray()        
            self.log.warning("Gray conversion is not optimized use native decoder, original format %s" % image.format)

        cv_img = self.cv_img = image.get_opencv_object()
        eig_image = cv.CreateImage(cv.GetSize(cv_img),cv.IPL_DEPTH_8U, 1)
        temp_image = cv.CreateImage(cv.GetSize(cv_img),cv.IPL_DEPTH_8U, 1)

        self.feats = cv.GoodFeaturesToTrack(cv_img,eig_image,temp_image,
                                            self.cornerCount,0.04,1.0,None,3,
                                            True)
        return self.feats 

    def save_image_with_features(self,outfile):        
        for x,y in self.feats :
            cv.Circle(self.cv_img,(x,y), 0, cv.CV_RGB(255, 255, 255))
        cv.SaveImage(outfile,self.cv_img)

