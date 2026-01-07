# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormSmartCutConfig_base.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_DialogSmartCutConfig(object):
    def setupUi(self, DialogSmartCutConfig):
        if not DialogSmartCutConfig.objectName():
            DialogSmartCutConfig.setObjectName(u"DialogSmartCutConfig")
        DialogSmartCutConfig.resize(550, 500)
        DialogSmartCutConfig.setStyleSheet(u"QDialog {background-color: rgb(255, 255, 255)}")
        self.verticalLayout = QVBoxLayout(DialogSmartCutConfig)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelTitle = QLabel(DialogSmartCutConfig)
        self.labelTitle.setObjectName(u"labelTitle")
        self.labelTitle.setWordWrap(True)

        self.verticalLayout.addWidget(self.labelTitle)

        self.labelDescription = QLabel(DialogSmartCutConfig)
        self.labelDescription.setObjectName(u"labelDescription")
        self.labelDescription.setWordWrap(True)

        self.verticalLayout.addWidget(self.labelDescription)

        self.verticalSpacer1 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer1)

        self.groupBoxLayer = QGroupBox(DialogSmartCutConfig)
        self.groupBoxLayer.setObjectName(u"groupBoxLayer")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxLayer)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.labelLayerInfo = QLabel(self.groupBoxLayer)
        self.labelLayerInfo.setObjectName(u"labelLayerInfo")
        self.labelLayerInfo.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.labelLayerInfo)

        self.listAvailableFields = QListWidget(self.groupBoxLayer)
        self.listAvailableFields.setObjectName(u"listAvailableFields")
        self.listAvailableFields.setSelectionMode(QAbstractItemView.MultiSelection)

        self.verticalLayout_2.addWidget(self.listAvailableFields)

        self.btnRefreshLayer = QPushButton(self.groupBoxLayer)
        self.btnRefreshLayer.setObjectName(u"btnRefreshLayer")

        self.verticalLayout_2.addWidget(self.btnRefreshLayer)


        self.verticalLayout.addWidget(self.groupBoxLayer)

        self.groupBoxUnique = QGroupBox(DialogSmartCutConfig)
        self.groupBoxUnique.setObjectName(u"groupBoxUnique")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxUnique)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.labelUniqueInfo = QLabel(self.groupBoxUnique)
        self.labelUniqueInfo.setObjectName(u"labelUniqueInfo")
        self.labelUniqueInfo.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.labelUniqueInfo)

        self.listUniqueAttrs = QListWidget(self.groupBoxUnique)
        self.listUniqueAttrs.setObjectName(u"listUniqueAttrs")
        self.listUniqueAttrs.setSelectionMode(QAbstractItemView.MultiSelection)

        self.verticalLayout_3.addWidget(self.listUniqueAttrs)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnAddToUnique = QPushButton(self.groupBoxUnique)
        self.btnAddToUnique.setObjectName(u"btnAddToUnique")

        self.horizontalLayout.addWidget(self.btnAddToUnique)

        self.btnRemoveFromUnique = QPushButton(self.groupBoxUnique)
        self.btnRemoveFromUnique.setObjectName(u"btnRemoveFromUnique")

        self.horizontalLayout.addWidget(self.btnRemoveFromUnique)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBoxUnique)

        self.buttonBox = QDialogButtonBox(DialogSmartCutConfig)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DialogSmartCutConfig)
        self.buttonBox.accepted.connect(DialogSmartCutConfig.accept)
        self.buttonBox.rejected.connect(DialogSmartCutConfig.reject)

        QMetaObject.connectSlotsByName(DialogSmartCutConfig)
    # setupUi

    def retranslateUi(self, DialogSmartCutConfig):
        DialogSmartCutConfig.setWindowTitle(QCoreApplication.translate("DialogSmartCutConfig", u"Configuration - D\u00e9coupe intelligente", None))
        self.labelTitle.setText(QCoreApplication.translate("DialogSmartCutConfig", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Configuration de la d\u00e9coupe intelligente</span></p></body></html>", None))
        self.labelDescription.setText(QCoreApplication.translate("DialogSmartCutConfig", u"S\u00e9lectionnez les attributs qui doivent rester uniques.\n"
"Lors d'une d\u00e9coupe, ces attributs ne seront conserv\u00e9s que sur le plus grand morceau (polygone) ou le segment le plus long (ligne).", None))
        self.groupBoxLayer.setTitle(QCoreApplication.translate("DialogSmartCutConfig", u"Attributs de la couche active", None))
        self.labelLayerInfo.setText(QCoreApplication.translate("DialogSmartCutConfig", u"<i>Aucune couche s\u00e9lectionn\u00e9e</i>", None))
        self.btnRefreshLayer.setText(QCoreApplication.translate("DialogSmartCutConfig", u"\u27f3 Actualiser depuis la couche active", None))
        self.groupBoxUnique.setTitle(QCoreApplication.translate("DialogSmartCutConfig", u"Attributs uniques configur\u00e9s", None))
        self.labelUniqueInfo.setText(QCoreApplication.translate("DialogSmartCutConfig", u"Ces attributs seront conserv\u00e9s uniquement sur le plus grand polygone:", None))
        self.btnAddToUnique.setText(QCoreApplication.translate("DialogSmartCutConfig", u"\u2b07 Ajouter aux attributs uniques", None))
        self.btnRemoveFromUnique.setText(QCoreApplication.translate("DialogSmartCutConfig", u"\u2716 Retirer", None))
    # retranslateUi

