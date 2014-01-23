"""
pimpy.video.cluster  

.. module:: cluster
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
import sys

from decoder import decoder
import scipy.cluster.hierarchy as sch
import Image, numpy

class videoClustering:
    """
    Video clustering base class 
    """
    def __init__(self):
        self.cluster = None 
        self.keys = None
        self.cuts = None
     
    def performclustering(self,video):
        pass
  
    def getcluster(self,video):
        self.cuts,self.diss = video.getcuts()
        self.keys = video.getkeyframesid()
        self.performclustering(video)

        return self.cluster

    def getsegsbycluster(self,video,framerate=25):
        """
        return a dictionary
        key : clusterid
        values : tuple (segments [[startframe,endframe],[startframe2,endframe2],....], child clusters (child1, child2), merge distance)
        :rtype: dict
        Timecodes are given in milliseconds
        """
        if (self.cluster is None) or (not hasattr(video, 'cuts')):
            self.cluster = self.getcluster(video)
            
        l = len(self.cluster)

        r = 1000./framerate

        result = {}
        prev_cut = self.cuts[0]
        for i in range(l+1):
            seg = (prev_cut*r, (self.cuts[i+1]-1)*r)
            result[i] = [[], (-1,-1), float('-infinity')]
            result[i][0].append(seg)
            prev_cut = self.cuts[i+1]
    
        for i in range(l):
            [nl,nr,d,n] = self.cluster[i]
            result[l+i+1] = [[],(nl, nr),d]
            result[l+i+1][0].extend(result[nl][0])
            result[l+i+1][0].extend(result[nr][0])
        return result

class gistClustering(videoClustering):
    """
    Video Clustering based on gist 
    """
    def __init__(self):
        videoClustering.__init__(self)
        self.gists = [] 


    def performclustering(self,video):
        self.gists = []
        d = decoder(video)
        # compute gist on keyframe 
        d.decode_gist_rgb(self._decoder_callback)
        self.cluster = sch.linkage(self.gists,method='ward',metric='euclidean')          
           
       
    def _decoder_callback(self,frame):
        try :
            import leargist 
        except: 
            raise NameError("Module leargist seems to be unavailable, please install it")

        if frame.framenumber in self.keys:
            im = Image.frombuffer("RGBA", (frame.width,frame.height),frame.data, "raw", "RGBA", 0, 1)                 
            desc = leargist.color_gist(im)
            self.gists.append(desc)                


class histClustering(videoClustering):
    """
    Video Clustering based on histogram sampled per segment
    """
    def __init__(self):
        videoClustering.__init__(self)
  
    def performclustering(self,video):           
        kwargs = {'framefilter' : self.keys }
        keys_histos = video.get_feature('histogramsampled4drgbamassnormed',**kwargs)        
        #flat rgba descriptor
        keys_histos = keys_histos.reshape(-1,16)
        self.cluster = sch.linkage(keys_histos,method='ward',metric='euclidean')
        
class sigClustering(videoClustering):
      """
      Video Clustering based on signature 
      """
      def __init__(self):
          videoClustering.__init__(self)
  
      def performclustering(self,video):               
          sigs = video.get_feature('bindct')
          #cuts detection in done on whole movies
          ids   = [k for k in self.keys if k < len(sigs)]
          ksigs = [sig[0] for sig in sigs[ids]]
          self.cluster = sch.linkage(ksigs,metric='hamming')



def main():
    if len(sys.argv) < 3 :
        print "Usage is : %s <video_file_uri> " % sys.argv[0]
        sys.exit(-1)
    print "TODO "

if __name__ == '__main__':
    main()

