# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReplyReportView_base.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ReplyReportView(object):
    def setupUi(self, ReplyReportView):
        ReplyReportView.setObjectName("ReplyReportView")
        ReplyReportView.resize(401, 328)
        ReplyReportView.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.StatutItemsSourceComboBox = QtWidgets.QComboBox(ReplyReportView)
        self.StatutItemsSourceComboBox.setGeometry(QtCore.QRect(120, 250, 271, 31))
        self.StatutItemsSourceComboBox.setObjectName("StatutItemsSourceComboBox")
        self.btn_sendResponse = QtWidgets.QPushButton(ReplyReportView)
        self.btn_sendResponse.setGeometry(QtCore.QRect(180, 290, 91, 31))
        self.btn_sendResponse.setObjectName("btn_sendResponse")
        self.lbl_newStatut = QtWidgets.QLabel(ReplyReportView)
        self.lbl_newStatut.setGeometry(QtCore.QRect(10, 240, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lbl_newStatut.setFont(font)
        self.lbl_newStatut.setObjectName("lbl_newStatut")
        self.lbl_response = QtWidgets.QLabel(ReplyReportView)
        self.lbl_response.setGeometry(QtCore.QRect(10, 55, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lbl_response.setFont(font)
        self.lbl_response.setObjectName("lbl_response")
        self.lbl_numberReportLabel = QtWidgets.QLabel(ReplyReportView)
        self.lbl_numberReportLabel.setGeometry(QtCore.QRect(10, 15, 381, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_numberReportLabel.setFont(font)
        self.lbl_numberReportLabel.setText("")
        self.lbl_numberReportLabel.setObjectName("lbl_numberReportLabel")
        self.pte_NewResponse = QtWidgets.QPlainTextEdit(ReplyReportView)
        self.pte_NewResponse.setGeometry(QtCore.QRect(10, 90, 381, 151))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pte_NewResponse.sizePolicy().hasHeightForWidth())
        self.pte_NewResponse.setSizePolicy(sizePolicy)
        self.pte_NewResponse.setObjectName("pte_NewResponse")

        self.retranslateUi(ReplyReportView)
        QtCore.QMetaObject.connectSlotsByName(ReplyReportView)

    def retranslateUi(self, ReplyReportView):
        _translate = QtCore.QCoreApplication.translate
        ReplyReportView.setWindowTitle(_translate("ReplyReportView", "Répondre au(x) signalement(s)"))
        self.btn_sendResponse.setText(_translate("ReplyReportView", "Enregistrer"))
        self.lbl_newStatut.setToolTip(_translate("ReplyReportView", "<html><head/><body><p>A propos des statuts de réponse</p><p><br/></p><p>En cours de traitement : le signalement est en cours d\'analyse ou de traitement par un responsable.</p><p><br/></p><p>En attente de saisie : la prise en compte effective du signalement nécessite un laps de temps plus long (attente de passage terrain par exemple). La mise à jour des données est donc différée.</p><p><br/></p><p>Pris en compte : le signalement est clos et a été pris en compte dans nos données.</p><p><br/></p><p>Déjà pris en compte : le signalement est clos. Aucune modification n\'a été faite dans les données car la mise à jour avait déjà été faite par ailleurs.</p><p><br/></p><p>Rejeté (hors spéc.) : le signalement est clos et n\'a pas été pris en compte car il n\'entre pas dans le champs des spécifications des données.</p><p><br/></p><p>Rejeté (hors de propos) : le signalement est clos et n\'a pas été pris en compte car hors de propos par rapport aux données.</p><p><br/></p><p><br/></p><p>La clôture d\'un signalement (un des 4 derniers statuts) nécessite l\'intervention d\'un valideur : votre gestionnaire de groupe. Le statut du signalement restera à en attente de validation tant qu\'il n\'aura pas validé votre réponse.</p><p><br/></p><p>Si le gestionnaire de groupe l\'a autorisé, la clôture du signalement peut également être automatique dès lors que vous choisissez un des 4 derniers statuts. </p></body></html>"))
        self.lbl_newStatut.setText(_translate("ReplyReportView", "Nouveau statut"))
        self.lbl_response.setText(_translate("ReplyReportView", "Ma réponse"))
