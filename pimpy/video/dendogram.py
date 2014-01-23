"""
pimpy.video.dendogram produce hierarchical clustering dendogram 
on video 

.. module:: dendogram
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

import scipy.cluster.hierarchy as sch
from decoder import decoder
import xml.etree.ElementTree as et
import base64
import tempfile

class VideoDendogram:
    def __init__(self,clust,video,thumbsize=(60,60)):
        """
        :param cluster: cluster return by videoclustering
        :type: numarray
        :param video: video object 
        :type: video
        :param key_frames_id: array of key frame number  
        :type: array
        """
	self.w = 0
        self.key_frames_id = clust.keys
        self.cluster = sch.to_tree(clust.cluster)
        self.video = video
        self.key_frames = []
	self.thumbsize = thumbsize

    def _decoder_callback(self,frame):
        """
        retrieve image for thumbtails
        """
        if frame.framenumber in self.key_frames_id:
                self.key_frames.append(frame)

    def _getimlist(self):
        """
        return a array key frames for each segment 
        """ 
        d = decoder(self.video)
        d.decode_qcif_rgb(self._decoder_callback)
    
    def _getdepth(self,tree,x=0):
        """
        return hierarchical tree depth
        """
        if tree.get_left() == None and tree.get_right() == None : return x
        return max(self._getdepth(tree.get_left(),x+1),self._getdepth(tree.get_right(),x+1))

    def _drawnode(self,clust,x,y):  
        """
        draw a dendogram node 
        """
        self.w = max(x,self.w)
        if not clust.is_leaf() :
	    # Line length
	    ll = (clust.dist+1)*self.thumbsize[0]

            h1     = clust.get_left().get_count()*self.thumbsize[0]
            h2     = clust.get_right().get_count()*self.thumbsize[0]
            top    = y-(h1+h2)/2
            bottom = y+(h1+h2)/2
    
            self.root.append(self._gettext(str(clust.get_id()),x+10,y))
            self.root.append(self._getline(x,top+h1/2,x,bottom-h2/2)) 
                    
            self.root.append(self._getline(x,top+h1/2,x+ll,top+h1/2))
            self.root.append(self._getline(x,bottom-h2/2,x+ll,bottom-h2/2))
            
            # Call the function to draw the left and right nodes    
            self._drawnode(clust.get_left(),x+ll,top+h1/2)
            self._drawnode(clust.get_right(),x+ll,bottom-h2/2)
        else :
            #create base64 image thumbnail
            nodeim = self.key_frames[clust.get_id()]
            nodeim = nodeim.get_pil_object()
            nodeim.thumbnail(self.thumbsize)
            tmp = tempfile.TemporaryFile(mode='w+b')
            nodeim.save(tmp,"png")
	    tmp.seek(0)
            picdata = base64.b64encode(tmp.read())
	
            #add image xml element 
	    h,w = self.thumbsize
            image = et.Element("{http://www.w3.org/2000/svg}image")
            image.attrib["x"] = str(x-h/2)
            image.attrib["y"] = str(y-w/2)
            image.attrib["width"] = str(w)
            image.attrib["height"] = str(h)
            image.attrib["{http://www.w3.org/1999/xlink}href"] = "data:image/png;base64,"+picdata
	    self.root.append(image)
                          
	
    def _getline(self,x1,y1,x2,y2,color="red"):
	line = et.Element("{http://www.w3.org/2000/svg}line")
	line.attrib["x1"] = str(x1)
	line.attrib["y1"] = str(y1)
	line.attrib["x2"] = str(x2)
	line.attrib["y2"] = str(y2)
	line.attrib["stroke"] = color
	return line


    def _gettext(self,text,x,y,color="white"):
	txt = et.Element("{http://www.w3.org/2000/svg}text")
	txt.attrib["x"] = str(x)
	txt.attrib["y"] = str(y+self.thumbsize[0]/4)
	txt.attrib["fill"] = color
	txt.attrib["font-size"] = str(self.thumbsize[0]/2)
	txt.text = text 
	return txt

    def getsvg(self):
        self._getimlist()    
        h = self.cluster.get_count()*self.thumbsize[0]

	self.root = et.Element("{http://www.w3.org/2000/svg}g")
        self._drawnode(self.cluster,0,(h/2))

	w = self.w + self.thumbsize[1]
	
	svg = et.Element("{http://www.w3.org/2000/svg}svg")
	svg.attrib["width"]  = str(w+50)
	svg.attrib["height"] = str(h+50)
	svg.attrib["style"]  = "background-color: black;"

	self.root.attrib["transform"]= "translate(25,25)"
	svg.append(self.root)

	tree = et.ElementTree(svg)
        return tree 

    def drawdendogram(self,drawfile):    
        """
        :param drawfile: draw dendogram with pics in leaf in file <drawfile>
        :type: string
        """
        tree = self.getsvg()
	tree.write(drawfile) 
	"""
	f = gzip.open(drawfile, 'wb')
	f.write(et.tostring(svg))
	f.close()
 	"""



