"""
pimpy.video.gist enable to compute a video gist

.. module:: gist
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

import logging,numpy
from feature import Feature
from pimpy.video.decoder import decoder

class GIST(Feature):
    
    log = logging.getLogger('pimpy.image.features.gist')

    def __init__(self,**kwargs):
        u"""
        compute video gist for each frame
        """
        Feature.__init__(self,**kwargs)

    def _callback(self,frame):
        g = frame.get_feature("gist")
        self.ds.write(numpy.array([g]))

    def get(self,video):
        """
        return array of gist descriptor for each video frame 
        :rtype:  numpy.array
        """        
        avfs = video.hdf5.get_avfeature_set("visual",self.name)
        if not avfs :
            gdt = (self.name,960,numpy.float)
            avfs = video.hdf5.create_avfeature_set("visual",
                                                   self.name,(gdt,)
                                                   ,None)
            self.ds = avfs[self.name]
            d = decoder(video)
            d.decode_gist_rgb(self._callback)
        return avfs[self.name].read()

