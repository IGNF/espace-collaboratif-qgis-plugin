# -*- coding: utf-8 -*-
"""
Created on 2 oct. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""

import logging
import os
from datetime import datetime
import dateutil.relativedelta
from os.path import expanduser


class PluginLogger(object):
    """
    Classe implémentant un fichier de log. Le fichier de log se trouve dans le répertoire
    "C:/Users/nom_utilisateur/.IGN_plugin_logs" et se nomme par exemple "20250730_espaceco.log". Tous les fichiers
    plus vieux d'un mois sont supprimés à l'initialisation de la classe.
    """

    # Paramètres du log
    logger = None
    logpath = None

    def __init__(self, parameter="") -> None:
        """
        Constructeur.

        :param parameter: le nom de la classe qui initialise le fichier de log
        :type parameter: str
        """
        # trouve le dossier d'installation du plugin et le nom du fichier de log (yyyymmdd_espaceco.log)
        home = expanduser("~")
        logdir = os.path.join(home, ".IGN_plugin_logs")
        today = datetime.now().date().strftime('%Y%m%d')
        logFilename = today + "_espaceco.log"
        self.logpath = os.path.abspath(os.path.join(logdir, logFilename))

        if not os.path.exists(logdir):
            os.makedirs(logdir)

        if parameter == "":
            parameter = "espaceco"

        self.logger = logging.getLogger(parameter)
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(self.logpath)
        fh.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(fh)

        # supprime les anciens fichiers de log
        self.removeOldLogs(logdir)

    def getPluginLogger(self) -> logging.Logger:
        """
        return: l'instance du logger
        """
        return self.logger

    def removeOldLogs(self, logdir) -> None:
        """
        Supprime les fichiers de logs plus vieux qu'un mois.
        
        :param logdir: le répertoire des fichiers de log
        :type logdir: str
        """
        today = datetime.now().date()
        lastMonth = today + dateutil.relativedelta.relativedelta(months=-1)
        last = lastMonth.strftime('%Y%m%d')

        if os.path.exists(logdir):
            for f in os.listdir(logdir):
                if f[:8] < last:
                    os.remove(os.path.join(logdir, f))

    def getLogpath(self) -> str:
        """
        :return: le chemin complet du fichier de log
        """
        return self.logpath
