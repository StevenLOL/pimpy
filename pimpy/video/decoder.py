"""
pimpy.video.decoder video decoder object class 

.. module:: decoder
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
import gst, logging 
import pimpy.video

class decoder:
    def __init__(self,video):
        """
        decoder object
        :param video: video object
        :type  video:
        """
        self.video = video 
        self.log = logging.getLogger("pimpy.video.decoder") 

    def decode_sqcif_gray(self,callback):
        self._decode(callback,width=128,height=96,\
                   format="x-raw-gray",\
                   depth=8,bpp=8)

    def decode_qcif_gray(self,callback):
        self._decode(callback,width=176,height=144,\
                   format="x-raw-gray",\
                   depth=8,bpp=8)

    def decode_qcif_rgb(self,callback):
        self._decode(callback,width=176,height=144,\
                   format="x-raw-rgb")

    def decode_cif_rgb(self,callback):
        self._decode(callback,width=352,height=288,\
                   format="x-raw-rgb")

    def decode_gist_rgb(self,callback):
        self._decode(callback,width=64,height=64,\
                         format="x-raw-rgb",
                     bpp=32,depth=24)



    def _decode(self,callback,width=None,height=None,\
                   format=None,depth=None,bpp=None):

        if not width or not height or not format :
            raise NameError("Failed to init decoder without format,"\
                                +" or height or width")

        begin = self.video.begin
        end   = self.video.end

        #init gstreamer 
        caps="video/%s,width=%i,height=%i"\
            % (format,width,height)

        if depth  : 
            caps+=",depth=%i" % depth 
        if bpp  : 
            caps+=",bpp=%i" % bpp

        pip_desc ="uridecodebin uri=%s ! ffmpegcolorspace !  videoscale ! appsink name=sink " % self.video.uri
        pipeline = gst.parse_launch(pip_desc)

        self.appsink = pipeline.get_by_name("sink")
        self.appsink.set_property('emit-signals', True)
        self.appsink.set_property('sync', False)
        self.appsink.set_property('caps', gst.caps_from_string(caps))
        
        if pipeline.set_state(gst.STATE_PLAYING) == gst.STATE_CHANGE_FAILURE:
            raise NameError("Failed to load uri video (example file:///home/... )%s" % self.video.uri)

	buff = self.appsink.emit('pull-preroll')

	#seek if necessary 
        if begin > 0 or end is not None : 
            self.log.info("seek in video from %d to %d" % (begin,end))
            flags = gst.SEEK_FLAG_FLUSH        
            flags |= gst.SEEK_FLAG_ACCURATE 

            res = pipeline.seek(
                1.0,                            # normal-speed playback
                gst.FORMAT_TIME,                # time-based seek
                flags,       
                gst.SEEK_TYPE_SET, begin*gst.SECOND,
                gst.SEEK_TYPE_SET, end*gst.SECOND)
            res = pipeline.seek_simple(gst.FORMAT_TIME,flags, begin*gst.SECOND)

            if res:                
		pipeline.set_new_stream_time(0L)
            else:
                gst.error("seek to %r failed" % begin)
                raise NameError("seek failed")

        #start video decoding
	framenumber = 0
        while True :
            buff = self.appsink.emit('pull-buffer')
            if not buff : break 
            f = pimpy.video.Frame(**{
                  "video" : self.video , 
                  "framenumber" : framenumber,
		  "data" : buff.data, 
		  "format": format ,
	          "width" : width,
	          "height" : height })

            f.position = pipeline.query_position(gst.Format(gst.FORMAT_TIME), None)[0]

            #send frame decoded to the callback function
            callback(f)
            framenumber+=1 

        #Decode step finish
        self.video.framenumber = framenumber 
	pipeline.set_state(gst.STATE_NULL)
	pipeline = None 
        


	
