"""
pimpy.video.features.surf : enable to compute a video signature

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
#
# You should have received a copy of the GNU General Public License
# along with pimpy; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#         
from feature import Feature 
import numpy,logging
from pimpy.video.decoder import decoder

class Surf(Feature):
    u"""
    A SURFs descriptors provided by OpenCV
    
    :param name: sigsize input signature size default 64
    :type name: int 
    """
    log = logging.getLogger('pimpy.video.features.surf')
    description = __doc__

    def __init__(self,**kwargs):
        u"""
        compute video signature based on dct descriptor
        """
        Feature.__init__(self,**kwargs)

    def _callback(self,frame):
        k,d  = frame.get_feature("surf")
        self.avfs["keypoints"].write(k)
        self.avfs["vectors"].write(d)


    def get(self,video):
        """
        return array of [keypoints,descriptors] for each video frame 
        :rtype:  numpy.array
        """        
        self.avfs = video.hdf5.get_avfeature_set("visual",self.name)
        if not self.avfs :
            desc_dataset = (("keypoints",6,numpy.float),
                            ("vectors",64,numpy.float))
            self.avfs = video.hdf5.create_avfeature_set("visual",
                                                        self.name,
                                                        desc_dataset)

            d = decoder(video)        
            d.decode_qcif_gray(self._callback)

        print self.avfs.keys()
        return (self.avfs['keypoints'].read(),
                self.avfs['vectors'].read())
    



  

