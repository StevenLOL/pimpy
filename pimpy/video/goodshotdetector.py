from __future__ import division
import sys
import numpy 
import time
import logging
from urlparse import urlparse
from xml.etree.ElementTree import Element, ElementTree , SubElement, tostring 

NB_CHANNELS = 1
NB_BINS = 255

K=10
T=70

MEAN_WINDOW = 3 
MOTION_THRESHOLD = 0.15
SHOT_THRESHOLD     = 0.15 
HIGH_CUT_THRESHOLD = 0.8
DISS_THRESHOLD = 0.4
DISS_START_THRESHOLD = 0.16 
DISS_END_THRESHOLD = 0.26 
DISS_MIN_FRAMES = 3
ALPHA = 1.8 
BETA = 0.10

class ShotDetector:
    """
    ShotDetector inspired by : 
    @phdthesis{DelakisPhd,
    author = {Delakis, Manolis},
    school = {Universite de Rennes 1, France},
    title = {Multimodal Tennis Video Structure Analysis with Segment Models},
    month = {October},
    year = {2006},
    url = {ftp://ftp.irisa.fr/techreports/theses/2006/delakis.pdf } 
    } 
    
    To improve computing time, features extraction are done with OpenCV :) 
    Unfortunaly, OpenCV does't manage network protocol like Gstreamer so only file:// uri scheme.

    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
            
    def process(self,uri,profile='default'):
        if profile == 'relax':
            self.alpha = 2.2
            self.beta = 0.15
        elif profile == 'aggresive':
            self.alpha = 2
            self.beta = 0.15
        elif profile == 'default':
            self.alpha = 1.8
            self.beta = 0.10
            
        self.log.info((self.alpha,self.beta))

        self.__check_uri(uri)
        he = HistogramExtractor()
        histos = he.process(urlparse(uri).path)
        
        #from pimpy.video import Video
        #v = Video(uri)
        #histos = v.get_feature('histogramgray')

        nbpixel = numpy.sum(histos[0])
        #compute various histogram variations
        hdiff = (numpy.abs(histos[:-1] - histos[1:]))/2
        hdiffsumchannel = numpy.sum(hdiff,axis=1)    
        #hdiffsum = numpy.sum(hdiffsumchannel,axis=1)
        histo_dist = hdiffsumchannel / int(nbpixel) / NB_CHANNELS

        #detect hard cut 
        cuts = numpy.flatnonzero( histo_dist >= HIGH_CUT_THRESHOLD )
        self.log.info("CUT HIGH "+str(cuts))

        #detect low cut
        for f in numpy.flatnonzero(
            (histo_dist < HIGH_CUT_THRESHOLD) & 
            (histo_dist >= SHOT_THRESHOLD)
            ):
            if self.__cut_detection(f,histo_dist):
                cuts = numpy.append(cuts,f)                
        
        #detect dissolve
        hcumul = self.__histo_cumul(histos)
        hcumul = self.__filter_by_cut(cuts,hcumul)
        hpixelwise = self.__histo_pixelwise(hdiff)
        hpixelwise = hpixelwise/nbpixel/100        

        diss = self.__detect_dissolve(hcumul,hpixelwise)

        return cuts,diss

    def __detect_dissolve(self,hcumul,hpixelwise):
        motion_frames = hpixelwise > MOTION_THRESHOLD
        start = end = -1 
        diss = []
        for f in numpy.flatnonzero(hcumul > DISS_THRESHOLD):
            #new frame not in current dissolve, record dissolve
            if start > 0 and f > end :
                motion = numpy.sum(motion_frames[range(start,end)])
                if not motion and end - start > DISS_MIN_FRAMES: 
                    diss.append([start,end])
                start = end = -1

            if start < 0 : 
                start = end = f
                #find lower bound
                while start > 0 and hcumul[start] > DISS_START_THRESHOLD:
                    start -= 1
                #find upper bound
                while end+1 < len(hcumul) and hcumul[end+1] > DISS_END_THRESHOLD : 
                    end += 1

        #add the last dissolve
        if start > 0 and end > 0 :
            motion = numpy.sum(motion_frames[range(start,end)])
            if not motion and end - start > DISS_MIN_FRAMES: 
                    diss.append([start,end])
        return diss

    def __histo_pixelwise(self, hdiff):
        r = []
        for h in hdiff:
            s = 0
            for i in range(T, NB_BINS):
                s += (h[i] * (i-T-1))
            r.append(s)
        return numpy.array(r)

    def __histo_cumul(self,histos):
        nbpix = numpy.sum(histos[0])
        r = []
        for i in range(1,len(histos)):
            h = (histos[i]+histos[i-1]) / 2
            c = 0
            for k in range(1,K):                
                if i-k < 0 : break 
                c += numpy.sum(numpy.abs(h-histos[i-k]))/nbpix
            r.append(c/K)
        return numpy.array(r)            


    def __filter_by_cut(self,cuts,histo_cumul):
        for c in cuts:
            for i in range(K):
                try :
                    histo_cumul[c+i] = histo_cumul[c+i]/(K-i)
                except IndexError:
                    break
        return histo_cumul
            
    def __cut_detection(self,f,histo_dist):
        d = histo_dist[f]
        left_diff  = histo_dist[f-1-MEAN_WINDOW:f-1] + self.beta
        right_diff = histo_dist[f+1:f+1+MEAN_WINDOW] + self.beta 

        mean_left  = numpy.mean(left_diff)
        mean_rigth = numpy.mean(right_diff)
        mean_local = (mean_left+mean_rigth)/2

        adapt_threshold =  self.alpha * mean_local  - self.beta
        self.log.debug("FRAME %05i | CUT d=%0.3f | AT=%0.3f | %r"   % \
                           (f,d,adapt_threshold,d >=adapt_threshold))
        #if f < 1000 : 
        #    print "FRAME %05i | CUT d=%0.3f | AT=%0.3f | %r"   % \
        #                   (f,d,adapt_threshold,d >=adapt_threshold)
        return d >= adapt_threshold


    def __check_uri(self,uri):
        scheme = urlparse(uri).scheme 
        if scheme != 'file':
            raise NotImplementedError("Only file scheme implemented, not %s" % scheme)

import cv 

class HistogramExtractor:
    def process(self,videofile):
        video = cv.CreateFileCapture(videofile)
        histo = cv.CreateHist([256],cv.CV_HIST_ARRAY,[[0,256]], 1)        
        frame = cv.QueryFrame(video)  
        frame_gray  = cv.CreateImage(cv.GetSize(frame), frame.depth, 1)
        hists    = []
        nbframes = 0 

        while frame :  
            cv.CvtColor(frame,frame_gray,cv.CV_RGB2GRAY)
            cv.CalcHist([frame_gray],histo,0,None)
            h = [cv.GetReal1D(histo.bins,i) for i in range(255) ]
            h = numpy.array(h,dtype='int32')
            hists.append(h)
            frame = cv.QueryFrame(video)  
            nbframes += 1

        hists = numpy.array(hists)
        return hists.reshape(nbframes,-1)



#####################################
#
# MAIN FOR STANDALNE RUNNING
#
#####################################
def __usage():
    print ""
    print "Video shot detector"
    print "Detect cut and dissolve quickly (25x real time) and efficiently "\
        "(trecvid 2007 results : http://pim.gforge.inria.fr/results/shotdetector/content/compare_shot_detector.html)"
    print "Output format is an xml file conform to TrecVid DTD."
    print ""
    print "usage  : python -m pimpy.video.goodshotdetector [-i input_dir] [-o output] [option]"
    print "Options :"
    print "-s      : save histogram feature in numpy format with filename videofile.mpg.npy"
    print "-e .avi : video file extension default is .mpg"
    print "-d file : debug file, print log in file "


def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "i:e:o:d:v",
                                   ["inputdir=",
                                    "extension=",
                                    "output=",
                                    "debugfile="])
    except getopt.GetoptError, err:
        print str(err) 
        __usage()
        sys.exit(2)
    input = None 
    ext = ".mpg"
    output = None
    alpha = 2.6
    beta = 0.10
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(level=logging.DEBUG)
        elif o in ("-i", "--inputdir"):
            input = a
        elif o in ("-e", "--extension"):
            ext = a
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-d", "--debugfile"):
            logging.basicConfig(filename=a,level=logging.DEBUG)
        else:
            __usage()
            assert False, "unhandled option"

    if not input or not output:
            __usage()
            sys.exit()

    start = time.time()
    
    sd = ShotDetector()

    a = alpha
    for b in drange(0,0.05,0.01):            
        
        expeid = str(a)+'-'+str(b)
        if os.path.exists(output+expeid+'.xml'):
            print output+expeid+'.xml exist we skip '
            continue 

        print 'expe : ',a,b
        print '------------------'

        root, sbr = __init_xml(output,expeid)
        for f in os.listdir(input):
            if not f.endswith(ext):
                continue
            f = os.path.join(input,f)
            print "Process file : %s" % "file://"+os.path.abspath(f)
            start= time.time()
            cuts,diss = sd.process("file://"+os.path.abspath(f),
                                       alpha=a,
                                       beta=b)
            print "Cuts      : \n"+str(cuts)
            print "Dissolve  : \n"+str(diss)
            print "Duration  : "+str(time.time()-start)
            videofile = os.path.basename(f)
            seg = SubElement(sbr,'seg',{'src' : videofile})
            __write_cut(seg,cuts)
            __write_grad(seg,diss)
            
            __write_xml(root,output+expeid+'.xml')

def __write_xml(root,outputfile):
    xmlstring = tostring(root)
    file = open(outputfile,'w')
    file.write("<!DOCTYPE shotBoundaryResults SYSTEM \"shotBoundaryResults.dtd\">\n")
    file.write(xmlstring)
    file.close()

def __init_xml(outputfile,expeid):
    xmltree = ElementTree()
    sbrs = Element('shotBoundaryResults')
    SubElement(sbrs,'shotBoundaryResult',
               {'sysId' : 'pimpy'+expeid,
                'totalRunTime'          : '0',
                'totalDecodeTime'       : '0',
                'totalSegmentationTime' : '0',
                'processorTypeSpeed'    : '0'})
    xmltree._setroot(sbrs)
    root = sbrs
    sbr = root.find('shotBoundaryResult')
    return root,sbr 

def __write_cut(seg,cuts):
    for c in cuts :
        attrib = {}
        attrib['type']="cut"
        attrib['preFNum']=str(c)
        attrib['postFNum']=str(c+1)
        SubElement(seg,'trans',attrib)

def __write_grad(seg,grad):
    for b,e in grad :
        attrib = {}
        attrib['type']="grad"
        attrib['preFNum']=str(b)
        attrib['postFNum']=str(e)
        SubElement(seg,'trans',attrib)

if __name__ == '__main__':
    import os 
    import getopt 
    main()
    
    #Adevene

#     if sys.argv[3]:
#         i = 0 
#         f = open(sys.argv[3],'w')
#         for c in sd.cuts :
#             f.write("%d\t%d\tshot\n" % (i*40,c*40))
#             i = c 

#     if sys.argv[4]:
#         i = 0 
#         f = open(sys.argv[4],'w')
#         for b,e in sd.wipe :
#             f.write("%d\t%d\twipe\n" % (b*40,e*40))

#     if sys.argv[5]:
#         i = 0 
#         f = open(sys.argv[5],'w')
#         for b,e in sd.diss :
#             f.write("%d\t%d\twipe\n" % (b*40,e*40))





        
