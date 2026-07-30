# -*- coding: utf-8 -*-
import requests
from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt.QtGui import QFont, QColor
from qgis.PyQt.QtWidgets import (
    QApplication, QCheckBox, QDateEdit, QDialog, QDialogButtonBox, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from .core.PluginLogger import PluginLogger

# Mapping raw API client identifiers → display labels
CLIENT_LABELS = {
    "SIG-QGIS": "QGIS Plugin",
    "WEB": "Interface Web",
    "API": "API directe",
    "MOBILE": "Application Mobile",
}


class FormStatistics(QDialog):
    """
    Dialogue d'affichage des statistiques d'une base de données de l'espace collaboratif.

    Permet de filtrer par période (dates de début/fin) et, si l'utilisateur
    est administrateur du groupe, de filtrer par identifiant utilisateur.
    """

    def __init__(self, context, databaseid: int, databasename: str, parent=None) -> None:
        super(FormStatistics, self).__init__(parent)
        self.__context = context
        self.__databaseid = databaseid
        self.__databasename = databasename
        self.__logger = PluginLogger("FormStatistics").getPluginLogger()
        self.__isAdmin = context.isUserCommunityAdmin()

        self.setWindowTitle(u"Statistiques – {}".format(databasename if databasename else "base {}".format(databaseid)))
        self.setMinimumWidth(580)
        self.setMinimumHeight(560)
        self.setSizeGripEnabled(True)

        self.__buildUi()
        self.__loadStatistics()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def __buildUi(self) -> None:
        main = QVBoxLayout(self)
        main.setSpacing(10)
        main.setContentsMargins(12, 12, 12, 12)

        main.addWidget(self.__buildFilterGroup())

        self.__periodLabel = QLabel(u"Période effective : –")
        self.__periodLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        font = QFont()
        font.setItalic(True)
        self.__periodLabel.setFont(font)
        main.addWidget(self.__periodLabel)

        main.addWidget(self.__buildContribGroup())
        main.addWidget(self.__buildTransGroup())

        self.__statusLabel = QLabel(u"")
        self.__statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__statusLabel.setWordWrap(True)
        main.addWidget(self.__statusLabel)

        btnBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btnBox.rejected.connect(self.reject)
        main.addWidget(btnBox)

    def __buildFilterGroup(self) -> QGroupBox:
        group = QGroupBox(u"Filtres")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Date row
        dateRow = QHBoxLayout()

        dateRow.addWidget(QLabel(u"Du :"))
        self.__dateStart = QDateEdit()
        self.__dateStart.setDisplayFormat("dd/MM/yyyy")
        self.__dateStart.setCalendarPopup(True)
        self.__dateStart.setDate(QDate.currentDate().addMonths(-1))
        self.__dateStart.setMinimumDate(QDate(2000, 1, 1))
        self.__dateStart.setEnabled(False)
        dateRow.addWidget(self.__dateStart)

        self.__cbStart = QCheckBox(u"Activer")
        self.__cbStart.setChecked(False)
        self.__cbStart.toggled.connect(self.__dateStart.setEnabled)
        dateRow.addWidget(self.__cbStart)

        dateRow.addSpacing(24)

        dateRow.addWidget(QLabel(u"Au :"))
        self.__dateEnd = QDateEdit()
        self.__dateEnd.setDisplayFormat("dd/MM/yyyy")
        self.__dateEnd.setCalendarPopup(True)
        self.__dateEnd.setDate(QDate.currentDate())
        self.__dateEnd.setMinimumDate(QDate(2000, 1, 1))
        self.__dateEnd.setEnabled(False)
        dateRow.addWidget(self.__dateEnd)

        self.__cbEnd = QCheckBox(u"Activer")
        self.__cbEnd.setChecked(False)
        self.__cbEnd.toggled.connect(self.__dateEnd.setEnabled)
        dateRow.addWidget(self.__cbEnd)

        dateRow.addStretch()
        layout.addLayout(dateRow)

        # User ID row (admin only)
        self.__userRow = QWidget()
        userLayout = QHBoxLayout(self.__userRow)
        userLayout.setContentsMargins(0, 0, 0, 0)
        userLayout.addWidget(QLabel(u"Filtrer par utilisateur (id) :"))
        self.__userIdEdit = QLineEdit()
        self.__userIdEdit.setPlaceholderText(u"Laisser vide pour tous les utilisateurs")
        self.__userIdEdit.setMaximumWidth(220)
        userLayout.addWidget(self.__userIdEdit)
        userLayout.addStretch()
        layout.addWidget(self.__userRow)
        self.__userRow.setVisible(self.__isAdmin)

        # Refresh button
        btnRow = QHBoxLayout()
        btnRow.addStretch()
        self.__btnRefresh = QPushButton(u"Rafraîchir")
        self.__btnRefresh.setFixedWidth(120)
        self.__btnRefresh.clicked.connect(self.__loadStatistics)
        btnRow.addWidget(self.__btnRefresh)
        layout.addLayout(btnRow)

        return group

    def __buildContribGroup(self) -> QGroupBox:
        group = QGroupBox(u"Contributions par client")
        layout = QVBoxLayout(group)
        self.__contribTable = QTableWidget(0, 2)
        self.__contribTable.setHorizontalHeaderLabels([u"Client", u"Contributions"])
        self.__contribTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.__contribTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.__contribTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__contribTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.__contribTable.setAlternatingRowColors(True)
        self.__contribTable.verticalHeader().setVisible(False)
        self.__contribTable.setMinimumHeight(110)
        self.__contribTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.__contribTable)
        return group

    def __buildTransGroup(self) -> QGroupBox:
        group = QGroupBox(u"Transactions")
        layout = QVBoxLayout(group)

        totalRow = QHBoxLayout()
        totalRow.addWidget(QLabel(u"Total de transactions :"))
        self.__transTotal = QLabel(u"0")
        boldFont = QFont()
        boldFont.setBold(True)
        boldFont.setPointSize(11)
        self.__transTotal.setFont(boldFont)
        totalRow.addWidget(self.__transTotal)
        totalRow.addStretch()
        layout.addLayout(totalRow)

        layout.addWidget(QLabel(u"Tables modifiées :"))
        self.__tablesTable = QTableWidget(0, 1)
        self.__tablesTable.setHorizontalHeaderLabels([u"Table"])
        self.__tablesTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.__tablesTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__tablesTable.setAlternatingRowColors(True)
        self.__tablesTable.verticalHeader().setVisible(False)
        self.__tablesTable.setMinimumHeight(80)
        self.__tablesTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.__tablesTable)
        return group


    def __buildParams(self) -> dict:
        params = {}
        if self.__cbStart.isChecked():
            params['startDate'] = self.__dateStart.date().toString("yyyy-MM-dd")
        if self.__cbEnd.isChecked():
            params['endDate'] = self.__dateEnd.date().toString("yyyy-MM-dd")
        if self.__isAdmin:
            uid = self.__userIdEdit.text().strip()
            if uid:
                params['user_id'] = uid
        return params

    def __loadStatistics(self) -> None:
        self.__btnRefresh.setEnabled(False)
        self.__statusLabel.setStyleSheet("")
        self.__statusLabel.setText(u"Chargement en cours…")
        QApplication.processEvents()

        try:
            url = "{}/gcms/api/databases/{}/statistic".format(
                self.__context.urlHostEspaceCo, self.__databaseid)
            headers = {
                'Authorization': '{} {}'.format(
                    self.__context.getTokenType(), self.__context.getTokenAccess())
            }
            ssl_verify = "localhost.ign.fr" not in url
            response = requests.get(
                url,
                headers=headers,
                proxies=self.__context.getProxies(),
                params=self.__buildParams(),
                verify=ssl_verify,
                timeout=30,
            )
            response.encoding = 'utf-8'

            if response.status_code == 200:
                self.__fillData(response.json())
                self.__statusLabel.setText(u"")
            else:
                self.__statusLabel.setStyleSheet("color: red;")
                self.__statusLabel.setText(
                    u"Erreur {} : {}".format(response.status_code, response.text[:300]))
        except Exception as e:
            self.__logger.error("FormStatistics.__loadStatistics : {}".format(e))
            self.__statusLabel.setStyleSheet("color: red;")
            self.__statusLabel.setText(u"Erreur de connexion : {}".format(str(e)))
        finally:
            self.__btnRefresh.setEnabled(True)

    # ------------------------------------------------------------------
    # Data display
    # ------------------------------------------------------------------

    def __fillData(self, data: dict) -> None:
        self.__fillPeriod(data.get('period', {}))
        # Group-admin response wraps results under 'aggregate'; regular users expose them at top level
        if 'aggregate' in data:
            agg = data['aggregate']
            self.__fillContributions(agg.get('contributions', {}).get('by_client', {}))
            self.__fillTransactions(agg.get('transactions', {}))
        else:
            self.__fillContributions(data.get('contributions', {}).get('by_client', {}))
            self.__fillTransactions(data.get('transactions', {}))

    def __fillPeriod(self, period: dict) -> None:
        start = period.get('start') or u"–"
        end = period.get('end') or u"–"
        self.__periodLabel.setText(u"Période effective : {} → {}".format(start, end))

    def __fillContributions(self, by_client: dict) -> None:
        self.__contribTable.clearSpans()
        self.__contribTable.setRowCount(0)

        # API returns {clientName: {Insert: N, Update: N, Delete: N}}
        if not by_client:
            self.__contribTable.setRowCount(1)
            item = QTableWidgetItem(u"Aucune contribution sur cette période")
            item.setForeground(QColor("#888888"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__contribTable.setItem(0, 0, item)
            self.__contribTable.setSpan(0, 0, 1, 2)
            return

        for client_name, counts in by_client.items():
            row = self.__contribTable.rowCount()
            self.__contribTable.insertRow(row)

            label = CLIENT_LABELS.get(client_name, client_name)
            total = counts.get('Insert', 0) + counts.get('Update', 0) + counts.get('Delete', 0)

            client_item = QTableWidgetItem(label)
            self.__contribTable.setItem(row, 0, client_item)

            count_item = QTableWidgetItem(str(total))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.__contribTable.setItem(row, 1, count_item)

    def __fillTransactions(self, transactions: dict) -> None:
        self.__transTotal.setText(str(transactions.get('total', 0)))

        touched = transactions.get('touched_tables', [])
        self.__tablesTable.clearSpans()
        self.__tablesTable.setRowCount(0)

        if not touched:
            self.__tablesTable.setRowCount(1)
            item = QTableWidgetItem(u"Aucune table modifiée")
            item.setForeground(QColor("#888888"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__tablesTable.setItem(0, 0, item)
            return

        for table in touched:
            row = self.__tablesTable.rowCount()
            self.__tablesTable.insertRow(row)
            name = table if isinstance(table, str) else table.get('name', str(table))
            self.__tablesTable.setItem(row, 0, QTableWidgetItem(name))
