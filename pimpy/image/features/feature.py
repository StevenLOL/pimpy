#-*- coding:utf-8 -*-

"""
pimpy.image.feature : abstract feature class object

.. module:: feature
   :synopsis: Tools for image description 
   :platform: Unix, Mac, Windows

.. moduleauthor:: Sebastien Campion <sebastien.campion@inria.fr>
"""

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
class Feature(object):
    u"""
    This base class describes an feature about image
    :param kwargs: an optional dict
    
    The constructor sets instance attributes from *kwargs*
    
    :class attributes:
        * .. attribute:: name
            The name of the feature
        * .. attribute:: description
            The description of the feature
    """       
    name = "API"
    description = ""


    def __init__(self,**kwargs):
	self.__dict__.update(kwargs)


    def get(self,image):
        u"""
        get the feature descriptor of the image

        :param image: image object 
        :type:  pimpy.image.image
        """
        raise NotImplementedError
        
