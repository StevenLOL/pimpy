from distutils.core import setup
v = file('VERSION').read().strip()

setup(
    name = "pimpy",
    packages = ['pimpy',
                'pimpy.audio',
                'pimpy.gpgpu',
                'pimpy.image',
                'pimpy.image.features',
                'pimpy.video',
                'pimpy.video.features'],

    version = v,
    description = "Platform for Indexing Multimedia content",
    author = "Sebastien Campion",
    author_email = "sebastien.campion@inria.fr",
    url = "http://pim.gforge.inria.fr/pimpy/",
    download_url = "http://pim.gforge.inria.fr/releases/pimpy-%s.tgz" % v ,
    keywords = ["video","shot detector","cbir","clustering","gist"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Video",
        ],
    long_description = """\
Plateform for Indexing Multimedia
-------------------------------------

Is a dedicated toolkit to audio, video indexing treatment.
This project comes from TEXMEX research team works.
For more information, see http://www.irisa.fr/texmex/
"""
)
