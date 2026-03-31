import json
import os
from .core import Constantes as cst
from qgis.PyQt import uic
from qgis.core import (
    QgsGeometry,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)
from PyQt5 import QtCore, QtWidgets
from qgis.PyQt.QtGui import QIcon, QColor
from .PluginHelper import PluginHelper

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ConflictsView_base.ui'))


def ring_orientation(ring):
    """
        Retourne 'horaire' ou 'antihoraire'
        selon le signe de l'aire algébrique.
    """
    area = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i].x(), ring[i].y()
        x2, y2 = ring[i + 1].x(), ring[i + 1].y()
        area += (x2 - x1) * (y2 + y1)
    return "horaire" if area > 0 else "antihoraire"


class ConflictsView(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue de gestion des conflits d'une carte
    """
    __datas = {}
    # Le conflit courant
    __currentIndex = 0
    # Filtrer les attributs (True = filtré)
    __filterActive = True

    def __init__(self, context, featuresConflicts, parent=None) -> None:
        super(ConflictsView, self).__init__(parent)
        self.setupUi(self)
        self.__context = context
        self.__features = featuresConflicts
        self.__nbConflicts = len(featuresConflicts)
        self.__initDialog()

    def __initDialog(self):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        if self.__nbConflicts >= 1:
            self.setWindowTitle("Gestion des conflits - {} conflit(s)".format(self.__nbConflicts))
        self.__initTableWidget()
        self.__setConnectButtons()
        self.__setImagesOnButtons()

    def __initTableWidget(self):
        entete = ["Nom des champs", "Objet issu du serveur", "Votre objet", "Commentaire"]
        self.tableWidget_attributes.setHorizontalHeaderLabels(entete)
        self.tableWidget_attributes.setColumnWidth(0, 180)
        self.tableWidget_attributes.setColumnWidth(1, 290)
        self.tableWidget_attributes.setColumnWidth(2, 290)
        self.tableWidget_attributes.setColumnWidth(3, 150)
        self.__setTableWidget()

    def __resetTableWidget(self):
        self.tableWidget_attributes.clear()
        self.tableWidget_attributes.setRowCount(0)

    def __setTableWidget(self):
        self.__resetTableWidget()
        feature = self.__features[self.__currentIndex]
        self.__setLabelsConflit(feature)
        self.__setAttributes(feature)

    def __colorize_row(self, row, color):
        for col in range(self.tableWidget_attributes.columnCount()):
            item = self.tableWidget_attributes.item(row, col)
            item.setForeground(QColor(color))
            font = item.font()
            font.setBold(True)
            item.setFont(font)

    def __setColorItem(self, color='red'):
        for row in range(self.tableWidget_attributes.rowCount()):
            item = self.tableWidget_attributes.item(row, 3)  # colonne à vérifier
            if not item:
                continue
            val = item.text()
            if val == '<>':
                self.__colorize_row(row, color)

    def __setLabelsConflit(self, feature):
        typeConflict = feature['type_conflict']
        self.label_type_conflict.setText(typeConflict)
        self.label_layer_name.setText(feature['layer_name'])
        if typeConflict == cst.CONFLICT_MODIFICATION:
            self.label_context_type_conflict.setText('Le même objet a été modifié par un autre utilisateur et par vous '
                                                     'même depuis la dernière transaction.')
        elif typeConflict == cst.CONFLICT_SUPPRESSION_SERVEUR:
            self.label_context_type_conflict.setText('Le même objet a été supprimé par un autre utilisateur et modifié '
                                                     'par vous depuis la dernière transaction.')
        elif typeConflict == cst.CONFLICT_SUPPRESSION_CLIENT:
            self.label_context_type_conflict.setText('Le même objet a été modifié par un autre utilisateur et supprimé '
                                                     'par vous même depuis la dernière transaction.')

    def __mergeDataServerAndClient(self, dictServer, dictClient):
        # Si un dict est None ou pas un dict, on le remplace par {}
        dictServer = dictServer or {}
        dictClient = dictClient or {}
        # Union des clés
        try:
            all_keys = sorted(dictServer.keys() | dictClient.keys())
        except TypeError:
            # Si les clés ne sont pas comparables entre elles → pas de tri
            all_keys = dictServer.keys() | dictClient.keys()
        resultat = {}
        for k in all_keys:
            v1 = dictServer.get(k, "")
            v2 = dictClient.get(k, "")
            if v1 == "" or v2 == "":
                status = "--"
            elif v1 != v2:
                status = "<>"
            else:
                status = "="
            resultat[k] = [v1, v2, status]
        return resultat

    def __resumeGeometry(self, obj, mode="compact"):
        """
        Description complète en français, avec :
          - dimension
          - points
          - parties
          - anneaux externes
          - anneaux internes
          - orientation (pour polygones)
          - segments
          - surface / périmètre / longueur (métrique)
          - mode détail ou compact
          - calculs métriques via reprojection automatique EPSG:2154

        Exemple : Multipolygone (pts=120, parties=4, ext=4, int=6, seg=120, dim=3D, surf=45230.55m², peri=1850.44m)
        """
        # --------------------------------------------
        # 1) Extraction de la géométrie
        # --------------------------------------------
        print("[INFO] géométrie : {}".format(obj))
        try:
            geom = obj.geometry()
        except AttributeError:
            geom = obj
        if geom is None or geom.isEmpty():
            return "Géométrie vide"

        # --------------------------------------------
        # 2) Dimension
        # --------------------------------------------
        # has_z = geom.is3D()
        # has_m = geom.isMeasure()
        #
        # if has_z and has_m:
        #     dim_str = "3D+M"
        # elif has_z:
        #     dim_str = "3D"
        # elif has_m:
        #     dim_str = "2D+M"
        # else:
        #     dim_str = "2D"

        # --------------------------------------------
        # 3) Comptage points / parties / anneaux / segments
        # --------------------------------------------
        geom_type = geom.type()  # 0=Point, 1=Ligne, 2=Polygone

        nb_points = 0
        nb_parties = 0
        nb_outer = 0
        nb_holes = 0
        nb_segments = 0
        type_name = ""

        orientations = []  # orientation des anneaux ext + int

        # -----------------------
        # POINTS
        # -----------------------
        if geom_type == 0:
            pt = geom.asPoint()
            if pt:
                type_name = "Point"
                nb_points = 1
                nb_parties = 1
                nb_segments = 0
            else:
                mp = geom.asMultiPoint()
                type_name = "Multipoint"
                nb_points = len(mp)
                nb_parties = 1
                nb_segments = 0

        # -----------------------
        # LIGNES
        # -----------------------
        elif geom_type == 1:
            pl = geom.asPolyline()
            if pl:
                type_name = "Ligne"
                nb_points = len(pl)
                nb_parties = 1
                nb_segments = len(pl) - 1
            else:
                mpl = geom.asMultiPolyline()
                type_name = "Multiligne"
                nb_parties = len(mpl)
                nb_points = sum(len(line) for line in mpl)
                nb_segments = sum(len(line) - 1 for line in mpl)

        # -----------------------
        # POLYGONES
        # -----------------------
        elif geom_type == 2:
            mpoly = geom.asMultiPolygon()
            if mpoly:
                type_name = "Multipolygone"

                nb_parties = len(mpoly)
                nb_outer = nb_parties
                nb_holes = sum(len(p) - 1 for p in mpoly)
                nb_points = sum(len(p[0]) for p in mpoly)
                nb_segments = sum(len(p[0]) for p in mpoly)

                # Orientation
                for p in mpoly:
                    orientations.append(("anneau externe", ring_orientation(p[0])))
                    for h in p[1:]:
                        orientations.append(("anneau interne", ring_orientation(h)))

            else:
                poly = geom.asPolygon()
                if poly:
                    type_name = "Polygone"
                    outer = poly[0]
                    holes = poly[1:]

                    nb_outer = 1
                    nb_holes = len(holes)
                    nb_parties = 1
                    nb_points = len(outer)
                    nb_segments = len(outer)

                    orientations.append(("anneau externe", ring_orientation(outer)))
                    for h in holes:
                        orientations.append(("anneau interne", ring_orientation(h)))

        # --------------------------------------------
        # 4) Mesures métriques via reprojection EPSG:2154
        # --------------------------------------------
        src_crs = QgsProject.instance().crs()
        if src_crs.isGeographic():
            geom_m = QgsGeometry(geom)
            tgt_crs = QgsCoordinateReferenceSystem("EPSG:2154")
            transform = QgsCoordinateTransform(src_crs, tgt_crs, QgsProject.instance())
            geom_m.transform(transform)
        else:
            geom_m = geom
        # TODO chercher pourquoi la géométrie de l'objet serveur ne permet pas de calculer la surface et le périmètre
        surface = None
        perimetre = None
        longueur = None

        if geom_type == 2:
            surface = geom_m.area()
            perimetre = geom_m.length()

        if geom_type == 1:
            longueur = geom_m.length()

        # --------------------------------------------
        # 5) Pluriels
        # --------------------------------------------
        txt_points = "point" if nb_points == 1 else "points"
        txt_parts = "partie" if nb_parties == 1 else "parties"
        txt_outer = "anneau externe" if nb_outer == 1 else "anneaux externes"
        txt_holes = "anneau interne" if nb_holes == 1 else "anneaux internes"
        txt_segments = "segment" if nb_segments == 1 else "segments"

        # --------------------------------------------
        # 6) Mode compact
        # --------------------------------------------
        if mode == "compact":
            vals = [
                f"pts={nb_points}",
                f"parties={nb_parties}",
                f"ext={nb_outer}",
                f"int={nb_holes}",
                f"seg={nb_segments}"
                # f"dim={dim_str}"
            ]
            if surface is not None:
                vals.append(f"surf={surface:.2f}m²")
            if perimetre is not None:
                vals.append(f"peri={perimetre:.2f}m")
            if longueur is not None:
                vals.append(f"long={longueur:.2f}m")
            return f"{type_name} (" + ", ".join(vals) + ")"

        # --------------------------------------------
        # 7) Mode détaillé
        # --------------------------------------------
        parts = [
            f"{type_name} : {nb_points} {txt_points}",
            f"{nb_parties} {txt_parts}",
            f"{nb_outer} {txt_outer}",
            f"{nb_holes} {txt_holes}",
            f"{nb_segments} {txt_segments}"
            # dim_str
        ]

        if surface is not None:
            parts.append(f"Surface {surface : .2f} m²")
        if perimetre is not None:
            parts.append(f"Périmètre {perimetre : .2f} m")
        if longueur is not None:
            parts.append(f"Longueur {longueur : .2f} m")

        # Orientations
        for name, ori in orientations:
            parts.append(f"{name} : {ori}")

        return ", ".join(parts)

    def __setAttributes(self, feature):
        resultats = self.__mergeDataServerAndClient(json.loads(feature['data_server']),
                                                    json.loads(feature['data_client']))
        print("[INFO] Resultat : {}".format(resultats))
        discardFields = ['date_modification', 'gcms_fingerprint', 'id_sqlite_1gnQg1s']
        for k, v in resultats.items():
            if k in discardFields:
                continue
            rowPosition = self.tableWidget_attributes.rowCount()
            self.tableWidget_attributes.insertRow(rowPosition)

            # Colonne "Nom des champs"
            item = QtWidgets.QTableWidgetItem(str(k))
            self.tableWidget_attributes.setItem(rowPosition, 0, item)

            # Colonne "Objet issu du serveur"
            if k == 'geometrie':
                geom = QgsGeometry.fromWkt(v[0])
                item = QtWidgets.QTableWidgetItem(self.__resumeGeometry(geom))
            else:
                item = QtWidgets.QTableWidgetItem(str(v[0]))
            self.tableWidget_attributes.setItem(rowPosition, 1, item)

            # Colonne "Votre objet"
            if k == 'geometrie':
                geom = QgsGeometry.fromWkt(feature['geometry_conflict'])
                item = QtWidgets.QTableWidgetItem(self.__resumeGeometry(geom))
            else:
                item = QtWidgets.QTableWidgetItem(str(v[1]))
            self.tableWidget_attributes.setItem(rowPosition, 2, item)

            # Colonne "Commentaire"
            item = QtWidgets.QTableWidgetItem(str(v[2]))
            self.tableWidget_attributes.setItem(rowPosition, 3, item)
        self.tableWidget_attributes.resizeRowsToContents()
        # Au départ, affichage uniquement des différences
        self.__showDiff()

    def __setConnectButtons(self):
        self.pushButton_conflict_create_report.clicked.connect(self.__createReport)
        self.pushButton_conflict_previous.clicked.connect(self.__previous)
        self.pushButton_conflict_next.clicked.connect(self.__next)
        self.pushButton_conflict_see_all_fields.clicked.connect(self.__seeAllFields)
        self.pushButton_conflict_reload.clicked.connect(self.__reload)
        self.pushButton_conflict_create.clicked.connect(self.__create)
        self.pushButton_conflict_delete.clicked.connect(self.__delete)
        self.pushButton_conflict_validate.clicked.connect(self.__validate)
        self.pushButton_conflict_validate_all.clicked.connect(self.__validateAll)
        self.pushButton_conflict_undo.clicked.connect(self.__undo)

    def __setImagesOnButtons(self):
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/create.png")
        self.pushButton_conflict_create_report.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_previous.png")
        self.pushButton_conflict_previous.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_next.png")
        self.pushButton_conflict_next.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_see_all_fields.png")
        self.pushButton_conflict_see_all_fields.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_reload.png")
        self.pushButton_conflict_reload.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_create.png")
        self.pushButton_conflict_create.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_delete.png")
        self.pushButton_conflict_delete.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_validate.png")
        self.pushButton_conflict_validate.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_validate_all.png")
        self.pushButton_conflict_validate_all.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_undo.png")
        self.pushButton_conflict_undo.setIcon(icon)

    # -- 1) Créer un signalement --
    def __createReport(self):
        PluginHelper.showMessageBox("createReport")

    # -- 2) Aller au conflit précédent --
    def __previous(self):
        if self.__currentIndex > 0:
            self.__currentIndex -= 1
            self.__setTableWidget()

    # -- 3) Aller au conflit suivant --
    def __next(self):
        if self.__currentIndex < len(self.__features) - 1:
            self.__currentIndex += 1
            self.__setTableWidget()

    # -- 4) Filtrer les attributs --
    def __showAll(self):
        """Affiche toutes les lignes."""
        for row in range(self.tableWidget_attributes.rowCount()):
            self.tableWidget_attributes.setRowHidden(row, False)
        self.__setColorItem()

    def __showDiff(self):
        """N'affiche que les lignes dont la valeur de la colonne testée est '<>'."""
        for row in range(self.tableWidget_attributes.rowCount()):
            item = self.tableWidget_attributes.item(row, 3)
            if item is None or item.text() != "<>":
                self.tableWidget_attributes.setRowHidden(row, True)
            else:
                self.tableWidget_attributes.setRowHidden(row, False)
        self.__setColorItem('black')

    def __seeAllFields(self):
        """Alterner l'affichage entre attributs filtrés et non filtrés."""
        if self.__filterActive:
            self.__showAll()
        else:
            self.__showDiff()
        # alterne l’état
        self.__filterActive = not self.__filterActive

    def __reload(self):
        PluginHelper.showMessageBox("reload")

    def __create(self):
        PluginHelper.showMessageBox("create")

    def __delete(self):
        PluginHelper.showMessageBox("delete")

    def __validate(self):
        PluginHelper.showMessageBox("validate")

    def __validateAll(self):
        PluginHelper.showMessageBox("validateAll")

    def __undo(self):
        PluginHelper.showMessageBox("undo")
