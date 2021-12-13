# -*- coding: utf-8 -*-
"""
Created on 7 aug. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse
"""


from qgis.core import QgsProject
from PyQt5.QtWidgets import QMessageBox


class CompterGuichet(object):

    def __init__(self):
        self.nodeGroups = QgsProject.instance().layerTreeRoot().findGroups()
        if len(self.nodeGroups) != 0:
            self.message = "Groupe {}\n\n".format(self.nodeGroups[0].name())

        self.title = "Comptage"

    def doCount(self):
        # si pas de groupe : warning
        if len(self.nodeGroups) == 0:
            QMessageBox.warning(None, self.title, u"Pas de groupe actif")
        else:
            # indice 0 parce que le projet ne comporte qu'un seul groupe
            layersId = self.nodeGroups[0].findLayerIds()
            for layerId in layersId:
                qgsmaplayer = QgsProject.instance().mapLayer(layerId)
                print("Différentiel")
                qgsmaplayer.doDifferentielAfterBeforeWorks()
                layerName = qgsmaplayer.name()
                print("Comptage : {}".format(layerName))
                stat = qgsmaplayer.getStat()
                stat.count()
                self.message += "{}\n".format(layerName)
                self.message += stat.countToDialog(layerName)

            # Affichage du résultat
            QMessageBox.information(None, self.title, self.message)
