"""Module docstring.

sigcuda is a executable and python library to search vidsig signature in large data using GPU Cuda Nvidia.

Usage is sigcuda -d <data> -r <request>

Don't forget to add cuda binaries in your path :
export PATH=$PATH:/usr/local/cuda/bin/
"""

import getopt
import sys
try:
    import pycuda.autoinit
    import pycuda.driver as cuda
    from pycuda.compiler import SourceModule
    print "Use cuda card ",pycuda.autoinit.device.name()
except:
    print "Couldn't load pycuda"
    
import numpy
import os
from math import ceil

class sig4cuda:

    def __init__(self):
        self.sigfile = []    
        self.sigfilesize = []    
        self.numpydata = numpy.array([],numpy.uint64)

    def add(self,sigfile):
        self.sigfile.append(sigfile)        
        self.sigfilesize.append(os.path.getsize(sigfile)/8)                
        self.numpydata = numpy.concatenate((self.numpydata,numpy.fromfile(sigfile,numpy.uint64)))
        print "%s loaded in RAM" % sigfile 

    def loaddir(self,dir,prefix='',suffix="sig"):
        for root, dirs, files in os.walk(dir):
            for file in files :
                if file.startswith(prefix) and file.endswith(suffix) :
                    self.add(os.path.join(root,file))
        
    def getsig(self,sigfile,start,end):
        if not sigfile in self.sigfile:
            self.add(sigfile)
        i = self.sigfile.index(sigfile)
        offset = sum (self.sigfilesize[0:i])
        return self.numpydata[offset+start:offset+end]
    
    def resolve(self,framenumber):
        for s in self.sigfilesize:
            if s > framenumber :                
                sigfile = self.sigfile[self.sigfilesize.index(s)]
                return (sigfile,framenumber)
            else:
                framenumber -= s

    def loadsig2gpu(self):
        self.devicealloc_sigdb = cuda.to_device(self.numpydata)
        print "DB signatures loaded in GPGPU" 

    def findsigbyfile(self,sigfile):
        sig = numpy.fromfile(sigfile,numpy.uint64)
        return self.findsig(sig)

    """
    TODO 
    def preindex(self):
        ind = numpy.cast['int16'](self.numpydata)
        hashindex = {}
        i = 0 
        for i in ind :
            if hashindex[ind[0]] :
                hashindex[ind[0]] = [i]
            else :
               hashindex[ind[0]] = hashindex[ind[0]].append([i])
            i += 1
    """
    def gridshape(self,nblocks,MAX=32768):
         l0 = k0 = 1
         l = 1
         k = int(ceil(nblocks/float(l)))
         nbmin = MAX*MAX
         while (k > MAX or l < MAX ):
             l += 1
             k = int(ceil(nblocks/float(l)))
             cur = k*l
             if ( cur < nbmin  and l < MAX and k < MAX ):
                 l0 = l
                 k0 = k
                 nbmin = cur
         return (l0,k0)
                                                             
        
    def findsig(self,sigfile,minhammingdistanceinpercent = 1, maxhammingdistanceinpercent = 15):
        mod = SourceModule("""
        __global__ void findsig(unsigned long *a, int asize, unsigned long *sig, int sigsize , int distancemax, char  *result  )
        {            
        //const int offset = threadIdx.x+ blockDim.x*blockIdx.x + gridDim.x * blockIdx.y * blockDim.x ;
        const int offset = threadIdx.x+ (blockIdx.x + gridDim.x * blockIdx.y ) *  blockDim.x ;
            if ( offset < asize ) {
              unsigned long diff;   /*bit difference */
              int dist = 0;         /*total distance */
              for (int i = 0 ; i < sigsize ; i++) {        
                 if (dist > sigsize*64*distancemax/100 ) {
                       break;
                 }                    
                 diff = sig[i] ^ a[offset+i];  /*different bits */
                 while (diff ) { 
                    diff &= diff - 1;          /*lose a bit */
                    dist++;
                 }
              }
              result[offset] = dist*100/(sigsize*64) ; // (dist*100)/(sigsize*sizeof(unsigned long)*8) 
            }
            
            //result[offset] +=  offset ;
        }
        """)
        func = mod.get_function("findsig")
        

   	#sig = self.getsig(sigfile,framestart,framestop)
	sig = sigfile 
        sigsize = sig.size
        asize = self.numpydata.size
        #print "Request sig size = %i " % sigsize
        
        #duration = datetime.timedelta(seconds=asize/25)
        

        dest = numpy.zeros(self.numpydata.shape,numpy.uint8)

        nbthread = 512
        nbblocks = int(ceil(asize/float(nbthread)))
        gridsize = self.gridshape(nbblocks)
        print "Nb blocks = %d " % nbblocks 
        print "Grid size %dx%d " % gridsize
            
        func(self.devicealloc_sigdb,numpy.int32(asize),cuda.In(sig),numpy.int32(sigsize),\
                 numpy.int32(maxhammingdistanceinpercent),cuda.Out(dest),\
                 block = (nbthread, 1, 1), grid=gridsize)
        
        results = []

        #numpy.savetxt('/tmp/result.dat', dest,fmt="%i" )
        print "GPGPU compute done "
        
        for i in numpy.nonzero(dest <= minhammingdistanceinpercent)[0]:
            results.append(self.resolve(i))
        return results



def main():
    data = None
    request = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:r:", ["help","data","request"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-d", "--data"):
            data = a 
        if o in ("-r", "--request"):
            request = a 

    if data == None or request == None :
        print __doc__
        sys.exit(0)

    sig = numpy.fromfile(request,numpy.uint64)
    sc = sig4cuda()
    sc.add(data)
    sc.loadsig()
    print  sc.findsig(sig)


if __name__ == "__main__":
    main()
