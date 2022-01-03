import os

from qgis.PyQt import QtGui, uic, QtWidgets
from .core import ConstanteRipart as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ReplyReportView_base.ui'))


class ReplyReportView(QtWidgets.QDialog, FORM_CLASS):
    """
    Formulaire de réponse à une remarque
    """
    reports = []
    newResponse = ""
    newStatus = ""

    def __init__(self, reports):
        """Constructor."""

        super(ReplyReportView, self).__init__(None)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.InitializeReplyReportView()
        self.btn_sendResponse.clicked.connect(self.onSend)
        self.reports = reports

    def InitializeReplyReportView(self):
        # Mise à jour de la ComboBox "Nouveau statut" avec ses libellés
        for i in range(0, 6):
            self.StatutItemsSourceComboBox.addItem(cst.ListWordings[i], i)
            numberReports = len(self.reports)
            if numberReports == 1:
                self.lbl_numberReportLabel.setText(u"Réponse au signalement n°{0}".format(self.Reports[0].id))
            else:
                self.lbl_numberReportLabel.setText("Attention, {0} signalements sélectionnés".format(numberReports))

    def onSend(self):
        self.newResponse = self.pte_NewResponse.toPlainText()
        print(self.newResponse)
        self.newStatus = cst.ListWordings[self.StatutItemsSourceComboBox.currentIndex()]
        print(self.newStatus)
        self.close()
