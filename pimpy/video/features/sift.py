"""
pimpy.video.features.sift : enable to compute a video signature

.. module:: sift
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
from feature import Feature 
import numpy , logging
from pimpy.video.decoder import decoder

class Sift(Feature):
    u"""
    A binary DCT video descriptor
    
    :param name: sigsize input signature size default 64
    :type name: int 
    """
    log = logging.getLogger('pimpy.video.features.sift')
    description = __doc__
    sigsize=64

    def __init__(self,**kwargs):
        u"""
        compute video signature based on dct descriptor
        """
        Feature.__init__(self,**kwargs)

    def _callback(self,frame):
        r = frame.get_feature("sift")
        kp = []
        sifts = []
        for s in r:
            x,y   = s[0]
            a     = s[1]
            b     = s[2]
            kp.append(numpy.array([x,y,a,b]))
            sifts.append(s[3])
        self.avfs["keypoints"].write(numpy.array(kp))
        self.avfs["vectors"].write(numpy.array(sifts))


    def get(self,video):
        """
        return array of descriptor for each video frame 
        :rtype:  numpy.array
        """        
        self.avfs = video.hdf5.get_avfeature_set("visual",self.name)
        if not self.avfs :
            desc_dataset = (("keypoints",4,numpy.float32),
                            ("vectors",128,numpy.uint8))
            self.avfs = video.hdf5.create_avfeature_set("visual",
                                                   self.name,
                                                   desc_dataset)

            d = decoder(video)        
            d.decode_qcif_gray(self._callback)
            
        return (self.avfs['keypoints'].read(),
                self.avfs['vectors'].read())
