# -*- coding: utf-8 -*-
import json
import requests
from qgis.PyQt.QtCore import Qt, QDate, QRectF
from qgis.PyQt.QtGui import QFont, QColor, QPainter, QPalette
from qgis.PyQt.QtWidgets import (
    QApplication, QCheckBox, QDateEdit, QDialog, QDialogButtonBox, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)
from .core.PluginLogger import PluginLogger

# Mapping raw API client identifiers → display labels
CLIENT_LABELS = {
    "SIG-QGIS": "QGIS Plugin",
    "WEB": "Interface Web",
    "API": "API directe",
    "MOBILE": "Application Mobile",
}

# Palette used across cards and charts.
COLOR_INSERT = "#2E7D32"   # vert  – insertions
COLOR_UPDATE = "#1565C0"   # bleu  – modifications
COLOR_DELETE = "#C62828"   # rouge – suppressions
COLOR_TX = "#00838F"       # cyan  – transactions
COLOR_FAIL = "#EF6C00"     # orange – échecs
CLIENT_PALETTE = [
    "#1565C0", "#00838F", "#2E7D32", "#F9A825",
    "#6A1B9A", "#AD1457", "#4E342E", "#546E7A",
]
EMPTY_COLOR = "#9E9E9E"


class _DonutChart(QWidget):
    """Anneau (donut) proportionnel dessiné avec QPainter, avec légende."""

    def __init__(self, parent=None) -> None:
        super(_DonutChart, self).__init__(parent)
        self.__segments = []  # list of (label, value, QColor)
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def setSegments(self, segments) -> None:
        self.__segments = [(str(lbl), max(0.0, float(val)), QColor(col))
                           for lbl, val, col in segments]
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        total = sum(val for _, val, _ in self.__segments)
        height = self.height()
        width = self.width()
        diameter = max(min(height - 16, width * 0.5), 10.0)
        cx = 10.0 + diameter / 2.0
        cy = height / 2.0
        outer = QRectF(cx - diameter / 2.0, cy - diameter / 2.0, diameter, diameter)
        ring = diameter * 0.24

        if total <= 0:
            painter.setPen(QColor(EMPTY_COLOR))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(outer)
            painter.drawText(outer, Qt.AlignmentFlag.AlignCenter, u"Aucune donnée")
            return

        # Filled pie slices, then a hole to make it a donut.
        start = 90 * 16
        painter.setPen(Qt.PenStyle.NoPen)
        for _, value, color in self.__segments:
            if value <= 0:
                continue
            span = -int(round(360 * 16 * value / total))
            painter.setBrush(color)
            painter.drawPie(outer, start, span)
            start += span

        hole = QRectF(outer.left() + ring, outer.top() + ring,
                      outer.width() - 2 * ring, outer.height() - 2 * ring)
        painter.setBrush(self.palette().color(QPalette.ColorRole.Base))
        painter.drawEllipse(hole)

        # Grand total in the centre.
        painter.setPen(QColor("#263238"))
        bold = QFont(self.font())
        bold.setBold(True)
        bold.setPointSize(bold.pointSize() + 3)
        painter.setFont(bold)
        painter.drawText(hole, Qt.AlignmentFlag.AlignCenter, str(int(total)))

        # Legend on the right.
        painter.setFont(self.font())
        legend_x = cx + diameter / 2.0 + 18
        swatch = 11
        line_h = 22
        legend_h = line_h * len(self.__segments)
        y = cy - legend_h / 2.0
        for label, value, color in self.__segments:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(legend_x, y + 3, swatch, swatch), 2, 2)
            pct = 100.0 * value / total
            painter.setPen(QColor("#37474F"))
            painter.drawText(
                QRectF(legend_x + swatch + 8, y, width - legend_x - swatch - 12, line_h),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                u"{}  {}  ({:.0f}%)".format(label, int(value), pct),
            )
            y += line_h


class _HBarChart(QWidget):
    """Barres horizontales dessinées avec QPainter (label · barre · valeur)."""

    ROW_H = 30

    def __init__(self, parent=None) -> None:
        super(_HBarChart, self).__init__(parent)
        self.__bars = []  # list of (label, value, QColor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(self.ROW_H)

    def setBars(self, bars) -> None:
        self.__bars = [(str(lbl), max(0.0, float(val)), QColor(col))
                       for lbl, val, col in bars]
        count = max(1, len(self.__bars))
        self.setMinimumHeight(self.ROW_H * count + 8)
        self.updateGeometry()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.__bars:
            painter.setPen(QColor(EMPTY_COLOR))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, u"Aucune donnée")
            return

        fm = painter.fontMetrics()
        width = self.width()
        label_w = min(
            max((fm.horizontalAdvance(lbl) for lbl, _, _ in self.__bars), default=40) + 12,
            width * 0.4,
        )
        value_w = 52.0
        max_val = max((val for _, val, _ in self.__bars), default=0) or 1
        track_w = max(width - label_w - value_w - 10, 10.0)
        bar_h = self.ROW_H - 12
        y = 4.0
        for label, value, color in self.__bars:
            painter.setPen(QColor("#37474F"))
            painter.drawText(
                QRectF(0, y, label_w - 8, self.ROW_H - 6),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                fm.elidedText(label, Qt.TextElideMode.ElideRight, int(label_w - 10)),
            )

            track = QRectF(label_w, y + 3, track_w, bar_h)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#ECEFF1"))
            painter.drawRoundedRect(track, 4, 4)

            bar_w = track_w * value / max_val
            if bar_w > 0:
                painter.setBrush(color)
                painter.drawRoundedRect(QRectF(label_w, y + 3, max(bar_w, 2.0), bar_h), 4, 4)

            painter.setPen(QColor("#263238"))
            painter.drawText(
                QRectF(label_w + track_w + 6, y, value_w, self.ROW_H - 6),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                str(int(value)),
            )
            y += self.ROW_H


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
        self.setStyleSheet(
            """
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
            QFrame#kpiCard, QFrame#chartCard {
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                background: palette(base);
            }
            QFrame#headerBanner { background: #0D3B66; border-radius: 8px; }
            QLabel#headerTitle { color: white; font-size: 15px; font-weight: 600; }
            QLabel#headerPeriod { color: #BBDEFB; font-size: 11px; }
            QLabel#cardTitle { color: #455A64; font-weight: 600; }
            """
        )

        main = QVBoxLayout(self)
        main.setSpacing(10)
        main.setContentsMargins(12, 12, 12, 12)

        main.addWidget(self.__buildHeader())
        main.addWidget(self.__buildFilterGroup())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        body = QVBoxLayout(content)
        body.setSpacing(10)
        body.setContentsMargins(0, 0, 6, 0)

        body.addLayout(self.__buildKpiRow())
        body.addLayout(self.__buildChartsRow())
        body.addWidget(self.__buildByUserGroup())
        body.addWidget(self.__buildTransGroup())
        body.addStretch()

        scroll.setWidget(content)
        main.addWidget(scroll, 1)

        self.__statusLabel = QLabel(u"")
        self.__statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__statusLabel.setWordWrap(True)
        main.addWidget(self.__statusLabel)

        btnBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btnBox.rejected.connect(self.reject)
        main.addWidget(btnBox)

    def __buildHeader(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("headerBanner")
        layout = QVBoxLayout(banner)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        title = QLabel(self.windowTitle())
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        self.__periodLabel = QLabel(u"Période effective : –")
        self.__periodLabel.setObjectName("headerPeriod")
        layout.addWidget(self.__periodLabel)
        return banner

    @staticmethod
    def __cardTitle(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("cardTitle")
        return label

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

    def __buildKpiRow(self) -> QHBoxLayout:
        self.__kpi = {}
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self.__makeKpiCard("contrib", u"Contributions", "#0D3B66"))
        row.addWidget(self.__makeKpiCard("insert", u"Insertions", COLOR_INSERT))
        row.addWidget(self.__makeKpiCard("update", u"Modifications", COLOR_UPDATE))
        row.addWidget(self.__makeKpiCard("delete", u"Suppressions", COLOR_DELETE))
        row.addWidget(self.__makeKpiCard("tx", u"Transactions", COLOR_TX))
        row.addWidget(self.__makeKpiCard("fail", u"Échecs", COLOR_FAIL))
        return row

    def __buildChartsRow(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        donutCard = QFrame()
        donutCard.setObjectName("chartCard")
        donutLayout = QVBoxLayout(donutCard)
        donutLayout.setContentsMargins(12, 10, 12, 10)
        donutLayout.addWidget(self.__cardTitle(u"Répartition des contributions"))
        self.__donut = _DonutChart()
        donutLayout.addWidget(self.__donut)
        row.addWidget(donutCard, 1)

        clientCard = QFrame()
        clientCard.setObjectName("chartCard")
        clientLayout = QVBoxLayout(clientCard)
        clientLayout.setContentsMargins(12, 10, 12, 10)
        clientLayout.addWidget(self.__cardTitle(u"Contributions par client"))
        self.__clientChart = _HBarChart()
        clientLayout.addWidget(self.__clientChart)
        clientLayout.addStretch()
        row.addWidget(clientCard, 1)
        return row

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

        # Filtre réservé aux gestionnaires de groupe (pas aux super-admins via ce widget)
        self.__userRow = QWidget()
        userLayout = QHBoxLayout(self.__userRow)
        userLayout.setContentsMargins(0, 0, 0, 0)
        userLayout.addWidget(QLabel(u"Filtrer par utilisateur (id) — gestionnaire de groupe uniquement :"))
        self.__userIdEdit = QLineEdit()
        self.__userIdEdit.setPlaceholderText(u"Laisser vide pour tous les membres du groupe")
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

    def __buildTransGroup(self) -> QGroupBox:
        group = QGroupBox(u"Transactions")
        layout = QVBoxLayout(group)

        totalRow = QHBoxLayout()
        totalRow.addWidget(QLabel(u"Total :"))
        self.__transTotal = QLabel(u"0")
        boldFont = QFont()
        boldFont.setBold(True)
        boldFont.setPointSize(11)
        self.__transTotal.setFont(boldFont)
        totalRow.addWidget(self.__transTotal)

        totalRow.addSpacing(24)
        totalRow.addWidget(QLabel(u"Échecs :"))
        self.__transFailed = QLabel(u"0")
        self.__transFailed.setFont(boldFont)
        self.__transFailed.setStyleSheet("color: {};".format(COLOR_FAIL))
        totalRow.addWidget(self.__transFailed)
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

    def __buildByUserGroup(self) -> QGroupBox:
        self.__byUserGroup = QGroupBox(u"Détail par utilisateur")
        layout = QVBoxLayout(self.__byUserGroup)

        layout.addWidget(self.__cardTitle(u"Top contributeurs"))
        self.__userChart = _HBarChart()
        layout.addWidget(self.__userChart)

        self.__byUserTable = QTableWidget(0, 5)
        self.__byUserTable.setHorizontalHeaderLabels(
            [u"Utilisateur", u"Insertions", u"Modifications", u"Suppressions", u"Transactions"]
        )
        self.__byUserTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 5):
            self.__byUserTable.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.__byUserTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.__byUserTable.setAlternatingRowColors(True)
        self.__byUserTable.verticalHeader().setVisible(False)
        self.__byUserTable.setMinimumHeight(100)
        self.__byUserTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.__byUserTable)
        self.__byUserGroup.setVisible(False)
        return self.__byUserGroup

    def __buildParams(self) -> dict:
        params = {}
        if self.__cbStart.isChecked():
            params['startDate'] = self.__dateStart.date().toString("yyyy-MM-dd")
        if self.__cbEnd.isChecked():
            params['endDate'] = self.__dateEnd.date().toString("yyyy-MM-dd")
        if self.__userRow.isVisible():
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
            params = self.__buildParams()
            url = "{}/gcms/api/databases/{}/statistics".format(
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
                params=params,
                verify=ssl_verify,
                timeout=30,
            )
            response.encoding = 'utf-8'

            if response.status_code == 200:
                payload = response.json()
                self.__printDebugContext(url, params, payload)
                # reveal user filter if the API confirms elevated access
                if isinstance(payload.get('aggregate'), dict):
                    self.__userRow.setVisible(True)
                self.__fillData(payload)
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

    def __printDebugContext(self, url: str, params: dict, payload: dict) -> None:
        debug = payload.get('debug', {})
        message = {
            'request_url': url,
            'database_id': self.__databaseid,
            'database_name': self.__databasename,
            'params': params,
            'response_mode': 'aggregate' if isinstance(payload.get('aggregate'), dict) else 'user',
            'response_keys': sorted(payload.keys()),
            'api_debug': debug,
        }
        print("[STATISTICS DEBUG] {}".format(json.dumps(message, ensure_ascii=False, sort_keys=True)))

    # ------------------------------------------------------------------
    # Data display
    # ------------------------------------------------------------------

    def __fillData(self, data: dict) -> None:
        self.__fillPeriod(data.get('period', {}))

        aggregate = data.get('aggregate') if isinstance(data.get('aggregate'), dict) else None
        source = aggregate if aggregate is not None else data

        by_client = source.get('contributions', {}).get('by_client', {})
        inserts, updates, deletes = self.__sumIUD(by_client)
        transactions = source.get('transactions', {})

        self.__fillKpis(inserts, updates, deletes, transactions)
        self.__donut.setSegments([
            (u"Insertions", inserts, COLOR_INSERT),
            (u"Modifications", updates, COLOR_UPDATE),
            (u"Suppressions", deletes, COLOR_DELETE),
        ])
        self.__fillClientChart(by_client)
        self.__fillTransactions(transactions)

        by_user = data.get('by_user') if isinstance(data.get('by_user'), list) else []
        self.__fillByUser(by_user)

    def __fillPeriod(self, period: dict) -> None:
        start = period.get('start') or u"–"
        end = period.get('end') or u"–"
        self.__periodLabel.setText(u"Période effective : {} → {}".format(start, end))

        # Sans filtre explicite, la route renvoie la 1ère/dernière date de
        # transaction : on cale les sélecteurs dessus pour servir de base.
        startDate = QDate.fromString(period.get('start') or u"", "yyyy-MM-dd")
        endDate = QDate.fromString(period.get('end') or u"", "yyyy-MM-dd")
        if startDate.isValid() and not self.__cbStart.isChecked():
            self.__dateStart.setMinimumDate(startDate)
            self.__dateStart.setDate(startDate)
        if endDate.isValid() and not self.__cbEnd.isChecked():
            self.__dateEnd.setDate(endDate)

    @staticmethod
    def __sumIUD(by_client) -> tuple:
        inserts = updates = deletes = 0
        counts_iter = []
        if isinstance(by_client, dict):
            counts_iter = by_client.values()
        elif isinstance(by_client, list):
            counts_iter = by_client
        for counts in counts_iter:
            if isinstance(counts, dict):
                inserts += int(counts.get('Insert', 0) or 0)
                updates += int(counts.get('Update', 0) or 0)
                deletes += int(counts.get('Delete', 0) or 0)
        return inserts, updates, deletes

    def __fillKpis(self, inserts: int, updates: int, deletes: int, transactions: dict) -> None:
        self.__kpi['contrib'].setText(str(inserts + updates + deletes))
        self.__kpi['insert'].setText(str(inserts))
        self.__kpi['update'].setText(str(updates))
        self.__kpi['delete'].setText(str(deletes))
        self.__kpi['tx'].setText(str(transactions.get('total', 0)))
        self.__kpi['fail'].setText(str(transactions.get('failed', 0)))

    def __normalizeContributions(self, by_client) -> list:
        if isinstance(by_client, dict):
            rows = []
            for client, counts in by_client.items():
                total = 0
                if isinstance(counts, dict):
                    total = sum(int(counts.get(state, 0) or 0) for state in ('Insert', 'Update', 'Delete'))
                rows.append({'client': client, 'count': total})
            rows.sort(key=lambda row: row['count'], reverse=True)
            return rows

        if isinstance(by_client, list):
            return by_client

        return []

    def __fillClientChart(self, by_client) -> None:
        bars = []
        for index, entry in enumerate(self.__normalizeContributions(by_client)):
            raw = (entry.get('client')
                   or entry.get('client_device')
                   or entry.get('name')
                   or str(entry))
            label = CLIENT_LABELS.get(raw, raw)
            count = (entry.get('count')
                     or entry.get('contributions')
                     or entry.get('total')
                     or 0)
            bars.append((label, count, CLIENT_PALETTE[index % len(CLIENT_PALETTE)]))
        self.__clientChart.setBars(bars)

    def __fillTransactions(self, transactions: dict) -> None:
        self.__transTotal.setText(str(transactions.get('total', 0)))
        self.__transFailed.setText(str(transactions.get('failed', 0)))

        touched = transactions.get('tables') or transactions.get('touched_tables') or []
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

    def __fillByUser(self, by_user: list) -> None:
        self.__byUserTable.setRowCount(0)

        if not by_user:
            self.__byUserGroup.setVisible(False)
            self.__userChart.setBars([])
            return

        self.__byUserGroup.setVisible(True)
        bars = []
        for entry in by_user:
            username = entry.get('user', {}).get('username', u'?')
            by_client = entry.get('contributions', {}).get('by_client', {})
            inserts, updates, deletes = self.__sumIUD(by_client)
            tx_total = entry.get('transactions', {}).get('total', 0)
            bars.append((username, inserts + updates + deletes))

            row = self.__byUserTable.rowCount()
            self.__byUserTable.insertRow(row)
            self.__byUserTable.setItem(row, 0, QTableWidgetItem(username))
            for col, val in enumerate([inserts, updates, deletes, tx_total], start=1):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.__byUserTable.setItem(row, col, item)

        bars.sort(key=lambda item: item[1], reverse=True)
        self.__userChart.setBars(
            [(name, value, CLIENT_PALETTE[index % len(CLIENT_PALETTE)])
             for index, (name, value) in enumerate(bars[:10])]
        )
