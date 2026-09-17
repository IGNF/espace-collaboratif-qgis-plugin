# -*- coding: utf-8 -*-
import json
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QApplication, QDialog, QFrame, QHeaderView, QLabel, QTableWidget,
    QTableWidgetItem, QVBoxLayout,
)

from .core.PluginLogger import PluginLogger
from .core.StatisticsCharts import (
    DonutChart, HBarChart,
    COLOR_INSERT, COLOR_UPDATE, COLOR_DELETE, COLOR_TX, COLOR_FAIL, CLIENT_PALETTE,
)
from .core.StatisticsData import StatisticsData
from .core.StatisticsService import StatisticsService

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'FormStatistics_base.ui'))

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
QFrame#kpiCard, QFrame#donutCard, QFrame#clientCard {
    border: 1px solid #CFD8DC;
    border-radius: 8px;
    background: palette(base);
}
QFrame#headerBanner { background: #0D3B66; border-radius: 8px; }
QLabel#headerTitle { color: white; font-size: 15px; font-weight: 600; }
QLabel#headerPeriod { color: #BBDEFB; font-size: 11px; }
QLabel#donutTitle, QLabel#clientTitle, QLabel#userTitle {
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

        self.__context = context
        self.__databaseid = databaseid
        self.__databasename = databasename
        self.__logger = PluginLogger("FormStatistics").getPluginLogger()
        self.__service = StatisticsService(context)
        self.__kpi = {}

        self.setWindowTitle(u"Statistiques – {}".format(
            databasename if databasename else u"base {}".format(databaseid)))
        self.setStyleSheet(DIALOG_STYLE)

        self.__setupWidgets()
        self.__connectSignals()
        self.__loadStatistics()

    # ------------------------------------------------------------------
    # UI wiring
    # ------------------------------------------------------------------

    def __setupWidgets(self) -> None:
        self.headerTitle.setText(self.windowTitle())

        self.dateStart.setDate(QDate.currentDate().addMonths(-1))
        self.dateEnd.setDate(QDate.currentDate())
        self.userRow.setVisible(self.__context.isUserCommunityAdmin())

        for key, caption, accent in (
            ("contrib", u"Contributions", "#0D3B66"),
            ("insert", u"Insertions", COLOR_INSERT),
            ("update", u"Modifications", COLOR_UPDATE),
            ("delete", u"Suppressions", COLOR_DELETE),
            ("tx", u"Transactions", COLOR_TX),
            ("fail", u"Échecs", COLOR_FAIL),
        ):
            self.kpiRow.layout().addWidget(self.__makeKpiCard(key, caption, accent))

        self.__donut = DonutChart()
        self.donutContainer.layout().addWidget(self.__donut)
        self.__clientChart = HBarChart()
        self.clientContainer.layout().addWidget(self.__clientChart)
        self.__userChart = HBarChart()
        self.userChartContainer.layout().addWidget(self.__userChart)

        boldFont = QFont()
        boldFont.setBold(True)
        boldFont.setPointSize(11)
        self.labelTransTotal.setFont(boldFont)
        self.labelTransFailed.setFont(boldFont)
        self.labelTransFailed.setStyleSheet("color: {};".format(COLOR_FAIL))

        self.__initTable(self.tableByUser,
                         [u"Utilisateur", u"Insertions", u"Modifications",
                          u"Suppressions", u"Transactions"])
        self.__initTable(self.tableTables, [u"Table"])
        self.groupByUser.setVisible(False)

    def __connectSignals(self) -> None:
        self.cbStart.toggled.connect(self.dateStart.setEnabled)
        self.cbEnd.toggled.connect(self.dateEnd.setEnabled)
        self.btnRefresh.clicked.connect(self.__loadStatistics)
        self.buttonBox.rejected.connect(self.reject)

    def __makeKpiCard(self, key: str, caption: str, accent: str) -> QFrame:
        card = QFrame()
        card.setObjectName("kpiCard")
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
        self.__kpi[key] = value
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

    # ------------------------------------------------------------------
    # Networking
    # ------------------------------------------------------------------

    def __buildParams(self) -> dict:
        params = {}
        if self.cbStart.isChecked():
            params['startDate'] = self.dateStart.date().toString("yyyy-MM-dd")
        if self.cbEnd.isChecked():
            params['endDate'] = self.dateEnd.date().toString("yyyy-MM-dd")
        if self.userRow.isVisible():
            uid = self.userIdEdit.text().strip()
            if uid:
                params['user_id'] = uid
        return params

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
                # reveal user filter if the API confirms elevated access
                if isinstance(payload.get('aggregate'), dict):
                    self.userRow.setVisible(True)
                self.__fillData(StatisticsData.fromPayload(payload))
                self.statusLabel.setText(u"")
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

    # ------------------------------------------------------------------
    # Data display
    # ------------------------------------------------------------------

    def __fillData(self, data: StatisticsData) -> None:
        self.__fillPeriod(data)

        self.__kpi['contrib'].setText(str(data.contrib_total))
        self.__kpi['insert'].setText(str(data.inserts))
        self.__kpi['update'].setText(str(data.updates))
        self.__kpi['delete'].setText(str(data.deletes))
        self.__kpi['tx'].setText(str(data.tx_total))
        self.__kpi['fail'].setText(str(data.tx_failed))

        self.__donut.setSegments([
            (u"Insertions", data.inserts, COLOR_INSERT),
            (u"Modifications", data.updates, COLOR_UPDATE),
            (u"Suppressions", data.deletes, COLOR_DELETE),
        ])
        self.__clientChart.setBars([
            (label, count, CLIENT_PALETTE[index % len(CLIENT_PALETTE)])
            for index, (label, count) in enumerate(data.clients)
        ])

        self.__fillTransactions(data)
        self.__fillByUser(data)

    def __fillPeriod(self, data: StatisticsData) -> None:
        self.headerPeriod.setText(
            u"Période effective : {} → {}".format(data.start, data.end))

        # Sans filtre explicite, la route renvoie la 1ère/dernière date de
        # transaction : on cale les sélecteurs dessus pour servir de base.
        startDate = QDate.fromString(data.start, "yyyy-MM-dd")
        endDate = QDate.fromString(data.end, "yyyy-MM-dd")
        if startDate.isValid() and not self.cbStart.isChecked():
            self.dateStart.setMinimumDate(startDate)
            self.dateStart.setDate(startDate)
        if endDate.isValid() and not self.cbEnd.isChecked():
            self.dateEnd.setDate(endDate)

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
        self.tableByUser.setRowCount(0)

        if not data.users:
            self.groupByUser.setVisible(False)
            self.__userChart.setBars([])
            return

        self.groupByUser.setVisible(True)
        for entry in data.users:
            row = self.tableByUser.rowCount()
            self.tableByUser.insertRow(row)
            self.tableByUser.setItem(row, 0, QTableWidgetItem(entry['username']))
            values = [entry['inserts'], entry['updates'], entry['deletes'], entry['tx_total']]
            for col, val in enumerate(values, start=1):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.tableByUser.setItem(row, col, item)

        top = sorted(data.users, key=lambda entry: entry['total'], reverse=True)[:10]
        self.__userChart.setBars([
            (entry['username'], entry['total'], CLIENT_PALETTE[index % len(CLIENT_PALETTE)])
            for index, entry in enumerate(top)
        ])
