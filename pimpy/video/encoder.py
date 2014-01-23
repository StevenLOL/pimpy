"""
pimpy.video.encoder video encoder object class 

.. module:: encoder
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
import logging,gst 
import gobject
gobject.threads_init()

class MPEG2_FAAC_AVI_Encoder:
    def __init__(self,video):
        """
        encoder object
        :param video: video object
        :type  video:
        """
        self.log = logging.getLogger("pimpy.video.encoder") 
        self.video = video 
        self.myMainloop = gobject.MainLoop()
        self.width=176
        self.height=144
        self.format="x-raw-yuv"
        self.depth=8
        self.bpp=8

    def encode(self,outfile):
        myPipeline = gst.Pipeline()        

        bus = myPipeline.get_bus()        
        bus.add_signal_watch()
        bus.connect('message::eos', self.eos_cb)

        myVideoQueue = gst.element_factory_make("queue","vidqueue")
        myAudioQueue = gst.element_factory_make("queue","audqueue")

        myVideoConverter = gst.element_factory_make('videoscale')
        myVideoEncoder = self.getvideoencoder()

        myAudioConverter = gst.element_factory_make('audioconvert')
        myAudioEncoder = self.getaudioencoder()

        myMux = self.getmux()

        mySink = gst.element_factory_make('filesink')
        mySink.set_property('location', outfile)


        #GNONLIN COMPOSITION FOR AUDIO AND VIDEO
        acomp = gst.element_factory_make ("gnlcomposition","audiocompo")
        vcomp = gst.element_factory_make ("gnlcomposition","videocompo")
        
        acomp.connect ("pad-added", self.on_pad_add,myAudioQueue)
        vcomp.connect ("pad-added", self.on_pad_add,myVideoQueue)
        
        #myComposition.add(source)
        acomp.add(self.getaudiosource())
        vcomp.add(self.getvideosource())
   
        myVideoCaps = self.getvideocapsfilter()

        myPipeline.add(acomp)    
        myPipeline.add(vcomp)    
        myPipeline.add(myVideoQueue)            
        myPipeline.add(myAudioQueue)    
        myPipeline.add(myAudioConverter)    
        myPipeline.add(myAudioEncoder)    
        myPipeline.add(myVideoConverter,myVideoCaps)        
        myPipeline.add(myVideoEncoder)
        myPipeline.add(myMux)
        myPipeline.add(mySink)
        
        gst.element_link_many(myVideoQueue,myVideoConverter,myVideoCaps,myVideoEncoder,myMux)
        gst.element_link_many(myAudioQueue,myAudioConverter,myAudioEncoder,myMux)
        
        gst.element_link_many(myMux,mySink)
        
        self.myPipeline = myPipeline
        myPipeline.set_state(gst.STATE_PLAYING)

    def getaudiosource(self):
        start = int(self.video.begin * gst.SECOND)
        duration = ( self.video.end - self.video.begin ) * gst.SECOND        
        acaps = gst.caps_from_string ("audio/x-raw-int;audio/x-raw-float")
        asource = gst.element_factory_make('gnlfilesource', 'asource')
        asource.set_property('location', self.video.uri)
        asource.set_property('start',start)
        asource.set_property('duration',duration)
        asource.set_property('media-start', start)
        asource.set_property('media-duration', duration)
        asource.set_property("caps",acaps)
        return asource

    def getvideosource(self):
        start = int(self.video.begin * gst.SECOND)
        duration = ( self.video.end - self.video.begin ) * gst.SECOND        
        vcaps = gst.caps_from_string ("video/x-raw-yuv;video/x-raw-rgb")
        vsource = gst.element_factory_make('gnlfilesource', 'vsource')
        vsource.set_property('location', self.video.uri)
        vsource.set_property('start',start)
        vsource.set_property('duration',duration)
        vsource.set_property('media-start', start)
        vsource.set_property('media-duration', duration)
        vsource.set_property('caps',vcaps)
        return vsource

    def getvideocapsfilter(self):
        structure = gst.Structure("video/%s" % self.format)
        structure["width"] = self.width
        structure["height"] = self.height
        if self.depth : structure["depth"] = self.depth
        if self.bpp   :   structure["bpp"] = self.bpp

        videocaps = gst.element_factory_make('capsfilter')
        videocaps.set_property('caps',gst.Caps(structure))
        return videocaps

    def getvideoencoder(self):
        return gst.element_factory_make('mpeg2enc')

    def getaudioencoder(self):
        return gst.element_factory_make('faac') 

    def getmux(self):
        return gst.element_factory_make('avimux')  

    def on_pad_add(self,composition, pad, compconvert):
        #FIXME more elegant but buggy (?)
        #convpad = self.compconvert.get_compatible_pad(pad, pad.get_caps())
        #pad.link(convpad)
        converterpad = compconvert.get_pad('sink')
        if not converterpad.is_linked():
            pad.link(converterpad)
        
    def eos_cb(self,bus, msg):        
        self.log.debug('END OF STREAM') 
        self.myPipeline.set_state(gst.STATE_NULL)
        self.myMainloop.quit()	


class Encoder(MPEG2_FAAC_AVI_Encoder):
    doc = "Basic encoder"


class THEORA_VORBIS_OGG_Encoder(MPEG2_FAAC_AVI_Encoder):
    doc = "ogg theora vorbis encoder "
    #def __init__(self):
    #    MPEG2_FAAC_AVI_Encoder.__init__(self)
    def getvideoencoder(self):
        return gst.element_factory_make('theoraenc')

    def getaudioencoder(self):
        return gst.element_factory_make('vorbisenc') 

    def getmux(self):
        return gst.element_factory_make('oggmux')  
    
class html5_Encoder(THEORA_VORBIS_OGG_Encoder):
    doc = "HTML5 compatible video "

