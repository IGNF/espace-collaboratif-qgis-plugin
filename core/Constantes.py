from .Enum import Enum

'''
constantes
'''
# taille maximale pour un document uploadé
MAX_TAILLE_UPLOAD_FILE = 16000000

# nombre par défaut de remarques par page
# NB_DEFAULT_REMARQUES_PAGINATION = 100

# Définition du protocole signant au près du service Ripart l'origine de ce programme.
RIPART_CLIENT_PROTOCOL = "_RIPART_QGIS_99712"

# Définition donnant la version de ce programme.
RIPART_CLIENT_VERSION = ""

STATUT = Enum("undefined", "submit", "pending", "pending0", "pending1", "valid", "valid0", "reject", "reject0",
              "pending2")

def getStatuts():
    statuts = [STATUT.submit.__str__(),
               STATUT.pending.__str__(),
               STATUT.pending0.__str__(),
               STATUT.pending1.__str__(),
               STATUT.valid.__str__(),
               STATUT.valid0.__str__(),
               STATUT.reject.__str__(),
               STATUT.reject0.__str__(),
               STATUT.pending2.__str__()
               ]
    return statuts


openStatut = [STATUT.undefined.__str__(), STATUT.submit.__str__(), STATUT.pending.__str__(), STATUT.pending0.__str__(),
              STATUT.pending1.__str__(), STATUT.pending2.__str__()]

statutLibelle = [u"Reçu dans nos services",
                 u"En cours de traitement",
                 u"Demande de qualification",
                 u"En attente de saisie",
                 u"Pris en compte",
                 u"Déjà pris en compte",
                 u"Rejeté (hors spéc.)",
                 u"Rejeté (hors de propos)",
                 u"En attente de validation"]

CorrespondenceStatusWording = {
    "En cours de traitement": STATUT.pending,
    "En attente de saisie": STATUT.pending1,
    "Pris en compte": STATUT.valid,
    "Déjà pris en compte": STATUT.valid0,
    "Rejeté (hors spéc.)": STATUT.reject,
    "Rejeté (hors de propos)": STATUT.reject0
}

ListWordings = [
    u"En cours de traitement",
    u"En attente de saisie",
    u"Pris en compte",
    u"Déjà pris en compte",
    u"Rejeté (hors spéc.)",
    u"Rejeté (hors de propos)"]

ZoneGeographique = Enum("UNDEFINED",
                        # France métropolitaine (Corse incluse).
                        "FXX",
                        # Terres Articques Australes.
                        "ATF",
                        # Guadeloupe
                        "GLP",
                        # Guyanne
                        "GUF",
                        # Martinique
                        "MTQ",
                        # Mayotte
                        "MYT",
                        # Nouvelle Caledonie
                        "NCL",
                        # Polynesie Française
                        "PYF",
                        # Réunion
                        "REU",
                        # Saint-Pierre et Miquelon
                        "SPM",
                        # Wallis et Futuna
                        "WLF")

namespace = {'gml': 'http://www.opengis.net/gml'}

# Constantes pour le chargement des couches du guichet
# Types de couches, balise <TYPE>
WMS = "geoservice"
WFS = "feature-type"
WMTS = "geoservice"
WCS = "WCS"
COLLABORATIF = "collaboratif.ign.fr"
WXSIGN = "wxs.ign.fr"

# Système de coordonnées de référence de Ripart
EPSGCRS4326 = 4326
EPSGCRS2154 = 2154
EPSG4326 = 'EPSG:4326'
EPSG2154 = 'EPSG:2154'
ID_ORIGINAL = 'id_original'
ID_SQLITE = 'id_sqlite_1gnQg1s'
FINGERPRINT = 'gcms_fingerprint'
NUMREC = 'gcms_numrec'
TABLEOFTABLES = 'tableoftables'
CLIENTFEATUREID = "_client_feature_id"
LOADINGTEXTPROGRESS = "Chargement des couches du guichet"
UPDATETEXTPROGRESS = "Mise à jour des couches du guichet"
ESPACECO = "[ESPACE CO] "
IGNESPACECO = "IGN Espace Collaboratif"
