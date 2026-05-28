# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormCreateReport_base.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from .qt_compat import (
    QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,
    QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform,
    QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGroupBox, QHeaderView,
    QLabel, QRadioButton, QSizePolicy, QTabWidget,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QWidget,
)

class Ui_dlgCreateRem(object):
    def setupUi(self, dlgCreateRem):
        if not dlgCreateRem.objectName():
            dlgCreateRem.setObjectName(u"dlgCreateRem")
        dlgCreateRem.resize(432, 639)
        font = QFont()
        font.setPointSize(7)
        dlgCreateRem.setFont(font)
        icon = QIcon()
        icon.addFile(u":/plugins/RipartPlugin/images/ign.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        dlgCreateRem.setWindowIcon(icon)
        dlgCreateRem.setToolTipDuration(-4)
        dlgCreateRem.setStyleSheet(u"QDialog {background-color: rgb(255, 255, 255)}")
        self.groupBoxProfil = QGroupBox(dlgCreateRem)
        self.groupBoxProfil.setObjectName(u"groupBoxProfil")
        self.groupBoxProfil.setGeometry(QRect(10, 20, 411, 581))
        font1 = QFont()
        font1.setPointSize(7)
        font1.setBold(False)
        self.groupBoxProfil.setFont(font1)
        self.tabWidget = QTabWidget(self.groupBoxProfil)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 130, 391, 241))
        font2 = QFont()
        font2.setPointSize(8)
        self.tabWidget.setFont(font2)
        self.tabTheme = QWidget()
        self.tabTheme.setObjectName(u"tabTheme")
        self.treeWidget = QTreeWidget(self.tabTheme)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setGeometry(QRect(0, 0, 391, 211))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setItemsExpandable(True)
        self.tabWidget.addTab(self.tabTheme, "")
        self.tabOption = QWidget()
        self.tabOption.setObjectName(u"tabOption")
        self.checkBoxJoinCroquis = QCheckBox(self.tabOption)
        self.checkBoxJoinCroquis.setObjectName(u"checkBoxJoinCroquis")
        self.checkBoxJoinCroquis.setGeometry(QRect(10, 10, 141, 20))
        self.checkBoxJoinCroquis.setChecked(True)
        self.checkBoxAttDoc = QCheckBox(self.tabOption)
        self.checkBoxAttDoc.setObjectName(u"checkBoxAttDoc")
        self.checkBoxAttDoc.setGeometry(QRect(10, 30, 251, 20))
        self.lblDoc = QLabel(self.tabOption)
        self.lblDoc.setObjectName(u"lblDoc")
        self.lblDoc.setGeometry(QRect(10, 60, 371, 71))
        self.lblDoc.setWordWrap(True)
        self.radioBtnUnique = QRadioButton(self.tabOption)
        self.radioBtnUnique.setObjectName(u"radioBtnUnique")
        self.radioBtnUnique.setGeometry(QRect(10, 140, 201, 20))
        self.radioBtnUnique.setChecked(True)
        self.radioBtnMultiple = QRadioButton(self.tabOption)
        self.radioBtnMultiple.setObjectName(u"radioBtnMultiple")
        self.radioBtnMultiple.setGeometry(QRect(10, 170, 161, 20))
        self.tabWidget.addTab(self.tabOption, "")
        self.textEditMessage = QTextEdit(self.groupBoxProfil)
        self.textEditMessage.setObjectName(u"textEditMessage")
        self.textEditMessage.setGeometry(QRect(10, 400, 391, 81))
        font3 = QFont()
        font3.setPointSize(8)
        font3.setBold(False)
        font3.setItalic(False)
        self.textEditMessage.setFont(font3)
        self.lblMessage = QLabel(self.groupBoxProfil)
        self.lblMessage.setObjectName(u"lblMessage")
        self.lblMessage.setGeometry(QRect(10, 380, 111, 16))
        font4 = QFont()
        font4.setPointSize(9)
        font4.setBold(True)
        self.lblMessage.setFont(font4)
        self.label = QLabel(self.groupBoxProfil)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 100, 191, 21))
        self.label.setFont(font4)
        self.lblMessageError = QLabel(self.groupBoxProfil)
        self.lblMessageError.setObjectName(u"lblMessageError")
        self.lblMessageError.setGeometry(QRect(10, 480, 391, 101))
        self.label_2 = QLabel(self.groupBoxProfil)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 40, 61, 21))
        self.label_2.setFont(font4)
        self.comboBoxGroupe = QComboBox(self.groupBoxProfil)
        self.comboBoxGroupe.setObjectName(u"comboBoxGroupe")
        self.comboBoxGroupe.setGeometry(QRect(10, 70, 251, 21))
        self.buttonBox = QDialogButtonBox(dlgCreateRem)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(170, 610, 101, 23))
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

        self.retranslateUi(dlgCreateRem)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(dlgCreateRem)
    # setupUi

    def retranslateUi(self, dlgCreateRem):
        dlgCreateRem.setWindowTitle(QCoreApplication.translate("dlgCreateRem", u"Cr\u00e9er un nouveau signalement", None))
        self.groupBoxProfil.setTitle("")
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("dlgCreateRem", u"attribut", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("dlgCreateRem", u"th\u00e8me", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTheme), QCoreApplication.translate("dlgCreateRem", u"Th\u00e8mes", None))
        self.checkBoxJoinCroquis.setText(QCoreApplication.translate("dlgCreateRem", u"Joindre un croquis", None))
        self.checkBoxAttDoc.setText(QCoreApplication.translate("dlgCreateRem", u"Joindre un document (4 au maximum)", None))
        self.lblDoc.setText("")
        self.radioBtnUnique.setText(QCoreApplication.translate("dlgCreateRem", u"Cr\u00e9er un signalement unique", None))
        self.radioBtnMultiple.setText(QCoreApplication.translate("dlgCreateRem", u"Cr\u00e9er xx signalements", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabOption), QCoreApplication.translate("dlgCreateRem", u"Options", None))
        self.lblMessage.setText(QCoreApplication.translate("dlgCreateRem", u"Commentaire", None))
        self.label.setText(QCoreApplication.translate("dlgCreateRem", u"Nouveau signalement", None))
        self.lblMessageError.setText("")
        self.label_2.setText(QCoreApplication.translate("dlgCreateRem", u"Groupe", None))
    # retranslateUi

