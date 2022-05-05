# -*- coding: utf-8 -*-
"""
Created on 7 aug. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse
"""


from qgis.core import QgsProject
from PyQt5.QtWidgets import QMessageBox


class RecordChanges(object):

    def __init__(self):
        self.nodeGroups = QgsProject.instance().layerTreeRoot().findGroups()
        if len(self.nodeGroups) != 0:
            self.message = "Groupe {}\n\n".format(self.nodeGroups[0].name())

        self.title = "Enregistrement des modifications"

    def doRecord(self):
        # Affichage du résultat
        QMessageBox.information(None, self.title, "En travaux ;-)")
