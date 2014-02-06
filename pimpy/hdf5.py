import os,hashlib
import h5py, logging 
import pimpy
import numpy

class File(h5py.File):
    u"""
    
    :class attributes:
        * .. attribute:: groups
            visual or audio

    """        
    groups = ["visual","audio"]
    def __init__(self,file_path,mediafile_path=None,block_size=1000000):
        """
        Constructor 

        :param file_path:  hdf5 file path 
        :type:   string
        :param mediafile_path: medium file path 
        :type: string
        """
        self.log = logging.getLogger("pimpy.hdf5.File")

        exists = os.path.exists(file_path)

        h5py.File.__init__(self,file_path,driver='core', block_size=block_size)

        if not exists :
            self._create_empty()

        self._check_version()

        if not exists and not mediafile_path :
            raise NameError("mediafile_path is mandatory at pimpy file creation") 
        
        if mediafile_path is None :
            #hdf5 file opened, all is ok 
            return 
        
        # first file access or update 
        mp = os.path.abspath(mediafile_path)
        
        if not os.path.exists(mp): 
            raise NameError("Mediafile %s not found" % mp)

        if 'medium' in self.attrs.keys() and \
                self.attrs['medium'] != mp :
            self.relocate(mp)
        else : 
            self.log.debug("set medium attribute to %s" % mp)
            self.attrs["medium"] = mp    
            self._set_md5_mediafile()
        #self.flush()

    def close(self):
        """
        flush data and close file 
        """
        self.flush()
        h5py.File.close(self)

    def create_avfeature_set(self,group,name,desc_datasets,timescale=None):
        """
        create a new AudioVisual feature dataset
        
        :param: group like visual, audio
        :type: string
        :param: feature name
        :type:  string
        :param: desc_datasets tuple which describe feature structure
        :type: tuple (name:string,number of dimension:int,datatype= numpy.dtype)
        :param: timescale in microseconds
        :type: int
        :rtype: dict of pynocchio.dataset
        """
        r = {}
	
        fsgroup = self[group].create_group(name)        

        if len(desc_datasets) == 1 : 
            name, nbdim, dtype = desc_datasets[0]
            r[name] = FeatureSet(fsgroup,timescale,nbdim,dtype)

        elif len(desc_datasets) > 1 : 
            for name, nbdim, dtype in desc_datasets :            
                fs = fsgroup.create_group(name)        
                r[name] = FeatureSet(fs,timescale,nbdim,dtype)

        else: 

            raise ValueError("No dataset description provided") 

        return r 

    def get_avfeature_set(self,group,name):
        """
        retrieve Audiovisual features dataset
        :rtype: dataset
        """
        if not name in self[group].keys(): 
            return None
        r = {}
        fs = self[group][name]
        for n,ds in fs.items():
            #if fs does'nt contain other fs
            #TODO test if class is Group or Dataset
            if n in ['data','dataref']: 
                r[name] = FeatureSet(fs)
                break
            r[n] = FeatureSet(ds)
        return r

    def _create_empty(self):
        self.attrs["version"] = pimpy.version
        for g in self.groups:
            if g not in [name for name,hfg in self.items()] : 
                self.log.debug("Init group %s" % g)
                h5py.File.create_group(self,g)

    
#     def create_group(self,name):
#         """
#         Not available
#         """
#         raise NotImplementedError("function create_group disabled")
        
    def getmediafilepath(self):
        """
        return the associated mediafile path 
        :rtype string:  mediafile path
        """
        return self.attrs["medium"] 
        
    def relocate(self,mediafile_path):
        """
        relocate mediafile_path if changed and md5 value not differ 
        :param mediafile_path: media file path
        :type: string 
        """
        self.log.debug("medium relocated %s " % mediafile_path)
        mp = os.path.abspath(mediafile_path)
        new_md5 = self._md5(mp)
        if new_md5 != self.getmediafileMD5():
            msg  = "New media file MD5 checksum differ."
            msg += "\n\tCurrent : " + self.getmediafileMD5().tostring()
            msg += "\n\tNew : " + new_md5
            raise NameError(msg)
        else:
            self.attrs["medium"] = mp


    def getmediafileMD5(self):
        """
        return the MD5 checksum associated with the mediafile
        :rtype string: MD5 mediafile hash string
        """
        return self.attrs["md5"] 

    def _set_md5_mediafile(self):
        mp = self.attrs["medium"]
	#self.attrs["md5"] = self._md5(mp)

    def _md5(self,path):
        m = hashlib.md5()
        return m.digest()
        
    def _check_version(self):
        #TODO test <= 
        try : 
            version = self.attrs["version"] 
        except KeyError:
            raise NameError("No version attribute found in this file ") 

        self.log.debug("File datamodel version "+version)

        if version != pimpy.version :
            msg  = "Error pio version not compatible "
            msg += "file version %s " % version
            msg += "module version %s " % pimpy.version
            raise NotImplementedError(msg)
                

class FeatureSet(h5py.highlevel.Group): 
    u"""
     FeatureSet  class 
    """        
    def __init__(self,fs,timescale=None,nbdim=None,dtype=None):
        """
        create av feature set

        :param fs: feature hdf5 group 
        :type: h5py.Group
        :param timescale: time scale in microsecond 
        :type: int
        :param nbdim: number of dimemsions 
        :type: int
        :param dtype: datatype 
        :type: numpy.dtype
        """
        self.log = logging.getLogger("pynocchio.FeatureSet")
        #ugly hack but inheritance 
        #isn't supported on h5py.highlevel.Group
        self.ds = fs        
        if not self.ds.items():
            self.dtype = dtype
            self.nbdim = nbdim
            if timescale is not None :
                self.ds.attrs["timescale"] = timescale

        else:
            self.log.debug(self.ds.items())
            self.dtype = self.ds["data"].dtype
            self.nbdim = self.ds["data"].shape[1]

        if "data" in [name for name, ds in self.ds.items()]:
            self.data = self.ds["data"]
        if "dataref" in [name for name, ds in self.ds.items()]:
            self.dataref = self.ds["dataref"]
        if "timeref" in [name for name, ds in self.ds.items()]:
            self.timeref = self.ds["timeref"]

    def write(self,array,begin=None,end=None):
        """
        write array data in FeatureSet must [data] or [[data1,data2,..]]

        :param array: data
        :type: numpy.array
        :param begin: start time
        :type: int
        :param end: stop time
        :type: int
        """
        self._check_array_shape(array)

        region_ref = self._write_data(array)
        self._write_dataref(region_ref,begin,end)
        self._write_timeref(begin,end)

        #self.log.debug("memory usage %i \n" % resource.getrusage(resource.RUSAGE_SELF)[2]*resource.getpagesize())


    def _write_data(self,array):
        if not hasattr(self, 'data') : #first access, create dataset
            self.data = self.ds.create_dataset("data",
                                               (len(array),self.nbdim),
                                               dtype = self.dtype,
                                               maxshape=(None, None),
					       chunks = (len(array),self.nbdim),
                                               compression = 'gzip',
                                               compression_opts = 9,
                                               shuffle = True )
            #Todo optimize compression with best chunks values
            i = 0
            nbdim = self.nbdim
        else : 
            i,nbdim = self.data.shape
            self.data.resize((i+len(array),nbdim))

        self.data[i:] = array

        return self.data.regionref[i : i+len(array)]


    def _write_dataref(self,regionref,begin,end):        
        if not hasattr(self, 'dataref') : #first access, create dataset
            dref_dtype = h5py.special_dtype(ref=h5py.RegionReference)
            self.dataref = self.ds.create_dataset("dataref",(1,),dtype=dref_dtype, maxshape=(None,), chunks=(1,))
            i = 0             
        else:
            i, = self.dataref.shape
            self.dataref.resize((i+1,))     
        self.dataref[i] = regionref

    def _write_timeref(self,begin,end):
        if not hasattr(self, 'timeref') : #first access, create dataset
            if begin == end == None :
                return 
            elif end != None :
                self.timeref = self.ds.create_dataset("timeref",(1,2),dtype=numpy.uint64, maxshape=(None, None), chunks=(1,2))
            else :
                #position timeref
                self.timeref = self.ds.create_dataset("timeref",(1,1),dtype=numpy.uint64, maxshape=(None, None), chunks=(1,1))
            i = 0             
        else:
            i,trdim = self.timeref.shape
            self.timeref.resize( (i+1 , trdim) )
        
        if end == None :
            self.timeref[i] = [begin]
        else :
            self.timeref[i] = [begin,end]


    def _check_array_shape(self,array):
        try : 
            len_array,nbdim_array = array.shape        
        except ValueError:
            raise ValueError("You array shape must be (nb_features,"+str(self.nbdim)\
                                 +" submitted array shape is "+ str(array.shape))

        if self.nbdim != nbdim_array :
            raise ValueError("You array shape must be (nb_features,"+str(self.nbdim)\
                                 +" submitted array shape is "+ str(array.shape))

    def read(self,begin=None,end=None):
        """
        return array data (shape [data] or [[data1,data2,..]])

        :param begin: start time
        :type: int
        :param end: stop time
        :type: int
        :rtype: numpy.array
        """
        if not hasattr(self,'timeref') or begin == None or end == None :
            #r = numpy.array(self.data)
            #return r.reshape(-1,self.nbdim)
            results = [] 
            for regionref in self.dataref :
                r = self.data[regionref]
                #h5py return flat array
                r = r.reshape(-1,self.nbdim)
                results.append(r)        
            return numpy.array(results,dtype="object")             
    
   
        self.log.debug("Read @ %i : %i " % (begin,end))
        b,e = numpy.hsplit(self.timeref,2)
        i = (b >= begin ) & (e <= end )

        results = [] 
        for f in numpy.flatnonzero(i):
            regionref = self.dataref[f]
            r = self.data[regionref]
            #h5py return flat array
            r = r.reshape(-1,self.nbdim)
            results.append(r)
                        
        return numpy.array(results,dtype="object")
        

        





    
        
