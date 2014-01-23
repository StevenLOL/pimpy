import os,urllib

class multimediaData():
    image_url = "http://www-2.cs.cmu.edu/~chuck/lennapg/lena_std.tif"
    video_url = "http://blip.tv/file/get/Commonscreative-ScienceCommonsJesseDylan858.ogv"
    #FIXME add mirror urls 
    
    def __init__(self): 
        self.videoname = "Commonscreative-ScienceCommonsJesseDylan858.ogv"
        self.video_path = self.download(self.videoname,self.video_url)
        self.video_uri = "file://"+self.video_path
        self.image_path = self.download("lenna.tif",self.image_url)

    def download(self,name,url):
        path = os.path.abspath(".")
        path = os.path.join(path,name)

        if not os.path.exists(path):
            print "No local version, retrieve it from the web : "
            print url 
            urllib.urlretrieve(url,path)
        return path
    




