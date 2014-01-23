================
Usage examples : 
================

Detect shot in a video 
-------------------------
* Using ShotDetector class : 

::

	from pimpy.video.goodshotdetector import ShotDetector,HistogramExtractor	
   	sd = ShotDetector()
        cuts,diss = sd.process(file:///tmp/myvideo.avi")

* Using command line : 

:: 

	python -m pimpy.video.goodshotdetector [-i input_dir] [-o output] [option]
	usage  : 
	Options :
	-s      : save histogram feature in numpy format with filename videofile.mpg.npy
	-e .avi : video file extension default is .mpg
	-d file : debug file, print log in file

Scene clustering using gist descriptor
--------------------------------------

Using cut detection, you can produce a SVG graph to display a scene clustering :

::

	from pimpy.video import Video
	from pimpy.video.cluster import gistClustering
	from pimpy.video.dendogram import VideoDendogram

	video = Video("file:///tmp/6min.avi")	  	     

        gc = gistClustering()
        clust = gc.getcluster(video)
        vd = VideoDendogram(gc,video)
        vd.drawdendogram("/tmp/test.svg") 

.. image:: gist_cluster_svg.png
   :scale: 60 %


Encode video segment 
--------------------

::	

	from pimpy.video import Video
	from pimpy.video.encoder import html5_Encoder,MPEG2_FAAC_AVI_Encoder 	
	video = Video("file:///tmp/6min.avi",begin=12.28,end=12.96)			
	he = html5_Encoder(video)
	he.encode("/tmp/mysegment.ogg")
	mf = MPEG2_FAAC_AVI_Encoder(video)
	mf.encode("/tmp/mysegment.avi")


Extract frames 
--------------

:: 

   from pimpy.video import Video
   from pimpy.video.frameextractor import FrameExtractor 

   video = Video("file:///tmp/6min.avi")			
   fe = FrameExtractor(video)
   fe.saveframes([10,20,30],"/tmp")
 

Compute Video Features
------------------------------
To list available video descriptors :
::
	from pimpy.video import Video 
	v = Video("file:///tmp/2min.avi")
	v.list_features()

output :
:: 

   ['histogramsampled4drgba', 'histogramrgb', 'gist', 'bindct','goodfeaturestotrack','surf','sift']

Get video histogram
+++++++++++++++++++

Compute video histogram of 15 seconds (between 45 and 60) of video ::	

	from pimpy.video import Video 
	v = Video("file:///tmp/2min.avi",begin=45,end=60)
	v.get_feature('histogramrgb')

Results one histogram per frame in a numpy array


Get video histogram on frame 10,20,30
+++++++++++++++++++++++++++++++++++++
:: 
        
   ...
   kwargs = {'framefilter' : [10,20,30] }
   histos = v.get_feature('histogramrgb',**kwargs)        
   ...

Get video sifts
+++++++++++++++++++

Compute video sift of 5 seconds (between 45 and 50) of video ::	

	from pimpy.video import Video 
	v = Video("file:///tmp/2min.avi",begin=45,end=50)
	v.get_feature('sift')

Results sift array per frame


Get image sifts
+++++++++++++++++++

Compute sift on image lenna.png  ::	
	from pimpy.image import Image
	im = Image()
	im.load("/tmp/lenna.png")
	s = im.get_feature('sift')

Video content based retrieval
------------------------------
Request a segment of 15 seconds (between 60 and 75) between two videos ::	

	from pimpy.video import Video
	from pimpy.video.cbr  import ContentBasedRetrieval

	target  = Video("file:///tmp/6min.avi")
	request = Video("file:///tmp/2min_low_quality.flv",begin=60,end=75 )

	#Init CBR engine	
	c = ContentBasedRetrieval(target)

	c.find(request)

Output is the frame number ::

       [1438]

       



        


