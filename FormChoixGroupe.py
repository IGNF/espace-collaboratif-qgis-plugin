# -*- coding: utf-8 -*-
"""
Created on 25 nov. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""


import os
from PyQt5.QtWidgets import QDialogButtonBox

from qgis.PyQt import uic, QtWidgets
from .core import ConstanteRipart as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChoixGroupe_base.ui'))


class FormChoixGroupe(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue pour le choix du groupe après la connexion au serveur
    et récupération du profil utilisateur
    """
    infosgeogroupes = None
    bCancel = True

    def __init__(self, profil, groupeActif, parent=None):
        super(FormChoixGroupe, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()

        #Ajout des noms de groupes trouvés pour l'utilisateur
        self.infosgeogroupes = profil.infosGeogroupes
        for igg in self.infosgeogroupes:
            self.comboBoxGroupe.addItem(igg.groupe.nom)

        if groupeActif is not None and groupeActif != "":
            self.comboBoxGroupe.setCurrentText(groupeActif)

        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)

    def save(self):
        """
        Retourne l'identifiant du groupe de l'utilisateur
        en fonction de son choix
        """
        self.accept()
        index = self.comboBoxGroupe.currentIndex()
        idGroup = self.infosgeogroupes[index].groupe.id
        nomGroup = self.infosgeogroupes[index].groupe.nom
        self.bCancel = False

        return idGroup, nomGroup

    def cancel(self):
        self.bCancel = True
        self.reject()
