import os
from qgis.PyQt import uic, QtWidgets
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ReplyReportView_base.ui'))


# Formulaire de réponse à un signalement
class ReplyReportView(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, reports):
        super(ReplyReportView, self).__init__(None)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.btn_sendResponse.clicked.connect(self.onSend)
        self.__reports = reports
        self.bResponse = False
        self.newResponse = None
        self.newStatus = None
        self.__initializeReplyReportView()

    def __initializeReplyReportView(self):
        self.lbl_numberReportLabel.setStyleSheet("QLabel {color : blue}")  # #ff0000
        # Mise à jour de la ComboBox "Nouveau statut" avec ses libellés
        for i in range(0, 6):
            self.StatutItemsSourceComboBox.addItem(cst.ListWordings[i], i)
        numberReports = len(self.__reports)
        if numberReports == 1:
            self.lbl_numberReportLabel.setText(u"Réponse au signalement n°{0}".format(self.__reports[0].getId()))
        else:
            self.lbl_numberReportLabel.setText("Attention, {0} signalements sélectionnés".format(numberReports))

    def onSend(self):
        self.bResponse = True
        self.newResponse = self.pte_NewResponse.toPlainText()
        self.newStatus = cst.ListWordings[self.StatutItemsSourceComboBox.currentIndex()]
        self.close()
