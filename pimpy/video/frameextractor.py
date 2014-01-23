"""
pimpy.video.frameextractor enable to extract frames from video 

.. module:: frameextractor
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

import os
from pimpy.video.decoder import decoder

class FrameExtractor:
    def __init__(self,video): 
        """
        :param video: video object
        :type: video
        """
        self.video = video 
        self.frames_list_ids = None
        self.frames = []

    def getframes(self,framelist):
        self.frames_list_ids = framelist
        self.frames = []
        d = decoder(self.video)
        d.decode_qcif_rgb(self._frame_callback)    
        return self.frames

    def saveframes(self,framelist,outputdir):
        frames = self.getframes(framelist)
        for i,f in enumerate(frames):
            id = framelist[i]
            path = os.path.join(outputdir, "%010d.png" % id)
            f.save(path)
                        
    def _frame_callback(self,frame):
        if frame.framenumber in self.frames_list_ids:
                self.frames.append(frame)


