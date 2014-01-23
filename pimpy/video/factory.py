#-*- coding:utf-8 -*-

# pimpy 
# Copyright (C) 2010 Sebastien Campion <sebastien.campion@inria.fr>
#
# pimpy is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pimpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pimpy; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import logging 

log = logging.getLogger('pimpy.video.factory')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

FEATURES={}

from pimpy.video.features.bindct import BinDCT
FEATURES['bindct']=BinDCT

try:
    from pimpy.video.features.gist import GIST 
    FEATURES['gist']=GIST
except ImportError:
    log.warning("No video gist feature available")
    pass

from pimpy.video.features.histogram import HistogramRGB, HistogramSampled4dRGBAMassNormed, HistogramGray
FEATURES["histogramrgb"]=HistogramRGB
FEATURES["histogramsampled4drgbamassnormed"]=HistogramSampled4dRGBAMassNormed
FEATURES["histogramgray"]=HistogramGray

"""
from pimpy.video.features.goodfeaturestotrack import GoodFeaturesToTrack
FEATURES["goodfeaturestotrack"]=GoodFeaturesToTrack
"""

try: 
    from pimpy.video.features.surf import Surf
    FEATURES["surf"]=Surf
except ImportError:
    log.warning("No video surf features available")
    log.warning(FEATURES.keys)
    pass

try : 
    from pimpy.video.features.sift import Sift
    FEATURES["sift"]=Sift
except ImportError:
    log.warning("No video sift feature available")
    pass

class FeatureFactory(object):
    u"""
    A *factory* to build feature
    """
    @staticmethod
    def get_feature(feature_name,**kwargs):
        u"""
        Returns the feature which stands for *feature_name*        
        The feature is already instanciated with \*args and \*\*kwargs
        """
        if feature_name not in FEATURES.keys():
            raise NotImplementedError("Feature %s not available" % feature_name)
        return FEATURES[feature_name](**kwargs)
    
    @staticmethod
    def list():
        u"""
        Returns list of available feature
        """
        return FEATURES.keys()




