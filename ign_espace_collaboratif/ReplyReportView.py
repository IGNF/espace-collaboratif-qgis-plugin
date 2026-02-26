import os
from PyQt5 import QtWidgets
from qgis.PyQt import uic
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ReplyReportView_base.ui'))


class ReplyReportView(QtWidgets.QDialog, FORM_CLASS):
    """
    Classe du dialogue de création du formulaire de réponse à un (ou plusieurs) signalement(s).
    """
    def __init__(self, reports, nbReportsSelected) -> None:
        """
        Constructeur de la boite de dialogue "Répondre au(x) signalement(s)"

        :param reports: la liste du (ou des) signalement(s) qui méritent une réponse
        :type reports: list

        :param nbReportsSelected: le nombre de signalement(s) sélectionné(s)
        :type nbReportsSelected: int
        """
        super(ReplyReportView, self).__init__(None)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.btn_sendResponse.clicked.connect(self.onSend)
        self.__reports = reports
        self.__nbReportsSelected = nbReportsSelected
        self.bResponse = False
        self.newResponse = None
        self.newStatus = None
        self.__initializeReplyReportView()

    def __initializeReplyReportView(self) -> None:
        """
        Initialise le dialogue de réponse à un signalement.
        """
        self.lbl_numberReportLabel.setStyleSheet("QLabel {color : blue}")  # #ff0000
        # Mise à jour de la ComboBox "Nouveau statut" avec ses libellés
        for i in range(0, 6):
            self.StatutItemsSourceComboBox.addItem(cst.ListWordings[i], i)
        numberReports = len(self.__reports)
        if numberReports == 1:
            self.lbl_numberReportLabel.setText(u"Réponse au signalement n°{0}".format(self.__reports[0].getId()))
        else:
            self.lbl_numberReportLabel.setText("Attention, {0} signalements valides "
                                               "sur {1} sélectionnés".format(numberReports, self.__nbReportsSelected))

    def onSend(self) -> None:
        """
        Losrque l'utilisateur clique sur le bouton "Enregistrer" du dialogue, la réponse et le nouveau statut
        sont enregistrés pour une utilisation dans ReplyReport.py, fonction : do
        """
        # A True, la requête de mise à jour du signalement doit être envoyée vers le serveur de l'espace collaboratif
        self.bResponse = True
        # La réponse de l'utilisateur au signalement
        self.newResponse = self.pte_NewResponse.toPlainText()
        # Le nouveau statut donné au signalement par l'utilisateur
        self.newStatus = cst.ListWordings[self.StatutItemsSourceComboBox.currentIndex()]
        # Fermeture du dialogue
        self.close()
