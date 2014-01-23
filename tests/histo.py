from path import uri 
from pimpy.video.objects import *

print uri

v = video(uri,begin=32,end=32.04)
h = v.gethistogram()
