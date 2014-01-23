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

log = logging.getLogger('pimpy.image.factory')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

FEATURES={}

from features.bindct import BinDCT
FEATURES['bindct']=BinDCT

try:
    from features.gist import GIST 
    FEATURES['gist']=GIST
except ImportError:
    log.info("No gist feature available")
    pass

from features.histogram import HistogramRGB, HistogramSampled4dRGBA, HistogramGray
FEATURES["histogramrgb"]=HistogramRGB
FEATURES["histogramsampled4drgba"]=HistogramSampled4dRGBA
FEATURES["histogramgray"]=HistogramGray


try:
    from features.goodfeaturestotrack import GoodFeaturesToTrack
    FEATURES["goodfeaturestotrack"]=GoodFeaturesToTrack
except ImportError:
    log.warning("No GoodFeaturesToTrack features available")
    pass

try: 
    from features.surf import Surf
    FEATURES["surf"]=Surf
except ImportError:
    log.warning("No surf feature available")
    pass

try:
    from features.sift import Sift
    FEATURES["sift"]=Sift
except ImportError:
    log.warning("No sift feature available")
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
        if feature_name in FEATURES.keys() : 
            return FEATURES[feature_name](**kwargs)
        else :
            msg = "feature %s not available " % feature_name
            log.error(msg)
            raise NotImplementedError(msg)
    
    @staticmethod
    def list():
        u"""
        Returns list of available feature
        """
        return FEATURES.keys()
