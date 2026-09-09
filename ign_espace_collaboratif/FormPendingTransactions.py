# -*- coding: utf-8 -*-
"""
Boîte de dialogue "Transactions hors connexion" : liste les transactions en attente dans la db local (SQLite) et permet de déclencher leur envoi vers le serveur.
"""

import datetime
import os

from qgis.PyQt import QtCore, QtGui, QtWidgets, uic

from .core import Constantes as cst
from .core.SQLiteManager import SQLiteManager

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormPendingTransactions_base.ui'))


STATUS_COLORS = {status: QtGui.QColor(hexColor)
                 for status, hexColor in cst.PENDING_STATUS_COLORS.items()}


class FormPendingTransactions(QtWidgets.QDialog, FORM_CLASS):
    """
    Fenêtre listant les transactions hors connexion en attente d'envoi, avec un bouton
    d'envoi et la possibilité d'abandonner une transaction en échec ou en conflit.
    """

    def __init__(self, sendCallback, parent=None) -> None:
        """
        :param sendCallback: fonction sans argument qui envoie les transactions en attente et retourne
                              un tuple (nb envoyées, nb en conflit, nb en échec, compte-rendu HTML)
        """
        super(FormPendingTransactions, self).__init__(parent)
        self.setupUi(self)
        self.__sendCallback = sendCallback
        self.__pendingIds = []

        self.setWindowTitle(cst.IGNESPACECO + " - Transactions hors connexion")

        # Modes de redimensionnement des colonnes (non définissables dans le fichier .ui)
        header = self.table.horizontalHeader()
        for column in range(self.table.columnCount() - 1):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.table.columnCount() - 1, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.emptyLabel.setVisible(False)
        self.reportText.setVisible(False)

        self.table.itemSelectionChanged.connect(self.__onSelectionChanged)
        self.btnDiscard.clicked.connect(self.__onDiscard)
        self.btnRefresh.clicked.connect(self.refresh)
        self.btnDeleteAll.clicked.connect(self.__onDeleteAll)
        self.btnSend.clicked.connect(self.__onSend)
        self.btnClose.clicked.connect(self.close)

        self.refresh()

    def refresh(self) -> None:
        """
        Recharge la liste des transactions dans la base de données locale (en attente, en conflit ou en échec).
        """
        # Nettoyage des transactions déjà envoyées avec succès (statut 'sent'), qui ne doivent pas s'accumuler.
        SQLiteManager.purgeSentTransactions()

        rows = SQLiteManager.selectPendingTransactions()
        pendings = [row for row in rows if row['status'] == cst.PENDING_STATUS_PENDING]
        others = [row for row in rows if row['status'] in (cst.PENDING_STATUS_CONFLICT,
                                                           cst.PENDING_STATUS_FAILED)]
        rows = pendings + others
        self.__pendingIds = [row['id'] for row in rows]

        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(rows))
        setItem = self.table.setItem
        for i, row in enumerate(rows):
            values = [row['database'], row['layer'],
                      cst.PENDING_STATUS_LABELS.get(row['status'], row['status']),
                      self.__formatDate(row['created_at']), str(row['retry_count']),
                      row['last_error'] or ""]
            color = STATUS_COLORS.get(row['status'])
            for j, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                if color is not None:
                    item.setForeground(color)
                setItem(i, j, item)
        self.table.setUpdatesEnabled(True)

        isEmpty = len(rows) == 0
        self.table.setVisible(not isEmpty)
        self.emptyLabel.setVisible(isEmpty)
        self.subtitleLabel.setText("{0} transaction(s) en attente d'envoi.".format(len(pendings)))
        self.btnSend.setEnabled(len(pendings) > 0)
        self.btnDiscard.setEnabled(False)

    @staticmethod
    def __formatDate(isoDate) -> str:
        """
        Formate une date ISO 8601 pour un affichage lisible (JJ/MM/AAAA HH:MM).
        """
        try:
            return datetime.datetime.fromisoformat(isoDate).strftime("%d/%m/%Y %H:%M")
        except (TypeError, ValueError):
            return isoDate or ""

    def __onSelectionChanged(self) -> None:
        """
        Active le bouton d'abandon uniquement lorsqu'une ligne est sélectionnée.
        """
        self.btnDiscard.setEnabled(len(self.table.selectionModel().selectedRows()) > 0)

    def __onDiscard(self) -> None:
        """
        Supprime définitivement de la db local la transaction sélectionnée (permet d'abandonner une
        transaction en échec ou en conflit qu'on ne souhaite pas retenter).
        """
        selectedRows = self.table.selectionModel().selectedRows()
        if not selectedRows:
            return
        row = selectedRows[0].row()
        pendingId = self.__pendingIds[row]

        reply = QtWidgets.QMessageBox.question(
            self, cst.IGNESPACECO,
            "Voulez-vous abandonner définitivement cette transaction en attente ? Cette action est "
            "irréversible.",
            QtWidgets.QMessageBox.StandardButton.Yes, QtWidgets.QMessageBox.StandardButton.No)
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        SQLiteManager.deletePendingTransaction(pendingId)
        self.refresh()

    def __onDeleteAll(self) -> None:
        """
        Vide entièrement la table des transactions hors connexion (en attente, envoyées, en conflit
        ou en échec), après confirmation de l'utilisateur.
        """
        reply = QtWidgets.QMessageBox.question(
            self, cst.IGNESPACECO,
            "Voulez-vous vraiment supprimer TOUTES les transactions hors connexion (en attente, "
            "envoyées, en conflit ou en échec) ? Cette action est irréversible.",
            QtWidgets.QMessageBox.StandardButton.Yes, QtWidgets.QMessageBox.StandardButton.No)
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        SQLiteManager.deleteAllPendingTransactions()
        self.refresh()

    def __onSend(self) -> None:
        """
        Déclenche l'envoi des transactions en attente via le callback fourni par le plugin, affiche le
        compte-rendu puis rafraîchit la liste.
        """
        self.btnSend.setEnabled(False)
        self.setCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            _sent, _conflict, _failed, reporting = self.__sendCallback()
            self.reportText.setHtml(reporting)
            self.reportText.setVisible(True)
        finally:
            self.unsetCursor()
            self.refresh()
