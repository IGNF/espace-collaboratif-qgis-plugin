# -*- coding: utf-8 -*-


import os

from PyQt5.QtWidgets import QDialogButtonBox

from qgis.PyQt import QtGui, uic, QtWidgets
from qgis.core import *
from .core import ConstanteRipart as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChoixGroupe_base.ui'))

class FormChoixGroupe(QtWidgets.QDialog, FORM_CLASS):

    """
    Dialogue pour le choix du groupe après la connexion au serveur
    et récupération du profil utilisateur
    """

    # les groupes auxquels l'utilisateur appartient
    infosgeogroupes = None
    cancel = True


    def __init__(self, profil, cleGeoportail, groupeActif, parent=None):
        super(FormChoixGroupe, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()

        #Ajout des noms de groupes trouvés pour l'utilisateur
        self.infosgeogroupes = profil.infosGeogroupes
        for igg in self.infosgeogroupes:
            self.comboBoxGroupe.addItem(igg.groupe.nom)

        if groupeActif != None and groupeActif != "":
            self.comboBoxGroupe.setCurrentText(groupeActif)

        if cleGeoportail == cst.DEMO:
            self.radioButtonNon.setChecked(True)
        if cleGeoportail != cst.DEMO and cleGeoportail != "":
            self.radioButtonOui.setChecked(True)
            self.lineEditCleGeoportailUser.setText(cleGeoportail)

        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
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
        nomGroup = self.infosgeogroupes[index].groupe.nom
        cleGeoportail = ""
        if self.radioButtonOui.isChecked() == True:
            cleGeoportail = self.lineEditCleGeoportailUser.text()
        if self.radioButtonNon.isChecked() == True:
            cleGeoportail = cst.DEMO
        self.cancel = False
        self.close()
        return (idGroup, nomGroup, cleGeoportail)


    def cancel(self):
        self.cancel=True
        self.close()
