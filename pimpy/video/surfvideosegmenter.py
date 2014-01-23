"""
pimpy.video.surfvideosegmenter basic cut detector 

.. module:: surfvideosegmenter
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
import logging

class SurfVideoSegmenter:
    u"""
    Video segementer based local features SURF
    """

    def __init__(self):
        self.log = logging.getLogger('pimpy.video.surfvideosegmenter')
        self.q = 64*4
        #self.max_dis_threshold = 0.31
        self.max_dis_threshold = 0.815
        self.min_dis_threshold = 0.45
        self.minframes = 4
        self.cut_threshold = 0.05
        self.grid = (7,7)
        #self.grid = (3,3)
        self.size=(176,144)

    def process(self,video,keypoints = None, surfs=None ):
        """
        :param video: video object
        :type: video
        :rtype: tuples frames_cut, frames_windows_dissolve,similarity_values_per frame
        """         
        if not keypoints and not surfs :
            keypoints, surfs = video.get_feature('surf')  
        #import pickle 
        #pickle.dump(keypoints,open("keypoints",'w'),pickle.HIGHEST_PROTOCOL)
        #pickle.dump(surfs,open("surfs",'w'),pickle.HIGHEST_PROTOCOL)

        similarity = []

        for frame_number in range(len(surfs)-1) : 
            self.curfn = frame_number
            k0,s0 = keypoints[frame_number],surfs[frame_number]
            k1,s1 = keypoints[frame_number+1],surfs[frame_number+1]
            d = self._match_similarity((k0,s0),(k1,s1))

            self.log.debug("Frame number %i nb of keyspoints = %i dis = %f  " % (frame_number,len(k0),d))
            similarity.append(d)
            if frame_number == 24*15 : break 

        similarity = numpy.array(similarity)

        #Find candidates, frames for cut and dissolve
        frames_cuts = numpy.flatnonzero(similarity < self.cut_threshold )
        self.log.debug(frames_cuts)

        #Get dissolves as segment wihout false alarm
        frames_dissolves = (similarity >= self.min_dis_threshold ) & (similarity <= self.max_dis_threshold ) 
        frames_dissolves = numpy.flatnonzero(frames_dissolves)
        self.log.debug(frames_dissolves)
        frames_dissolves = self._post_process(frames_dissolves,self.minframes)

        self.log.debug(frames_dissolves)

        return frames_cuts,frames_dissolves,similarity

    def _post_process(self,frames,min_frames):
        i = 0 
        dissolve_segments = []
        #find segments
        # i.e: 1,2,3,4,7,8,9 -> (1,4),(7,9)
        while i+1 < len(frames)-1 : 
            if frames[i]+1 == frames[i+1] :
                start = frames[i]
                while i+1 <= len(frames)-1 and frames[i]+1 == frames[i+1] :
                    i+=1
                stop = frames[i]
                dissolve_segments.append((start,stop))
            i+=1

        #remove segment if segment lenght < min_frames
        for start,stop in dissolve_segments[:]:
            if stop-start+1 < min_frames :
                dissolve_segments.remove((start,stop))
        return dissolve_segments

    def _dispatch_surfs_per_area(self,areas,kp,ds):
        r = {}
        s = numpy.hsplit(numpy.cast['uint8'](kp),6)
        x = s[0]
        y = s[1]
        for (x1,y1),(x2,y2) in areas :
            #find index where keypoints in area 
            si = (x < x2) & (x > x1) & ( y < y2) & (y > y1)
            indices = numpy.flatnonzero(si)
            r[(x1,y1),(x2,y2)] = ds[indices]
        return r 

    def _match_similarity(self,c_surfs,n_surfs):
        max_surfs = 0 
        max_sim = 0 
        areas = self._get_areas()
        spa = self._dispatch_surfs_per_area(areas,c_surfs[0],c_surfs[1])
        nspa = self._dispatch_surfs_per_area(areas,n_surfs[0],n_surfs[1])

        for a in areas:
            #optimisation
            if len(spa) < max_surfs or len(nspa) < max_surfs :
                continue
            c,n = self._surf_match_area(spa[a],nspa[a])#n_surfs[1]) 
            #c,n = self._surf_match_area(spa[a],n_surfs[1]) 
            #c,n = self._surf_match_area_quant(spa[a],n_surfs[1]) 
            if n == 0 : 
                continue 
            self.log.debug("Area : %i,%i - %i,%i / c=%i n=%i v=%f" % (a[0][0],a[0][1],a[1][0],a[1][1],c,n,c*1.0/n))
            if c > max_surfs :
                max_surfs = c 
                max_sim = c*1.0/n

            if c == max_surfs and c*1.0/n < max_sim :
                max_sim = c*1.0/n

        self.log.debug("Return sim values : %f" % max_sim )
        return max_sim

    def _get_areas(self):
        w = self.size[0]/self.grid[0]
        h = self.size[1]/self.grid[1]
        results = []

        for x in range(self.grid[0]):
            for y in range(self.grid[1]):
                x1 = x*w
                y1 = y*h
                x2 = (x+1)*w
                y2 = (y+1)*h
                results.append(((x1,y1),(x2,y2)))
        return results

    def _quantify(self,s):
        return numpy.cast['uint16'](numpy.sum(s*self.q,axis=1))

    def _surf_match_area(self,surfs_request,next_surfs):
        match = 0 
        for r in surfs_request :
            for t in next_surfs:
                if numpy.allclose(r,t,atol=1e-1):
                  match +=1   
                  break
        return match,len(surfs_request)

    def _surf_match_area_quant(self,surfs_request,next_surfs):
        nextsurfs_quant = self._quantify(next_surfs)
        surfs_request_quant = self._quantify(surfs_request)

        corresponding_surf = len(numpy.intersect1d_nu(surfs_request_quant,nextsurfs_quant))
        return corresponding_surf,len(surfs_request)

    def save(self,outputfile):
        numpy.save(outputfile,self.dissimilarity)

  

