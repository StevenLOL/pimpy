"""
pimpy.video.features.bindct : enable to compute a video signature

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
#
# You should have received a copy of the GNU General Public License
# along with pimpy; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#         
from feature import Feature 
import numpy 
from pimpy.video.decoder import decoder

class BinDCT(Feature):
    u"""
    A binary DCT video descriptor
    
    :param name: sigsize input signature size default 64
    :type name: int 
    """
    description = __doc__
    sigsize=64

    def __init__(self,**kwargs):
        u"""
        compute video signature based on dct descriptor
        """
        Feature.__init__(self,**kwargs)

    def _callback(self,frame):
        sig = frame.get_feature("bindct",**{"sigsize" : self.sigsize})
        self.ds.write(numpy.array([sig]))

    def get(self,video):
        """
        return array of descriptor for each video frame 
        :rtype:  numpy.array
        """        
        bdt = (self.name,self.sigsize,numpy.bool)
        #if already computed return it
        avfs = video.hdf5.get_avfeature_set("visual",self.name)
        if not avfs :
            avfs = video.hdf5.create_avfeature_set("visual",self.name,(bdt,))
            self.ds = avfs[self.name]
            d = decoder(video)        
            d.decode_qcif_gray(self._callback)
        return avfs[self.name].read()
