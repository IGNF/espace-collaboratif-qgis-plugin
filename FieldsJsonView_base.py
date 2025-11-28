# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FieldsJsonView_base.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDialog,
    QLabel, QPushButton, QSizePolicy, QTextEdit,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(531, 406)
        self.pushButtonModify = QPushButton(Dialog)
        self.pushButtonModify.setObjectName(u"pushButtonModify")
        self.pushButtonModify.setGeometry(QRect(420, 370, 93, 28))
        self.pushButtonCancel = QPushButton(Dialog)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")
        self.pushButtonCancel.setGeometry(QRect(310, 370, 93, 28))
        self.pushbuttonAddJsonField = QPushButton(Dialog)
        self.pushbuttonAddJsonField.setObjectName(u"pushbuttonAddJsonField")
        self.pushbuttonAddJsonField.setGeometry(QRect(490, 10, 28, 28))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.pushbuttonAddJsonField.setFont(font)
        self.pushButtonRemoveJsonField = QPushButton(Dialog)
        self.pushButtonRemoveJsonField.setObjectName(u"pushButtonRemoveJsonField")
        self.pushButtonRemoveJsonField.setGeometry(QRect(10, 110, 28, 28))
        font1 = QFont()
        font1.setPointSize(18)
        font1.setBold(True)
        self.pushButtonRemoveJsonField.setFont(font1)
        self.labelJsonField = QLabel(Dialog)
        self.labelJsonField.setObjectName(u"labelJsonField")
        self.labelJsonField.setGeometry(QRect(20, 10, 201, 21))
        font2 = QFont()
        font2.setPointSize(9)
        self.labelJsonField.setFont(font2)
        self.labelField_1 = QLabel(Dialog)
        self.labelField_1.setObjectName(u"labelField_1")
        self.labelField_1.setGeometry(QRect(60, 40, 150, 18))
        self.labelField_2 = QLabel(Dialog)
        self.labelField_2.setObjectName(u"labelField_2")
        self.labelField_2.setGeometry(QRect(60, 70, 150, 18))
        self.labelField_3 = QLabel(Dialog)
        self.labelField_3.setObjectName(u"labelField_3")
        self.labelField_3.setGeometry(QRect(60, 100, 150, 18))
        self.labelField_4 = QLabel(Dialog)
        self.labelField_4.setObjectName(u"labelField_4")
        self.labelField_4.setGeometry(QRect(60, 130, 150, 18))
        self.labelField_5 = QLabel(Dialog)
        self.labelField_5.setObjectName(u"labelField_5")
        self.labelField_5.setGeometry(QRect(60, 160, 150, 18))
        self.labelField_6 = QLabel(Dialog)
        self.labelField_6.setObjectName(u"labelField_6")
        self.labelField_6.setGeometry(QRect(60, 190, 150, 18))
        self.labelField_7 = QLabel(Dialog)
        self.labelField_7.setObjectName(u"labelField_7")
        self.labelField_7.setGeometry(QRect(60, 220, 150, 18))
        self.labelField_8 = QLabel(Dialog)
        self.labelField_8.setObjectName(u"labelField_8")
        self.labelField_8.setGeometry(QRect(60, 250, 150, 18))
        self.labelField_9 = QLabel(Dialog)
        self.labelField_9.setObjectName(u"labelField_9")
        self.labelField_9.setGeometry(QRect(60, 280, 150, 18))
        self.labelField_10 = QLabel(Dialog)
        self.labelField_10.setObjectName(u"labelField_10")
        self.labelField_10.setGeometry(QRect(60, 310, 150, 18))
        self.comboBox_2 = QComboBox(Dialog)
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setGeometry(QRect(220, 70, 250, 23))
        self.comboBox_4 = QComboBox(Dialog)
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setGeometry(QRect(220, 130, 250, 23))
        self.comboBox_5 = QComboBox(Dialog)
        self.comboBox_5.setObjectName(u"comboBox_5")
        self.comboBox_5.setGeometry(QRect(220, 160, 250, 23))
        self.comboBox_6 = QComboBox(Dialog)
        self.comboBox_6.setObjectName(u"comboBox_6")
        self.comboBox_6.setGeometry(QRect(220, 190, 250, 23))
        self.comboBox_7 = QComboBox(Dialog)
        self.comboBox_7.setObjectName(u"comboBox_7")
        self.comboBox_7.setGeometry(QRect(220, 220, 250, 23))
        self.comboBox_8 = QComboBox(Dialog)
        self.comboBox_8.setObjectName(u"comboBox_8")
        self.comboBox_8.setGeometry(QRect(220, 250, 250, 23))
        self.comboBox_10 = QComboBox(Dialog)
        self.comboBox_10.setObjectName(u"comboBox_10")
        self.comboBox_10.setGeometry(QRect(220, 310, 250, 23))
        self.dateEdit_3 = QDateEdit(Dialog)
        self.dateEdit_3.setObjectName(u"dateEdit_3")
        self.dateEdit_3.setGeometry(QRect(220, 100, 250, 23))
        self.textEdit_1 = QTextEdit(Dialog)
        self.textEdit_1.setObjectName(u"textEdit_1")
        self.textEdit_1.setGeometry(QRect(220, 40, 250, 23))
        self.textEdit_9 = QTextEdit(Dialog)
        self.textEdit_9.setObjectName(u"textEdit_9")
        self.textEdit_9.setGeometry(QRect(220, 280, 250, 23))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Modifier un champ JSON", None))
        self.pushButtonModify.setText(QCoreApplication.translate("Dialog", u"Modifier", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("Dialog", u"Annuler", None))
        self.pushbuttonAddJsonField.setText(QCoreApplication.translate("Dialog", u"+", None))
        self.pushButtonRemoveJsonField.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.labelJsonField.setText(QCoreApplication.translate("Dialog", u"Champ JSON", None))
        self.labelField_1.setText(QCoreApplication.translate("Dialog", u"Champ_1", None))
        self.labelField_2.setText(QCoreApplication.translate("Dialog", u"Champ_2", None))
        self.labelField_3.setText(QCoreApplication.translate("Dialog", u"Champ_3", None))
        self.labelField_4.setText(QCoreApplication.translate("Dialog", u"Champ_4", None))
        self.labelField_5.setText(QCoreApplication.translate("Dialog", u"Champ_5", None))
        self.labelField_6.setText(QCoreApplication.translate("Dialog", u"Champ_6", None))
        self.labelField_7.setText(QCoreApplication.translate("Dialog", u"Champ_7", None))
        self.labelField_8.setText(QCoreApplication.translate("Dialog", u"Champ_8", None))
        self.labelField_9.setText(QCoreApplication.translate("Dialog", u"Champ_9", None))
        self.labelField_10.setText(QCoreApplication.translate("Dialog", u"Champ_10", None))
    # retranslateUi

