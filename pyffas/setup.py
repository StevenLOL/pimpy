from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules=[
    Extension("pyffas",
              ["pyffas.pyx"],
              libraries=["swscale","avcodec","avformat","avutil"]) 
]

setup(
  name = "pyffas",
  cmdclass = {"build_ext": build_ext},
  ext_modules = ext_modules,
  version = "0.1",
  description = "Python module for FFMpeg Fast Accurate Seeking",
  author = "Sebastien Campion",
  author_email = "sebastien.campion@inria.fr"
)
