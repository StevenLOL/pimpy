#!/usr/bin/env python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# gstfile.py
# (c) 2005 Edward Hervey <edward at fluendo dot com>
# Discovers and prints out multimedia information of files

# This example shows how to use gst-python:
# _ in an object-oriented way (Discoverer class)
# _ subclassing a gst.Pipeline
# _ and overidding existing methods (do_iterate())

import os
import sys

import gobject
gobject.threads_init()

from gst.extend.discoverer import Discoverer

class GstFile:
    """
    Analyses one or more files and prints out the multimedia information of
    each file.
    """

    def __init__(self, files,attrs):
        self.files = files
        self.attrs = attrs
        self.mainloop = gobject.MainLoop()
        self.current = None

    def run(self):
        gobject.idle_add(self._discover_one)
        self.mainloop.run()

    def _discovered(self, d,ismedia):
        self.attrs['media type'] = str(d.mimetype)
        if d.is_video:            
            #self.attrs['video.caps'] =  str(d.videocaps)
            self.attrs['video.width'] =  d.videowidth
            self.attrs['video.height'] =  d.videoheight
            self.attrs['video.length'] =  d.videolength
            self.attrs['video.framerate'] =  d.videorate.num*1.0/d.videorate.denom
            self.attrs['video.framerate.num'] =  d.videorate.num
            self.attrs['video.framerate.denom'] =  d.videorate.denom
        if d.is_audio:
            #self.attrs['audio.caps'] =  str(d.audiocaps)
            self.attrs['audio.format'] =  d.audiofloat and 'floating-point' or 'integer'
            self.attrs['audio.samplerate'] =  d.audiorate
            self.attrs['audio.samplewidth'] =  d.audiowidth
            self.attrs['audio.sampledepth'] =  d.audiodepth
            self.attrs['audio.length'] =  d.audiolength
            self.attrs['audio.channels'] =  d.audiochannels

        self.current = None
        if len(self.files):
            print "\n"
        gobject.idle_add(self._discover_one)
        
    def _discover_one(self):
        if not len(self.files):
            gobject.idle_add(self.mainloop.quit)
            return False
        filename = self.files.pop(0)
        if not os.path.isfile(filename):
            gobject.idle_add(self._discover_one)
            return False

        # create a discoverer for that file
        self.current = Discoverer(filename)
        # connect a callback on the 'discovered' signal
        self.current.connect('discovered', self._discovered)
        # start the discovery
        self.current.discover()
        return False

def main(args):
    if len(args) < 2:
        print 'usage: %s files...' % args[0]
        return 2

    gstfile = GstFile(args[1:])
    gstfile.run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
