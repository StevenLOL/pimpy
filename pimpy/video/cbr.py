"""
pimpy.video.cbr enable to find inside video by Content Based Retrival

.. module:: cbr
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

class ContentBasedRetrieval:
    """
    Video Content Based Retrieval enable to find a video segment in a another video
    """
    def __init__(self,video): 
        """
        :param video: video object
        :type: video
        """
        self.video = video 
        self.sigs = video.get_feature('bindct');

    def find(self,videorequest,hamming_threshold=0.15):
        """
        Find return list of frame number where videofile request segment was identified.

        :param videofilerequest: videofile request uri like file:///home/... 
        :type: string
        :param begin: begin in seconds of the segment requested
        :type:  float 
        :param end: in seconds of the segment requested
        :type:  float
        :param hamming_threshold: 0.20, default value
        :type:  float
        :rtype: array  
        """        
        ((fnb,hd),lreq) = self.__find__(videorequest)
	#filter huge hamming values
	fnb = fnb[numpy.where(hd < hamming_threshold)]

	if len(fnb) == 0  : return None
	results = [] 
        #filter by lenght on segment requested
	r = fnb[0]
	results.append(r)
	for i in fnb[1:]:
		if abs(r-i) > lreq :
			r = i
			results.append(r)	 
	return  results
		
    def __find__(self,videorequest):
        """
        :param videorequest: videorequest object
        :type: object
        :rtype: tuple of 2 numpy.array (frames number, hamming distances)   
        """        
        reqsig = videorequest.get_feature('bindct')
        lreq = len(reqsig)
        dists = []
        for i in range(len(self.sigs)-lreq):
            print "frame", i 
            hdist = ssd.hamming(self.sigs[i:i+lreq],reqsig)
            dists.append(hdist)
        return self.__local_minima_fancy__(dists,window=lreq),lreq

    def __local_minima_fancy__(self,fits, window=50):
        from scipy.ndimage import minimum_filter
        fits = numpy.asarray(fits)
        minfits = minimum_filter(fits, size=window, mode="wrap")
        minima_mask = fits == minfits
        good_indices = numpy.arange(len(fits))[minima_mask]
        good_fits = fits[minima_mask]
        order = good_fits.argsort()
        return good_indices[order], good_fits[order] 

