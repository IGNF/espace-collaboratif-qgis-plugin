# -*- coding: utf-8 -*-
import json
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QApplication, QComboBox, QDialog, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from .core.PluginLogger import PluginLogger
from .core.StatisticsCharts import (
    ContributionBreakdown, HBarChart,
    COLOR_INSERT, COLOR_UPDATE, COLOR_DELETE, COLOR_TX, COLOR_FAIL,
)
from .core.StatisticsData import StatisticsData, UNKNOWN_CLIENT_LABEL
from .core.StatisticsService import StatisticsService

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'FormStatistics_base.ui'))

NO_STATISTICS_MESSAGE = (
    u"Aucune donnée statistique à afficher\n"
    u"Aucune contribution ne correspond à la période et à l’utilisateur sélectionnés. "
    u"Élargissez la période ou choisissez « Tous les utilisateurs », puis cliquez sur Valider."
)

DIALOG_STYLE = """
QGroupBox {
    font-weight: 600;
    border: 1px solid #CFD8DC;
    border-radius: 8px;
    margin-top: 12px;
    padding: 10px 8px 8px 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #37474F;
}
QFrame#statisticsMetricCard, QFrame#contributionBreakdownCard, QFrame#clientCard {
    border: 1px solid #E3E6EB;
    border-radius: 8px;
    background: palette(base);
}
QFrame#headerBanner { background: #EFF6FF; border-radius: 8px; }
QLabel#headerTitle { color: #1A1A1A; font-size: 15px; font-weight: 600; }
QLabel#headerPeriod { color: #5B5B5B; font-size: 11px; }
QLabel#contributionBreakdownTitle, QLabel#clientTitle, QLabel#userTitle {
    color: #455A64; font-weight: 600;
}
"""


class FormStatistics(QDialog, FORM_CLASS):
    """
    Dialogue d'affichage des statistiques d'une base de données de l'espace collaboratif.

    La structure statique est décrite dans ``FormStatistics_base.ui`` ; l'accès
    réseau est délégué à :class:`StatisticsService` et la mise en forme des
    données à :class:`StatisticsData`.
    """

    def __init__(self, context, databaseid: int, databasename: str, parent=None) -> None:
        super(FormStatistics, self).__init__(parent)
        self.setupUi(self)
        self.__fullDialogSize = self.size()
        self.__fullDialogMinimumSize = self.minimumSize()

        self.__context = context
        self.__databaseid = databaseid
        self.__databasename = databasename
        self.__logger = PluginLogger("FormStatistics").getPluginLogger()
        self.__service = StatisticsService(context)
        self.__metricValueLabels = {}
        self.__isAdmin = context.isUserCommunityAdmin()
        self.__hasLoaded = False
        self.__defaultStart = None
        self.__defaultEnd = None

        self.setWindowTitle(u"Statistiques – {}".format(
            databasename if databasename else u"base {}".format(databaseid)))
        self.setStyleSheet(DIALOG_STYLE)

        self.__setupWidgets()
        self.__connectSignals()
        self.__loadStatistics()

 
    def __setupWidgets(self) -> None:
        self.headerTitle.setText(self.windowTitle())

        self.dateStart.setDate(QDate.currentDate().addMonths(-1))
        self.dateEnd.setDate(QDate.currentDate())
        self.dateStart.setEnabled(True)
        self.dateEnd.setEnabled(True)
        self.cbStart.hide()
        self.cbEnd.hide()
        self.labelUser.setText(u"Utilisateur")
        if self.__isAdmin:
            self.userCombo.addItem(u"Tous les utilisateurs", None)
        else:
            self.userCombo.addItem(
                self.__context.getUserNameCommunity() or u"Utilisateur connecté", None)
            self.userCombo.setEnabled(False)

        self.filtersLayout.removeItem(self.dateRow)
        self.filtersLayout.removeWidget(self.userRow)
        self.userRowLayout.takeAt(self.userRowLayout.count() - 1)
        self.userRowLayout.setDirection(QHBoxLayout.Direction.TopToBottom)
        self.filterFieldsRow = QFrame(self.groupFilters)
        self.filterFieldsLayout = QHBoxLayout(self.filterFieldsRow)
        self.filterFieldsLayout.setContentsMargins(0, 0, 0, 0)
        self.filterFieldsLayout.setSpacing(24)

        self.labelPeriod = QLabel(u"Période", self.filterFieldsRow)
        self.periodDefaultLabel = QLabel(self.filterFieldsRow)
        self.periodDefaultLabel.setStyleSheet("color: #5B5B5B; font-size: 10px;")
        self.periodDefaultLabel.setWordWrap(True)
        self.periodColumn = QVBoxLayout()
        self.periodColumn.setSpacing(6)
        self.periodColumn.addWidget(self.labelPeriod)
        self.periodColumn.addLayout(self.dateRow)
        self.periodColumn.addWidget(self.periodDefaultLabel)
        self.filterFieldsLayout.addLayout(self.periodColumn, 1)
        self.filterFieldsLayout.addWidget(self.userRow, 1)
        self.filtersLayout.insertWidget(0, self.filterFieldsRow)

        for key, caption, accent in (
            ("transactions", u"Transactions", COLOR_TX),
            ("contributions", u"Contributions", "#1E3E85"),
            ("failed_transactions", u"Échecs", COLOR_FAIL),
        ):
            self.statisticsMetricRow.layout().addWidget(
                self.__createStatisticsMetricCard(key, caption, accent), 1)

        self.__breakdown = ContributionBreakdown()
        self.contributionBreakdownContainer.layout().addWidget(self.__breakdown)
        self.__clientChart = HBarChart()
        self.clientContainer.layout().addWidget(self.__clientChart)
        self.clientNote = QLabel(
            u"Non identifié : contributions dont le client n'a pas pu être déterminé.",
            self.clientCard)
        self.clientNote.setWordWrap(True)
        self.clientNote.setStyleSheet("color: #5B5B5B; font-size: 10px; border: none;")
        self.clientCardLayout.insertWidget(2, self.clientNote)
        self.userChartContainer.hide()

        boldFont = QFont()
        boldFont.setBold(True)
        boldFont.setPointSize(11)
        self.labelTransTotal.setFont(boldFont)
        self.labelTransFailed.setFont(boldFont)
        self.labelTransFailed.setStyleSheet("color: {};".format(COLOR_FAIL))

        self.__initTable(self.tableByUser,
                 [u"Rang", u"Utilisateur", u"Contributions", u"Transactions",
                  u"Insertions", u"Modifications", u"Suppressions"])
        self.__initTable(self.tableTables, [u"Table"])
        self.groupByUser.setVisible(True)
        self.userTitle.hide()
        self.labelTotalCaption.hide()
        self.labelTransTotal.hide()
        self.labelFailedCaption.hide()
        self.labelTransFailed.hide()
        self.transLayout.removeItem(self.transRow)
        self.tableTables.setShowGrid(False)
        self.tableTables.horizontalHeader().hide()

        self.scrollLayout.removeWidget(self.groupByUser)
        self.scrollLayout.removeWidget(self.groupTrans)
        self.detailsRow = QFrame(self.scrollContent)
        self.detailsLayout = QHBoxLayout(self.detailsRow)
        self.detailsLayout.setContentsMargins(0, 0, 0, 0)
        self.detailsLayout.setSpacing(10)
        self.groupByUser.setParent(self.detailsRow)
        self.groupTrans.setParent(self.detailsRow)
        self.detailsLayout.addWidget(self.groupByUser, 7)
        self.detailsLayout.addWidget(self.groupTrans, 3)
        self.scrollLayout.insertWidget(2, self.detailsRow)

    def __connectSignals(self) -> None:
        self.btnRefresh.clicked.connect(self.__loadStatistics)
        self.btnReset.clicked.connect(self.__resetFilters)
        self.buttonBox.rejected.connect(self.reject)

    def __createStatisticsMetricCard(
            self, key: str, caption: str, accent: str) -> QFrame:
        """Crée une carte indicateur et conserve son libellé de valeur.

        :return: le cadre contenant la valeur, le titre et l'aide facultative.
        """
        card = QFrame()
        card.setObjectName("statisticsMetricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        value = QLabel(u"0")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        value.setFont(font)
        value.setStyleSheet("color: {}; border: none;".format(accent))

        caption_label = QLabel(caption)
        caption_label.setStyleSheet("color: #607D8B; border: none;")

        layout.addWidget(value)
        layout.addWidget(caption_label)
        descriptions = {
            "transactions": u"Opérations regroupées en une unité de travail.",
            "contributions": u"Insertions, modifications et suppressions.",
        }
        if key in descriptions:
            info_row = QHBoxLayout()
            info_row.setSpacing(5)
            info_icon = QLabel(u"i")
            info_icon.setFixedSize(14, 14)
            info_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_icon.setToolTip(descriptions[key])
            info_icon.setStyleSheet(
                "color: #5B5B5B; border: 1px solid #9AA3AF; border-radius: 7px;"
                "font-size: 9px; font-weight: bold;")
            info_text = QLabel(descriptions[key])
            info_text.setWordWrap(True)
            info_text.setStyleSheet("color: #5B5B5B; font-size: 10px; border: none;")
            info_row.addWidget(info_icon, 0, Qt.AlignmentFlag.AlignTop)
            info_row.addWidget(info_text, 1)
            layout.addLayout(info_row)
        self.__metricValueLabels[key] = value
        return card

    @staticmethod
    def __initTable(table: QTableWidget, headers: list) -> None:
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, len(headers)):
            table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)

   
    def __buildParams(self) -> dict:
        params = {}
        if self.__hasLoaded:
            params['startDate'] = self.dateStart.date().toString("yyyy-MM-dd")
            params['endDate'] = self.dateEnd.date().toString("yyyy-MM-dd")
        if self.__isAdmin and self.userCombo.currentData() is not None:
            params['user_id'] = str(self.userCombo.currentData())
        return params

    def __resetFilters(self) -> None:
        self.userCombo.setCurrentIndex(0)
        if self.__defaultStart is not None:
            self.dateStart.setDate(self.__defaultStart)
        if self.__defaultEnd is not None:
            self.dateEnd.setDate(self.__defaultEnd)
        self.__loadStatistics()

    def __loadStatistics(self) -> None:
        self.btnRefresh.setEnabled(False)
        self.statusLabel.setStyleSheet("")
        self.statusLabel.setText(u"Chargement en cours…")
        QApplication.processEvents()

        try:
            params = self.__buildParams()
            result = self.__service.getStatistics(self.__databaseid, params)
            if result.ok:
                payload = result.payload
                self.__printDebugContext(params, payload)
                if isinstance(payload.get('aggregate'), dict) and not self.__isAdmin:
                    self.__isAdmin = True
                    self.userCombo.setItemText(0, u"Tous les utilisateurs")
                    self.userCombo.setEnabled(True)
                data = StatisticsData.fromPayload(payload)
                if data.has_statistics:
                    self.setMinimumSize(self.__fullDialogMinimumSize)
                    self.resize(self.__fullDialogSize)
                    self.__fillData(data)
                    self.scrollArea.show()
                    self.statusLabel.setText(u"")
                else:
                    self.__fillPeriod(data)
                    self.__populateUsers(data)
                    self.scrollArea.hide()
                    self.statusLabel.setStyleSheet(
                        "color: #37474F; font-size: 14px; font-weight: 500; padding: 14px;")
                    self.statusLabel.setText(NO_STATISTICS_MESSAGE)
                    self.setMinimumSize(820, 0)
                    self.resize(1000, 480)
                self.__hasLoaded = True
            else:
                self.statusLabel.setStyleSheet("color: red;")
                code = result.status_code if result.status_code is not None else u"?"
                self.statusLabel.setText(
                    u"Erreur {} : {}".format(code, result.error[:300]))
        except Exception as e:
            self.__logger.error("FormStatistics.__loadStatistics : {}".format(e))
            self.statusLabel.setStyleSheet("color: red;")
            self.statusLabel.setText(u"Erreur de connexion : {}".format(str(e)))
        finally:
            self.btnRefresh.setEnabled(True)

    def __printDebugContext(self, params: dict, payload: dict) -> None:
        message = {
            'database_id': self.__databaseid,
            'database_name': self.__databasename,
            'params': params,
            'response_mode': 'aggregate' if isinstance(payload.get('aggregate'), dict) else 'user',
            'response_keys': sorted(payload.keys()),
            'api_debug': payload.get('debug', {}),
        }
        print("[STATISTICS DEBUG] {}".format(json.dumps(message, ensure_ascii=False, sort_keys=True)))

  
    def __fillData(self, data: StatisticsData) -> None:
        """Distribue les statistiques normalisées dans les vues du dialogue.

        Les trois cartes affichent les totaux de contributions, transactions et
        échecs. Le graphique de répartition reçoit les comptes par opération; les barres
        client reçoivent leurs nombres et signalent le client non identifié.
        Les utilisateurs et les tables sont affichés par leurs méthodes dédiées.
        """
        self.__fillPeriod(data)
        self.__populateUsers(data)

        self.__metricValueLabels['contributions'].setText(str(data.contrib_total))
        self.__metricValueLabels['transactions'].setText(str(data.tx_total))
        self.__metricValueLabels['failed_transactions'].setText(str(data.tx_failed))

        self.__breakdown.setSegments([
            (u"Insertions", data.inserts, COLOR_INSERT),
            (u"Modifications", data.updates, COLOR_UPDATE),
            (u"Suppressions", data.deletes, COLOR_DELETE),
        ])
        self.__clientChart.setBars([
            (label, count, "#5B7FD0", label == UNKNOWN_CLIENT_LABEL)
            for label, count in data.clients
        ])

        self.__fillTransactions(data)
        self.__fillByUser(data)

    def __populateUsers(self, data: StatisticsData) -> None:
        if not self.__isAdmin:
            return
        selected = self.userCombo.currentData()
        known_ids = {
            str(self.userCombo.itemData(index))
            for index in range(1, self.userCombo.count())
        }
        for entry in data.users:
            user_id = entry.get('user_id')
            if user_id is None or str(user_id) in known_ids:
                continue
            self.userCombo.addItem(entry['username'], user_id)
            known_ids.add(str(user_id))
        selected_index = self.userCombo.findData(selected)
        self.userCombo.setCurrentIndex(max(0, selected_index))

    def __fillPeriod(self, data: StatisticsData) -> None:
        self.headerPeriod.setText(
            u"Période effective : {} → {}".format(data.start, data.end))

        # Sans filtre explicite, la route renvoie la 1ère/dernière date de
        # transaction : on cale les sélecteurs dessus pour servir de base.
        startDate = QDate.fromString(data.start, "yyyy-MM-dd")
        endDate = QDate.fromString(data.end, "yyyy-MM-dd")
        if not self.__hasLoaded:
            if startDate.isValid():
                self.__defaultStart = startDate
                self.dateStart.setDate(startDate)
            if endDate.isValid():
                self.__defaultEnd = endDate
                self.dateEnd.setDate(endDate)
            start_text = self.__defaultStart.toString("dd/MM/yyyy") if self.__defaultStart else u"–"
            end_text = self.__defaultEnd.toString("dd/MM/yyyy") if self.__defaultEnd else u"–"
            self.periodDefaultLabel.setText(
                u"Période par défaut du {} au {}".format(start_text, end_text))

    def __fillTransactions(self, data: StatisticsData) -> None:
        self.labelTransTotal.setText(str(data.tx_total))
        self.labelTransFailed.setText(str(data.tx_failed))

        self.tableTables.clearSpans()
        self.tableTables.setRowCount(0)
        if not data.tables:
            self.tableTables.setRowCount(1)
            item = QTableWidgetItem(u"Aucune table modifiée")
            item.setForeground(QColor("#888888"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableTables.setItem(0, 0, item)
            return

        for table in data.tables:
            row = self.tableTables.rowCount()
            self.tableTables.insertRow(row)
            name = table if isinstance(table, str) else table.get('name', str(table))
            self.tableTables.setItem(row, 0, QTableWidgetItem(name))

    def __fillByUser(self, data: StatisticsData) -> None:
        self.tableByUser.clearSpans()
        self.tableByUser.setRowCount(0)

        if not data.users:
            self.tableByUser.setRowCount(1)
            item = QTableWidgetItem(u"Aucune donnée contributeur")
            item.setForeground(QColor("#888888"))
            self.tableByUser.setItem(0, 1, item)
            self.tableByUser.setSpan(0, 1, 1, self.tableByUser.columnCount() - 1)
            return

        self.groupByUser.setVisible(True)
        ranked_users = sorted(data.users, key=lambda entry: entry['total'], reverse=True)
        for rank, entry in enumerate(ranked_users, start=1):
            row = self.tableByUser.rowCount()
            self.tableByUser.insertRow(row)
            values = [rank, entry['username'], entry['total'], entry['tx_total'],
                      entry['inserts'], entry['updates'], entry['deletes']]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                alignment = Qt.AlignmentFlag.AlignVCenter
                alignment |= Qt.AlignmentFlag.AlignLeft if col == 1 else Qt.AlignmentFlag.AlignCenter
                item.setTextAlignment(alignment)
                self.tableByUser.setItem(row, col, item)
