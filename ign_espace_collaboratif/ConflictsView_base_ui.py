# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConflictsView_base.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from qgis.PyQt.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from qgis.PyQt.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from qgis.PyQt.QtWidgets import (QApplication, QDialog, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_ConflictsView(object):
    def setupUi(self, ConflictsView):
        if not ConflictsView.objectName():
            ConflictsView.setObjectName(u"ConflictsView")
        ConflictsView.resize(1026, 606)
        self.label_type_conflict = QLabel(ConflictsView)
        self.label_type_conflict.setObjectName(u"label_type_conflict")
        self.label_type_conflict.setGeometry(QRect(20, 10, 171, 31))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        self.label_type_conflict.setFont(font)
        self.label_layer_name = QLabel(ConflictsView)
        self.label_layer_name.setObjectName(u"label_layer_name")
        self.label_layer_name.setGeometry(QRect(20, 60, 271, 21))
        font1 = QFont()
        font1.setPointSize(10)
        self.label_layer_name.setFont(font1)
        self.label_context_type_conflict = QLabel(ConflictsView)
        self.label_context_type_conflict.setObjectName(u"label_context_type_conflict")
        self.label_context_type_conflict.setGeometry(QRect(270, 10, 731, 31))
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.label_context_type_conflict.setFont(font2)
        self.tableWidget_attributes = QTableWidget(ConflictsView)
        if (self.tableWidget_attributes.columnCount() < 4):
            self.tableWidget_attributes.setColumnCount(4)
        self.tableWidget_attributes.setObjectName(u"tableWidget_attributes")
        self.tableWidget_attributes.setGeometry(QRect(20, 100, 981, 481))
        self.tableWidget_attributes.setColumnCount(4)
        self.pushButton_conflict_create_report = QPushButton(ConflictsView)
        self.pushButton_conflict_create_report.setObjectName(u"pushButton_conflict_create_report")
        self.pushButton_conflict_create_report.setGeometry(QRect(510, 50, 40, 40))
        self.pushButton_conflict_create_report.setIconSize(QSize(32, 32))
        self.pushButton_conflict_previous = QPushButton(ConflictsView)
        self.pushButton_conflict_previous.setObjectName(u"pushButton_conflict_previous")
        self.pushButton_conflict_previous.setGeometry(QRect(560, 50, 40, 40))
        self.pushButton_conflict_previous.setIconSize(QSize(32, 32))
        self.pushButton_conflict_next = QPushButton(ConflictsView)
        self.pushButton_conflict_next.setObjectName(u"pushButton_conflict_next")
        self.pushButton_conflict_next.setGeometry(QRect(610, 50, 40, 40))
        self.pushButton_conflict_next.setIconSize(QSize(32, 32))
        self.pushButton_conflict_see_all_fields = QPushButton(ConflictsView)
        self.pushButton_conflict_see_all_fields.setObjectName(u"pushButton_conflict_see_all_fields")
        self.pushButton_conflict_see_all_fields.setGeometry(QRect(660, 50, 40, 40))
        self.pushButton_conflict_see_all_fields.setIconSize(QSize(32, 32))
        self.pushButton_conflict_reload = QPushButton(ConflictsView)
        self.pushButton_conflict_reload.setObjectName(u"pushButton_conflict_reload")
        self.pushButton_conflict_reload.setGeometry(QRect(710, 50, 40, 40))
        self.pushButton_conflict_reload.setIconSize(QSize(32, 32))
        self.pushButton_conflict_create = QPushButton(ConflictsView)
        self.pushButton_conflict_create.setObjectName(u"pushButton_conflict_create")
        self.pushButton_conflict_create.setGeometry(QRect(760, 50, 40, 40))
        self.pushButton_conflict_create.setIconSize(QSize(32, 32))
        self.pushButton_conflict_delete = QPushButton(ConflictsView)
        self.pushButton_conflict_delete.setObjectName(u"pushButton_conflict_delete")
        self.pushButton_conflict_delete.setGeometry(QRect(810, 50, 40, 40))
        self.pushButton_conflict_delete.setIconSize(QSize(32, 32))
        self.pushButton_conflict_validate = QPushButton(ConflictsView)
        self.pushButton_conflict_validate.setObjectName(u"pushButton_conflict_validate")
        self.pushButton_conflict_validate.setGeometry(QRect(860, 50, 40, 40))
        self.pushButton_conflict_validate.setIconSize(QSize(32, 32))
        self.pushButton_conflict_validate_all = QPushButton(ConflictsView)
        self.pushButton_conflict_validate_all.setObjectName(u"pushButton_conflict_validate_all")
        self.pushButton_conflict_validate_all.setGeometry(QRect(910, 50, 40, 40))
        self.pushButton_conflict_validate_all.setIconSize(QSize(32, 32))
        self.pushButton_conflict_undo = QPushButton(ConflictsView)
        self.pushButton_conflict_undo.setObjectName(u"pushButton_conflict_undo")
        self.pushButton_conflict_undo.setGeometry(QRect(960, 50, 40, 40))
        self.pushButton_conflict_undo.setIconSize(QSize(32, 32))

        self.retranslateUi(ConflictsView)

        QMetaObject.connectSlotsByName(ConflictsView)
    # setupUi

    def retranslateUi(self, ConflictsView):
        ConflictsView.setWindowTitle(QCoreApplication.translate("ConflictsView", u"Gestion des conflits", None))
        self.label_type_conflict.setText(QCoreApplication.translate("ConflictsView", u"Type de conflit", None))
        self.label_layer_name.setText(QCoreApplication.translate("ConflictsView", u"Nom de la couche", None))
        self.label_context_type_conflict.setText(QCoreApplication.translate("ConflictsView", u"Le contexte du type de conflit", None))
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_create_report.setToolTip(QCoreApplication.translate("ConflictsView", u"Cr\u00e9er un nouveau signalement", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_create_report.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_previous.setToolTip(QCoreApplication.translate("ConflictsView", u"Aller au conflit pr\u00e9c\u00e9dent", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_previous.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_next.setToolTip(QCoreApplication.translate("ConflictsView", u"Aller au conflit suivant", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_next.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_see_all_fields.setToolTip(QCoreApplication.translate("ConflictsView", u"Afficher/Ne pas afficher tous les champs", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_see_all_fields.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_reload.setToolTip(QCoreApplication.translate("ConflictsView", u"S\u00e9lectionner toutes les zones de conflit", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_reload.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_create.setToolTip(QCoreApplication.translate("ConflictsView", u"Recr\u00e9er l'objet supprim\u00e9 sur le serveur", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_create.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_delete.setToolTip(QCoreApplication.translate("ConflictsView", u"Supprimer l'objet issu du serveur", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_delete.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_validate.setToolTip(QCoreApplication.translate("ConflictsView", u"Valider le conflit en cours", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_validate.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_validate_all.setToolTip(QCoreApplication.translate("ConflictsView", u"Valider tous les conflits s\u00e9lectionn\u00e9s", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_validate_all.setText("")
#if QT_CONFIG(tooltip)
        self.pushButton_conflict_undo.setToolTip(QCoreApplication.translate("ConflictsView", u"Annuler la derni\u00e8re manipulation", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_conflict_undo.setText("")
    # retranslateUi

