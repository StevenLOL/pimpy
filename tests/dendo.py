from pimpy.video.video import Video
from pimpy.video.cluster import *
from pimpy.video.dendogram import VideoDendogram
from tests.multimedia_data import multimediaData as md


uri = md().video_uri
v = Video(uri)
gc = gistClustering()
gc.getcluster(v,smoothbyhisto=True)

dd = VideoDendogram(gc,v)
dd.drawdendogram("gistclust_smooth.svg")

