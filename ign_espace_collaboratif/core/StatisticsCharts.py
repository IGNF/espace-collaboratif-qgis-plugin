# -*- coding: utf-8 -*-
"""Widgets de graphiques (dessinés avec QPainter) pour le panneau statistiques."""
from qgis.PyQt.QtCore import Qt, QRectF
from qgis.PyQt.QtGui import QColor, QFont, QPainter, QPalette
from qgis.PyQt.QtWidgets import QSizePolicy, QWidget

# Palette partagée entre les cartes KPI et les graphiques.
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


class DonutChart(QWidget):
    """Anneau (donut) proportionnel dessiné avec QPainter, avec légende."""

    def __init__(self, parent=None) -> None:
        super(DonutChart, self).__init__(parent)
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


class HBarChart(QWidget):
    """Barres horizontales dessinées avec QPainter (label · barre · valeur)."""

    ROW_H = 30

    def __init__(self, parent=None) -> None:
        super(HBarChart, self).__init__(parent)
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
