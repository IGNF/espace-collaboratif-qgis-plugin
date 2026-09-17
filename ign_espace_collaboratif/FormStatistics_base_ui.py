# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormStatistics_base.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDateEdit,
    QDialog, QDialogButtonBox, QFrame, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_StatisticsDialog(object):
    def setupUi(self, StatisticsDialog):
        if not StatisticsDialog.objectName():
            StatisticsDialog.setObjectName(u"StatisticsDialog")
        StatisticsDialog.resize(960, 860)
        StatisticsDialog.setMinimumSize(QSize(820, 760))
        StatisticsDialog.setSizeGripEnabled(True)
        self.verticalLayoutMain = QVBoxLayout(StatisticsDialog)
        self.verticalLayoutMain.setSpacing(10)
        self.verticalLayoutMain.setObjectName(u"verticalLayoutMain")
        self.headerBanner = QFrame(StatisticsDialog)
        self.headerBanner.setObjectName(u"headerBanner")
        self.headerLayout = QVBoxLayout(self.headerBanner)
        self.headerLayout.setSpacing(2)
        self.headerLayout.setObjectName(u"headerLayout")
        self.headerLayout.setContentsMargins(14, 10, 14, 10)
        self.headerTitle = QLabel(self.headerBanner)
        self.headerTitle.setObjectName(u"headerTitle")

        self.headerLayout.addWidget(self.headerTitle)

        self.headerPeriod = QLabel(self.headerBanner)
        self.headerPeriod.setObjectName(u"headerPeriod")

        self.headerLayout.addWidget(self.headerPeriod)


        self.verticalLayoutMain.addWidget(self.headerBanner)

        self.groupFilters = QGroupBox(StatisticsDialog)
        self.groupFilters.setObjectName(u"groupFilters")
        self.filtersLayout = QVBoxLayout(self.groupFilters)
        self.filtersLayout.setSpacing(8)
        self.filtersLayout.setObjectName(u"filtersLayout")
        self.dateRow = QHBoxLayout()
        self.dateRow.setObjectName(u"dateRow")
        self.labelFrom = QLabel(self.groupFilters)
        self.labelFrom.setObjectName(u"labelFrom")

        self.dateRow.addWidget(self.labelFrom)

        self.dateStart = QDateEdit(self.groupFilters)
        self.dateStart.setObjectName(u"dateStart")
        self.dateStart.setEnabled(False)
        self.dateStart.setCalendarPopup(True)

        self.dateRow.addWidget(self.dateStart)

        self.cbStart = QCheckBox(self.groupFilters)
        self.cbStart.setObjectName(u"cbStart")

        self.dateRow.addWidget(self.cbStart)

        self.dateSpacer = QSpacerItem(24, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.dateRow.addItem(self.dateSpacer)

        self.labelTo = QLabel(self.groupFilters)
        self.labelTo.setObjectName(u"labelTo")

        self.dateRow.addWidget(self.labelTo)

        self.dateEnd = QDateEdit(self.groupFilters)
        self.dateEnd.setObjectName(u"dateEnd")
        self.dateEnd.setEnabled(False)
        self.dateEnd.setCalendarPopup(True)

        self.dateRow.addWidget(self.dateEnd)

        self.cbEnd = QCheckBox(self.groupFilters)
        self.cbEnd.setObjectName(u"cbEnd")

        self.dateRow.addWidget(self.cbEnd)

        self.dateStretch = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.dateRow.addItem(self.dateStretch)


        self.filtersLayout.addLayout(self.dateRow)

        self.userRow = QWidget(self.groupFilters)
        self.userRow.setObjectName(u"userRow")
        self.userRowLayout = QHBoxLayout(self.userRow)
        self.userRowLayout.setObjectName(u"userRowLayout")
        self.userRowLayout.setContentsMargins(0, 0, 0, 0)
        self.labelUser = QLabel(self.userRow)
        self.labelUser.setObjectName(u"labelUser")

        self.userRowLayout.addWidget(self.labelUser)

        self.userIdEdit = QLineEdit(self.userRow)
        self.userIdEdit.setObjectName(u"userIdEdit")
        self.userIdEdit.setMaximumSize(QSize(220, 16777215))

        self.userRowLayout.addWidget(self.userIdEdit)

        self.userStretch = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.userRowLayout.addItem(self.userStretch)


        self.filtersLayout.addWidget(self.userRow)

        self.btnRow = QHBoxLayout()
        self.btnRow.setObjectName(u"btnRow")
        self.btnStretch = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.btnRow.addItem(self.btnStretch)

        self.btnRefresh = QPushButton(self.groupFilters)
        self.btnRefresh.setObjectName(u"btnRefresh")
        self.btnRefresh.setMinimumSize(QSize(120, 0))

        self.btnRow.addWidget(self.btnRefresh)


        self.filtersLayout.addLayout(self.btnRow)


        self.verticalLayoutMain.addWidget(self.groupFilters)

        self.scrollArea = QScrollArea(StatisticsDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollContent = QWidget()
        self.scrollContent.setObjectName(u"scrollContent")
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setSpacing(10)
        self.scrollLayout.setObjectName(u"scrollLayout")
        self.scrollLayout.setContentsMargins(0, 0, 6, 0)
        self.kpiRow = QWidget(self.scrollContent)
        self.kpiRow.setObjectName(u"kpiRow")
        self.kpiLayout = QHBoxLayout(self.kpiRow)
        self.kpiLayout.setSpacing(8)
        self.kpiLayout.setObjectName(u"kpiLayout")
        self.kpiLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollLayout.addWidget(self.kpiRow)

        self.chartsRow = QHBoxLayout()
        self.chartsRow.setSpacing(10)
        self.chartsRow.setObjectName(u"chartsRow")
        self.donutCard = QFrame(self.scrollContent)
        self.donutCard.setObjectName(u"donutCard")
        self.donutCardLayout = QVBoxLayout(self.donutCard)
        self.donutCardLayout.setObjectName(u"donutCardLayout")
        self.donutCardLayout.setContentsMargins(12, 10, 12, 10)
        self.donutTitle = QLabel(self.donutCard)
        self.donutTitle.setObjectName(u"donutTitle")

        self.donutCardLayout.addWidget(self.donutTitle)

        self.donutContainer = QWidget(self.donutCard)
        self.donutContainer.setObjectName(u"donutContainer")
        self.donutContainerLayout = QVBoxLayout(self.donutContainer)
        self.donutContainerLayout.setObjectName(u"donutContainerLayout")
        self.donutContainerLayout.setContentsMargins(0, 0, 0, 0)

        self.donutCardLayout.addWidget(self.donutContainer)


        self.chartsRow.addWidget(self.donutCard)

        self.clientCard = QFrame(self.scrollContent)
        self.clientCard.setObjectName(u"clientCard")
        self.clientCardLayout = QVBoxLayout(self.clientCard)
        self.clientCardLayout.setObjectName(u"clientCardLayout")
        self.clientCardLayout.setContentsMargins(12, 10, 12, 10)
        self.clientTitle = QLabel(self.clientCard)
        self.clientTitle.setObjectName(u"clientTitle")

        self.clientCardLayout.addWidget(self.clientTitle)

        self.clientContainer = QWidget(self.clientCard)
        self.clientContainer.setObjectName(u"clientContainer")
        self.clientContainerLayout = QVBoxLayout(self.clientContainer)
        self.clientContainerLayout.setObjectName(u"clientContainerLayout")
        self.clientContainerLayout.setContentsMargins(0, 0, 0, 0)

        self.clientCardLayout.addWidget(self.clientContainer)

        self.clientSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.clientCardLayout.addItem(self.clientSpacer)


        self.chartsRow.addWidget(self.clientCard)


        self.scrollLayout.addLayout(self.chartsRow)

        self.groupByUser = QGroupBox(self.scrollContent)
        self.groupByUser.setObjectName(u"groupByUser")
        self.byUserLayout = QVBoxLayout(self.groupByUser)
        self.byUserLayout.setObjectName(u"byUserLayout")
        self.userTitle = QLabel(self.groupByUser)
        self.userTitle.setObjectName(u"userTitle")

        self.byUserLayout.addWidget(self.userTitle)

        self.userChartContainer = QWidget(self.groupByUser)
        self.userChartContainer.setObjectName(u"userChartContainer")
        self.userChartLayout = QVBoxLayout(self.userChartContainer)
        self.userChartLayout.setObjectName(u"userChartLayout")
        self.userChartLayout.setContentsMargins(0, 0, 0, 0)

        self.byUserLayout.addWidget(self.userChartContainer)

        self.tableByUser = QTableWidget(self.groupByUser)
        self.tableByUser.setObjectName(u"tableByUser")
        self.tableByUser.setMinimumSize(QSize(0, 100))

        self.byUserLayout.addWidget(self.tableByUser)


        self.scrollLayout.addWidget(self.groupByUser)

        self.groupTrans = QGroupBox(self.scrollContent)
        self.groupTrans.setObjectName(u"groupTrans")
        self.transLayout = QVBoxLayout(self.groupTrans)
        self.transLayout.setObjectName(u"transLayout")
        self.transRow = QHBoxLayout()
        self.transRow.setObjectName(u"transRow")
        self.labelTotalCaption = QLabel(self.groupTrans)
        self.labelTotalCaption.setObjectName(u"labelTotalCaption")

        self.transRow.addWidget(self.labelTotalCaption)

        self.labelTransTotal = QLabel(self.groupTrans)
        self.labelTransTotal.setObjectName(u"labelTransTotal")

        self.transRow.addWidget(self.labelTransTotal)

        self.transSpacer = QSpacerItem(24, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.transRow.addItem(self.transSpacer)

        self.labelFailedCaption = QLabel(self.groupTrans)
        self.labelFailedCaption.setObjectName(u"labelFailedCaption")

        self.transRow.addWidget(self.labelFailedCaption)

        self.labelTransFailed = QLabel(self.groupTrans)
        self.labelTransFailed.setObjectName(u"labelTransFailed")

        self.transRow.addWidget(self.labelTransFailed)

        self.transStretch = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.transRow.addItem(self.transStretch)


        self.transLayout.addLayout(self.transRow)

        self.labelTablesCaption = QLabel(self.groupTrans)
        self.labelTablesCaption.setObjectName(u"labelTablesCaption")

        self.transLayout.addWidget(self.labelTablesCaption)

        self.tableTables = QTableWidget(self.groupTrans)
        self.tableTables.setObjectName(u"tableTables")
        self.tableTables.setMinimumSize(QSize(0, 80))

        self.transLayout.addWidget(self.tableTables)


        self.scrollLayout.addWidget(self.groupTrans)

        self.bottomSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.scrollLayout.addItem(self.bottomSpacer)

        self.scrollArea.setWidget(self.scrollContent)

        self.verticalLayoutMain.addWidget(self.scrollArea)

        self.statusLabel = QLabel(StatisticsDialog)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setWordWrap(True)

        self.verticalLayoutMain.addWidget(self.statusLabel)

        self.buttonBox = QDialogButtonBox(StatisticsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayoutMain.addWidget(self.buttonBox)


        self.retranslateUi(StatisticsDialog)

        QMetaObject.connectSlotsByName(StatisticsDialog)
    # setupUi

    def retranslateUi(self, StatisticsDialog):
        StatisticsDialog.setWindowTitle(QCoreApplication.translate("StatisticsDialog", u"Statistiques", None))
        self.headerTitle.setText(QCoreApplication.translate("StatisticsDialog", u"Statistiques", None))
        self.headerPeriod.setText(QCoreApplication.translate("StatisticsDialog", u"P\u00e9riode effective : \u2013", None))
        self.groupFilters.setTitle(QCoreApplication.translate("StatisticsDialog", u"Filtres", None))
        self.labelFrom.setText(QCoreApplication.translate("StatisticsDialog", u"Du :", None))
        self.dateStart.setDisplayFormat(QCoreApplication.translate("StatisticsDialog", u"dd/MM/yyyy", None))
        self.cbStart.setText(QCoreApplication.translate("StatisticsDialog", u"Activer", None))
        self.labelTo.setText(QCoreApplication.translate("StatisticsDialog", u"Au :", None))
        self.dateEnd.setDisplayFormat(QCoreApplication.translate("StatisticsDialog", u"dd/MM/yyyy", None))
        self.cbEnd.setText(QCoreApplication.translate("StatisticsDialog", u"Activer", None))
        self.labelUser.setText(QCoreApplication.translate("StatisticsDialog", u"Filtrer par utilisateur (id) \u2014 gestionnaire de groupe uniquement :", None))
        self.userIdEdit.setPlaceholderText(QCoreApplication.translate("StatisticsDialog", u"Laisser vide pour tous les membres du groupe", None))
        self.btnRefresh.setText(QCoreApplication.translate("StatisticsDialog", u"Rafra\u00eechir", None))
        self.donutTitle.setText(QCoreApplication.translate("StatisticsDialog", u"R\u00e9partition des contributions", None))
        self.clientTitle.setText(QCoreApplication.translate("StatisticsDialog", u"Contributions par client", None))
        self.groupByUser.setTitle(QCoreApplication.translate("StatisticsDialog", u"D\u00e9tail par utilisateur", None))
        self.userTitle.setText(QCoreApplication.translate("StatisticsDialog", u"Top contributeurs", None))
        self.groupTrans.setTitle(QCoreApplication.translate("StatisticsDialog", u"Transactions", None))
        self.labelTotalCaption.setText(QCoreApplication.translate("StatisticsDialog", u"Total :", None))
        self.labelTransTotal.setText(QCoreApplication.translate("StatisticsDialog", u"0", None))
        self.labelFailedCaption.setText(QCoreApplication.translate("StatisticsDialog", u"\u00c9checs :", None))
        self.labelTransFailed.setText(QCoreApplication.translate("StatisticsDialog", u"0", None))
        self.labelTablesCaption.setText(QCoreApplication.translate("StatisticsDialog", u"Tables modifi\u00e9es :", None))
        self.statusLabel.setText("")
    # retranslateUi

