#-*- coding:utf-8 -*-"""

u"""
pimpy.image.features.gist : image gist using http://pypi.python.org/pypi/pyleargist/

.. module:: gist
   :synopsis: Tools for video 
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
# You should have received a copy of the GNU General Public License
# along with pimpy; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from feature import Feature

try :
    import leargist 
except: 
    raise ImportError("Module leargist seems to be unavailable, please install it")


class GIST(Feature):
    u"""
    An gist image descriptor using pyleargist. 
    See alsohttp://pypi.python.org/pypi/pyleargist/
    """
    name = "gist"
    description = __doc__


    def get(self,image):
        """
        get gist descriptor

        :rtype: list of tuple (histo,bin_edges)
        """
        return leargist.color_gist(image.get_pil_object())

