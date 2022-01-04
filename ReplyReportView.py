import os
from qgis.PyQt import QtGui, uic, QtWidgets
from .core import ConstanteRipart as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ReplyReportView_base.ui'))


class ReplyReportView(QtWidgets.QDialog, FORM_CLASS):
    """
    Formulaire de réponse à un signalement
    """
    reports = []
    newResponse = ""
    newStatus = ""
    bResponse = False

    def __init__(self, reports):
        super(ReplyReportView, self).__init__(None)
        self.setupUi(self)
        self.reports = reports
        self.btn_sendResponse.clicked.connect(self.onSend)
        self.InitializeReplyReportView()

    def InitializeReplyReportView(self):
        self.lbl_numberReportLabel.setStyleSheet("QLabel {color : blue}")  # #ff0000
        # Mise à jour de la ComboBox "Nouveau statut" avec ses libellés
        for i in range(0, 6):
            self.StatutItemsSourceComboBox.addItem(cst.ListWordings[i], i)
        numberReports = len(self.reports)
        if numberReports == 1:
            self.lbl_numberReportLabel.setText(u"Réponse au signalement n°{0}".format(self.reports[0].id))
        else:
            self.lbl_numberReportLabel.setText("Attention, {0} signalements sélectionnés".format(numberReports))

    def onSend(self):
        self.bResponse = True
        self.newResponse = self.pte_NewResponse.toPlainText()
        print(self.newResponse)
        self.newStatus = cst.ListWordings[self.StatutItemsSourceComboBox.currentIndex()]
        print(self.newStatus)
        self.close()
