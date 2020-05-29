# -*- coding: utf-8 -*-


import os

from PyQt5.QtWidgets import QDialogButtonBox
from qgis.PyQt import QtGui, uic, QtWidgets
from qgis.core import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChoixGroupe_base.ui'))

class FormChoixGroupe(QtWidgets.QDialog, FORM_CLASS):

    """
    Dialogue pour le choix du groupe après la connexion au serveur
    et récupération du profil utilisateur
    """

    # les groupes auxquels l'utilisateur appartient
    infosgeogroupes = None
    cancel = True


    def __init__(self, profil, parent=None):
        super(FormChoixGroupe, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Enregistrer")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")

        #Ajout des noms de groupes trouvés pour l'utilisateur
        self.infosgeogroupes = profil.infosGeogroupes
        for igg in self.infosgeogroupes:
            self.comboBoxGroupe.addItem(igg.groupe.nom)

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)


    def save(self):
        """
        Retourne l'identifiant du groupe de l'utilisateur
        en fonction de son choix
        """
        index = None
        idGroup = None
        index = self.comboBoxGroupe.currentIndex()
        idGroup = self.infosgeogroupes[index].groupe.id
        self.cancel = False
        self.close()
        return idGroup


    def cancel(self):
        self.cancel=True
        self.close()
