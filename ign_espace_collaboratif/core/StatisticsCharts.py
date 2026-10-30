# -*- coding: utf-8 -*-
"""Widgets de graphiques (dessinés avec QPainter) pour le panneau statistiques."""
from qgis.PyQt.QtCore import Qt, QRectF
from qgis.PyQt.QtGui import QColor, QPainter
from qgis.PyQt.QtWidgets import QSizePolicy, QWidget

# Palette partagée entre les cartes KPI et les graphiques.
COLOR_INSERT = "#845BD0"   # violet – insertions
COLOR_UPDATE = "#3D9665"   # vert – modifications
COLOR_DELETE = "#C46F2A"   # orange – suppressions
COLOR_TX = "#00838F"       # cyan  – transactions
COLOR_FAIL = "#EF6C00"     # orange – échecs
EMPTY_COLOR = "#9E9E9E"


class ContributionBreakdown(QWidget):
    """Affiche la répartition des contributions."""

    def __init__(self, parent=None) -> None:
        super(ContributionBreakdown, self).__init__(parent)
        self.__segments = []
        self.setMinimumHeight(116)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def setSegments(self, segments) -> None:
        """Stocke des éléments ``(libellé, nombre, couleur)`` à dessiner.

        Les nombres sont convertis en flottants positifs ou nuls. Les
        pourcentages de la légende sont calculés sur le total des segments.
        """
        self.__segments = [(str(label), max(0.0, float(value)), QColor(color))
                           for label, value, color in segments]
        self.update()

    def paintEvent(self, event) -> None:  
        """Dessine la barre proportionnelle et une ligne par type de contribution.

        Chaque ligne affiche le libellé, le nombre absolu et la part du total.
        Si tous les nombres sont nuls, la barre reste vide et les parts valent 0.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        total = sum(value for _, value, _ in self.__segments)
        track = QRectF(0, 4, max(self.width(), 1), 8)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#ECEEF1"))
        painter.drawRoundedRect(track, 4, 4)

        x = track.left()
        for _, value, color in self.__segments:
            if total <= 0 or value <= 0:
                continue
            width = track.width() * value / total
            painter.setBrush(color)
            painter.drawRect(QRectF(x, track.top(), width, track.height()))
            x += width

        row_height = 30
        for index, (label, value, color) in enumerate(self.__segments):
            y = 24 + index * row_height
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(0, y + 7, 10, 10), 2, 2)
            painter.setPen(QColor("#1A1A1A"))
            painter.drawText(QRectF(18, y, self.width() - 112, row_height),
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                             label)
            percentage = 100.0 * value / total if total else 0.0
            painter.setPen(QColor("#1A1A1A"))
            painter.drawText(QRectF(self.width() - 104, y, 34, row_height),
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                             str(int(value)))
            painter.setPen(QColor("#5B5B5B"))
            painter.drawText(QRectF(self.width() - 64, y, 64, row_height),
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                             u"· {:.0f} %".format(percentage))


class HBarChart(QWidget):
    """Dessine des barres horizontales avec libellés, nombres et pourcentages.

    Chaque barre est un tuple ``(libellé, valeur, couleur)`` ou
    ``(libellé, valeur, couleur, afficher_info)``. Sa longueur est rapportée à
    la valeur maximale; son pourcentage est calculé sur la somme des valeurs.
    """

    ROW_H = 30

    def __init__(self, parent=None) -> None:
        super(HBarChart, self).__init__(parent)
        self.__bars = []  # list of (label, value, QColor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(self.ROW_H)

    def setBars(self, bars) -> None:
        """Normalise les barres et adapte la hauteur au nombre de lignes.

        Les valeurs deviennent des flottants positifs ou nuls et les couleurs
        des objets ``QColor``. Le quatrième champ facultatif affiche un repère
        d'information après le libellé; les tuples à trois champs restent valides.
        """
        normalized_bars = []
        for bar in bars:
            label, value, color = bar[:3]
            show_info = len(bar) > 3 and bool(bar[3])
            normalized_bars.append((str(label), max(0.0, float(value)),
                                    QColor(color), show_info))
        self.__bars = normalized_bars
        count = max(1, len(self.__bars))
        self.setMinimumHeight(self.ROW_H * count + 8)
        self.updateGeometry()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        """Dessine une ligne par barre, ou le message d'absence de données.

        Chaque ligne contient un libellé éventuellement raccourci, une piste
        remplie selon la valeur maximale, puis le nombre et sa part du total.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.__bars:
            painter.setPen(QColor(EMPTY_COLOR))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, u"Aucune donnée")
            return

        fm = painter.fontMetrics()
        width = self.width()
        label_width = max(
            (fm.horizontalAdvance(label) + (16 if show_info else 0)
             for label, _, _, show_info in self.__bars),
            default=40,
        )
        label_w = min(label_width + 12, width * 0.4)
        value_w = 76.0
        max_val = max((value for _, value, _, _ in self.__bars), default=0) or 1
        total = sum(value for _, value, _, _ in self.__bars)
        track_w = max(width - label_w - value_w - 10, 10.0)
        bar_h = self.ROW_H - 12
        y = 4.0
        for label, value, color, show_info in self.__bars:
            painter.setPen(QColor("#37474F"))
            text_width = label_w - 8 - (16 if show_info else 0)
            painter.drawText(
                QRectF(0, y, text_width, self.ROW_H - 6),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                fm.elidedText(label, Qt.TextElideMode.ElideRight, int(text_width - 2)),
            )
            if show_info:
                info_x = min(fm.horizontalAdvance(label), text_width) + 4
                info_rect = QRectF(info_x, y + 6, 12, 12)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QColor("#5B5B5B"))
                painter.drawEllipse(info_rect)
                painter.drawText(info_rect, Qt.AlignmentFlag.AlignCenter, "i")

            track = QRectF(label_w, y + 3, track_w, bar_h)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#ECEFF1"))
            painter.drawRoundedRect(track, 4, 4)

            bar_w = track_w * value / max_val
            if bar_w > 0:
                painter.setBrush(color)
                painter.drawRoundedRect(QRectF(label_w, y + 3, max(bar_w, 2.0), bar_h), 4, 4)

            painter.setPen(QColor("#263238"))
            percentage = 100.0 * value / total if total else 0.0
            painter.drawText(
                QRectF(label_w + track_w + 6, y, value_w, self.ROW_H - 6),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                u"{}  ·  {:.0f}%".format(int(value), percentage),
            )
            y += self.ROW_H
