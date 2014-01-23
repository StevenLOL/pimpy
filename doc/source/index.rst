.. pimpy documentation master file, created by sphinx-quickstart on Tue Jun 23 14:19:23 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PimPy's documentation!
=================================

What's PimPy
------------
PimPy for Indexing Multimedia with Python (or Platform for Indexing Multimedia with Python)

The aim of this module is to provide a convenient and high level API to manage common multimedia indexing tasks.

This project comes from INRIA/IRISA TEXMEX research team works.
For more information, see http://www.irisa.fr/texmex/

PimPy allow to : 

* retrieve media features, such as :

  * video histogram
  * binarize dct descriptor 
  * ...

* detect video cuts
* search a video segment in another video (content based retrieval)
* etc ....




Download & Source Code 
----------------------
Python tarballs and Debian packages : 
  http://pim.gforge.inria.fr/releases/

Source code : 
  http://bitbucket.org/scamp/pimpy 



Software design 
---------------
Software design was created to offer a simple framework. It must allow to extend easily this library with new features.

For each media, features are written in their module dans instanciate via FeatureFactory class (pattern factory method) so new descriptors could be easily added.

Multimedia decoder in this current version is based on GStreamer.

Tests 
-----
Run it with : 
::

	python tests/main.py

Dependencies 
------------
* GIST image descriptor are provided by pyleargist module : 
 * http://pim.gforge.inria.fr/releases
 * http://bitbucket.org/scamp/pyleargist/
* OpenCV for some features
* GPGPU implementation require pycuda module (in progress) 

TODO 
----

* integrate yaafe for audio features extractions http://yaafe.sourceforge.net/ 
* store result with hdf5 and pinocchio http://bitbucket.org/ravio/pinocchio
* decoding method using design pattern to allow others decoders like FFMpeg via pyffas (Python FFmpeg Fast Accurate Seeking)
* refactor factory pattern to use plugin design



Examples : 
==========

.. toctree::
   :maxdepth: 2

   examples
       


Source Code Documentation 
-------------------------------
.. toctree::
   :maxdepth: 3
   
   image
   video
   hdf5


Indices and tables
==================


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

