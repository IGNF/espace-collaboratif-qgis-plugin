# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RipartPlugin
                                 A QGIS plugin
 IGN_Ripart
                             -------------------
        begin                : 2015-01-21
        copyright            : (C) 2015 by Alexia Chang-Wailing/IGN
        email                : a
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

import sys 
sys.path.append(r'D:\eclipse\plugins\org.python.pydev_3.9.1.201501081637\pysrc') 
import pydevd   

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RipartPlugin class from file RipartPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .RipartModule import RipartPlugin
    return RipartPlugin(iface)
