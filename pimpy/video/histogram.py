"""
pimpy.video.histogram enable to compute a video histogram

.. module:: histogram
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

from decoder import decoder

class histogram:
    def __init__(self,video,framefilter=None):
        """
        compute video histogram based on rgb channel, bins on 4 values
        [0,64,128,192,255]
        :param video: video objects
        :type  video:
        :param framefilter: selected framenumber where we will 
        compute histograme 
        :type  array:
        """        
        self.histos = None 
        self.framefilter = framefilter
        d = decoder(video)
        d.decode_cif_rgb(self._decoder_callback)

    def _decoder_callback(self,type,frame):
        if not self.framefilter or frame.framenumber in self.framefilter:
            """
            n = numpy.fromstring(frame.data,dtype=numpy.uint8)
            m = n.reshape(n.shape[0]/4,4)
            #remove alpha column
            rgb = numpy.delete(m, 3, 1)
            # split channel
            (n,r,g,b) = numpy.split(rgb,[0,1,2],1)
            
            #prepare empty histo structure
            h = numpy.empty((3,4),dtype=numpy.uint8)

            for i,color in enumerate([r,g,b]):
                ch,b = numpy.histogram(color,bins=[0,64,128,192,255])
                #normalize histogram
                h[i] = ch*255.0/sum(ch)
            """
            if self.histos == None  : 
                self.histos = [frame.getHistogramEdge4D(normed=True)]
            else :
                self.histos.append(frame.getHistogramEdge4D(normed=True))

    def gethistogram(self):
        """
        return array of histogram for each video frame 
        :rtype:  numpy.array
        """        
        return self.histos

