"""
pimpy.video.shotdetector basic cut detector 

.. module:: shotdetector
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

import numpy
import scipy.spatial.distance as ssd

class ShotDetector:
    u"""
    Video Shot Detector is a simple video cut detector
    based on difference between DCT
    """

    def __init__(self):
        self.cuts = None 

    def detect(self,video,hamming_threshold=21.0/64):
        """
        :param video: video object
        :type: video
        """         
        dctcuts = []
        dctcuts.append(0)
        sigs = video.get_feature('bindct')  
        s = sigs[0]
        #TODO use GPGPU module if possible or numpy.ediff1d
        for i,s_ in enumerate (sigs[1:]):
            if ssd.hamming(s,s_) > hamming_threshold :
                dctcuts.append(i+1)
            s= s_
        dctcuts.append(len(sigs))
        self.cuts = numpy.array(dctcuts)
        self.video = video 
        return self.cuts

    def smoothbyhisto(self,threshold=176*144*3*255*0.003):
        #build framefilter with previous and next frame 
        framefilter = numpy.concatenate((self.cuts[1:-1]-1,self.cuts[1:-1]))
        framefilter.sort()
        framefilter = numpy.unique(framefilter)

        kwargs = {'framefilter' : framefilter }
        histos = self.video.get_feature('histogramrgb',**kwargs)        
        print histos.shape
    
        cuts = []
        cuts.append(self.cuts[0])
        for i,c in enumerate(self.cuts[1:-1]):
            pos = numpy.where(framefilter == c)[0][0]
            r,g,b,a = abs(histos[pos]-histos[pos-1])
            diff = [sum(col) for col in r,g,b,a]
            diff = sum(diff)
            if diff > threshold:
                cuts.append(c)
        cuts.append(self.cuts[-1])
        self.cuts = numpy.array(cuts)
        return self.cuts 

    def getkeyframes(self):
        """
        get key frames number (frame in the middle of the cut)
        :param smooth: smooth cut dectection using color histogram, more expensive 
        :type  boolean:
        :rtype: numpy
        """
        if self.cuts is None : return None 
        keys = []

        prev_cut= self.cuts[0]
        for i in self.cuts[1:] :
            key_frame = prev_cut+(i-prev_cut)/2
            if key_frame not in keys :
                keys.append(key_frame)
            prev_cut = i
        return keys

if __name__ == '__main__':
    import sys
    import os
    import time
    from pimpy.video import Video

    def format_time(val=0):
        """Formats a value (in milliseconds) into a time string.
        """
        (s, ms) = divmod(long(val), 1000)
        # Format: HH:MM:SS.mmm
        return "%s.%03d" % (time.strftime("%H:%M:%S", time.gmtime(s)), ms)
    
    if not sys.argv[1:]:
        print "Syntax: %s video.avi" % sys.argv[0]
        sys.exit(1)
    v=Video('file://' + os.path.abspath(sys.argv[1]))
    s=ShotDetector()
    shots = s.detect(v)

    print "Detected shots : ", "\n".join(format_time(v) for v in shots)

    


