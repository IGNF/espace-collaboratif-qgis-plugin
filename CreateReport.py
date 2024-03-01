# -*- coding: utf-8 -*-
"""
Created on 27 oct. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
from .core.Point import Point
from .core.RipartLoggerCl import RipartLogger
from .FormCreerRemarque import FormCreerRemarque
from .PluginHelper import PluginHelper
from .ToolsReport import ToolsReport
from .core.Report import Report
from .core.MapToolsReport import MapToolsReport
from PyQt5.QtWidgets import QApplication
from .core import Constantes as cst
from PyQt5.QtCore import Qt


# Classe pour la création d'un nouveau signalement
class CreateReport(object):

    def __init__(self, context):
        self.__logger = RipartLogger("CreateReport").getRipartLogger()
        self.__context = context
        clipboard = QApplication.clipboard()
        clipboard.clear()
        self.__activeLayer = self.__context.iface.activeLayer()
        self.__canvas = self.__context.iface.mapCanvas()

    # Création d'un nouveau signalement
    def do(self):
        clipboard = QApplication.clipboard()
        clipboard.clear()
        hasSelectedFeature = self.__context.hasMapSelectedFeatures()
        # Sans croquis
        if not hasSelectedFeature:
            if self.__activeLayer.name() != cst.nom_Calque_Signalement:
                return
            mapToolsReport = MapToolsReport(self.__canvas, self.__activeLayer)
            self.__canvas.setMapTool(mapToolsReport)
        # Avec croquis
        else:
            print("Création d'un croquis avec le ou les objet(s) sélectionné(s)")

        # try:
        #     hasSelectedFeature = self.__context.hasMapSelectedFeatures()
        #
        #     if not hasSelectedFeature:
        #         PluginHelper.showMessageBox(u"Aucun objet sélectionné.\nIl est donc impossible de déterminer le "
        #                                     u"point d'application du nouveau signalement à créer.")
        #         return    # si pas d'objet sélectionné, on arrête le processus
        #
        #     if self.__context.client is None:
        #         connResult = self.__context.getConnexionEspaceCollaboratif()
        #         if not connResult:
        #             return 0
        #         # la connexion a échoué, on ne fait rien
        #         if self.__context.client is None:
        #             self.__context.iface.messageBar().pushMessage("", u"Un problème de connexion avec le service est "
        #                                                             u"survenu. Veuillez rééssayer", level=2,
        #                                                         duration=3)
        #             return
        #
        #     # Création des croquis à partir de la sélection de features
        #     croquisList = self.__context.makeCroquisFromSelection()
        #
        #     # Il y a eu un problème à la génération des croquis, on sort
        #     if len(croquisList) == 0:
        #         return
        #     self.logger.debug(str(len(croquisList)) + u" croquis générés")
        #
        #     # ouverture du formulaire de création de la remarque
        #     formCreate = FormCreerRemarque(context=self.__context, NbSketch=len(croquisList))
        #     formCreate.exec_()
        #
        #     # création de la remarque
        #     if formCreate.bSend:
        #         self._createNewReport(formCreate, croquisList)
        #
        # except Exception as e:
        #     self.logger.error(format(e))
        #     self.__context.iface.messageBar().pushMessage("", u"Problème dans la création de signalement(s)", level=2,
        #                                                 duration=3)

    def _createNewReport(self, formCreate, croquisList):
        """Création d'une nouvelle remarque (requête au service ripart)
        
        :param formCreate: le formulaire de création de la remarque
        :type formCreate: FormCreerRemarque
        
        :param croquisList: la liste des croquis associés à la remarque
        :type croquisList: list d'objet Croquis
        """
        try:
            tmpRem = Remarque()
                
            tmpRem.setCommentaire(formCreate.textEditMessage.toPlainText())
            
            selectedThemes = formCreate.getSelectedThemes()
            PluginHelper.save_preferredThemes(self.__context.projectDir, selectedThemes)

            PluginHelper.save_preferredGroup(self.__context.projectDir, formCreate.preferredGroup)
            
            tmpRem.addThemeList(selectedThemes)  
            
            # liste contenant les identifiants des nouvelles remarques créées
            listNewReportIds = []
            
            # si on doit attacher un document
            if formCreate.optionWithAttDoc():
                tmpRem.addDocument(formCreate.getAttachedDoc())
           
            # création d'une seule remarque
            if formCreate.isSingleRemark():
                listNewReportIds.clear()
                newReport = self._prepareAndSendReport(tmpRem, croquisList, formCreate.optionWithCroquis(), formCreate.idSelectedGeogroup)
                if newReport is None:
                    self.__context.iface.messageBar().pushMessage("", u"Une erreur est survenue dans la création du "
                                                                    u"signalement ", level=2, duration=3)
                     
                listNewReportIds.append(newReport.id)
            
            # création de plusieurs signalements
            else:             
                listNewReportIds.clear()
                for cr in croquisList:                
                    tmpRem.clearCroquis()
                    newReport = self._prepareAndSendReport(tmpRem, [cr], formCreate.optionWithCroquis(), formCreate.idSelectedGeogroup)
                    if newReport is None:
                        self.__context.iface.messageBar().pushMessage("", u"Une erreur est survenue dans la création "
                                                                        u"d'un signalement", level=2, duration=15)
                        continue
                    listNewReportIds.append(newReport.id)
   
            self.__context.refresh_layers()

            message = 'Succès '
            nbReports = len(listNewReportIds)
            if nbReports == 1:
                message += ": création d'un nouveau signalement n°{0}".format(listNewReportIds[0])
            else:
                message += "de la création de {0} nouveaux signalements pour l'espace collaboratif.\n".format(nbReports)
                message += "Les identifiants vont de {0} à {1}.".format(listNewReportIds[0], listNewReportIds[nbReports-1])
            PluginHelper.showMessageBox(message)

        except Exception as e:
            self.__context.iface.messageBar().pushMessage("", format(e), level=2, duration=3)
            self.logger.error("in _createNewReport " + format(e))

        finally:
            self.__context.conn.close()

    def _prepareAndSendReport(self, tmpRem, croquisList, optionWithCroquis, idSelectedGeogroupe):
        """Trouve la position de la remarque, ajoute les croquis et envoie la requête au service Ripart
        
        :param tmpRem: remarque temporaire
        :type tmpRem: Remarque
        
        :param croquisList: la liste de croquis à ajouter à la remarque
        :type croquisList: List
        
        :param optionWithCroquis: option d'ajouter ou non les croquis à la remarque
        :type optionWithCroquis: boolean
        
        :return: La Remarque créée
        :rtype: Remarque
        """
        
        client = self.__context.client
        
        positionRemarque = self.__context.getPositionRemarque(croquisList)
                    
        if positionRemarque is None:
            self.logger.error("error in _prepareAndSendReport : positionRemarque not created")
            return None
        
        tmpRem.setPosition(positionRemarque)
                    
        if optionWithCroquis:
            tmpRem.addCroquisList(croquisList)
                   
        # create new remark (ripart service)
        remarqueNouvelle = client.createRemarque(tmpRem, idSelectedGeogroupe)

        self.logger.info(u"Succès de la création du nouveau signalement n°" + str(remarqueNouvelle.id))
        
        PluginHelper.insertRemarques(self.__context.conn, remarqueNouvelle)
        self.__context.conn.commit()
            
        return remarqueNouvelle
