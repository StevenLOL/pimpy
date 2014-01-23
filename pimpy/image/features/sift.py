import tempfile
import logging
import cStringIO
import numpy as np
from subprocess import Popen, PIPE
from feature import Feature 

class Sift(Feature):
    siftfeat_bin = "sift"
    swapdir = "/dev/shm"
    dim = 128
    sift_type = np.dtype([('coords',(np.float32,2)),\
                              ('scale',np.float32),\
                              ('orientation',np.float32),\
                              ('values',np.uint8,dim)])
    
    log = logging.getLogger('pimpy.image.features.sift')

    def __init__(self,**kwargs):
        Feature.__init__(self,**kwargs)
        self.log = logging.getLogger('pimpy.image.features.sift')

    def get(self,image):
            
        im = image.get_pil_object()
        if image.format != "x-raw-gray" :
            im = im.convert('L')
        output = cStringIO.StringIO()
        tmp = tempfile.NamedTemporaryFile(dir=self.swapdir,suffix=".pgm")
        im.save(tmp.name)

        self.log.debug("swap image file path %s " % tmp.name) 

        cmd = self.siftfeat_bin
        try :
            sift = Popen(cmd.split(' '),stdin=open(tmp.name),stdout=PIPE,stderr=PIPE)
            output = sift.communicate()[0]
            self.log.debug("Sift in progress") 
            #self.log.debug(output)
            sifts = self._parse_output(output)
        except OSError: 
            raise NotImplementedError("external sift program executable **%s** not available " % self.siftfeat_bin)        
        return sifts 
        
    def _parse_output(self,output):        
        lines = output.split('\n')

        #first line /nb_of_features dim 
        featuresnb, dim = [int(v) for v in lines[0].split()]
        
        sifts = np.zeros([featuresnb],dtype=self.sift_type)

        for i in range(1,len(lines)-1 ,8):
            #firt line in block 
            y,x,scl,ori = lines[i].split()
            values = []
            #concat sift values dispatch on 7 next lines
            for j in range(1,8):
                values += lines[i+j].split()
            sifts[i/8] = ((y,x),scl,ori,values)
        return sifts 


