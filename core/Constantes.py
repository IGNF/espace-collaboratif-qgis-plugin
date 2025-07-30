from .Enum import Enum

'''
constantes
'''
# taille maximale pour un document uploadé
MAX_TAILLE_UPLOAD_FILE = 16000000

# Définition du protocole signant auprès du service Collaboratif l'origine de ce programme.
CLIENT_INPUT_DEVICE = "SIG-QGIS"

STATUT = Enum("undefined", "test", "submit", "pending", "pending0", "pending1", "pending2", "valid", "valid0", "reject",
              "reject0")

openStatut = [STATUT.undefined.__str__(), STATUT.submit.__str__(), STATUT.pending.__str__(), STATUT.pending0.__str__(),
              STATUT.pending1.__str__(), STATUT.pending2.__str__()]

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

# Constantes pour le chargement des couches du guichet
# Types de couches, balise <TYPE>
WMS = "WMS"
WMTS = "WMTS"
FEATURE_TYPE = WFS = "feature-type"
GEOSERVICE = "geoservice"
PARTOFURLWMTS = "%26VERSION%3D1.0.0%26REQUEST%3DGetCapabilities"
APIKEY = "ign_scan_ws"

# Système de coordonnées de référence de Ripart
EPSGCRS4326 = 4326
EPSG4326 = 'EPSG:4326'
ID_ORIGINAL = 'id_original'
ID_SQLITE = 'id_sqlite_1gnQg1s'
FINGERPRINT = 'gcms_fingerprint'
NUMREC = 'gcms_numrec'
TABLEOFTABLES = 'tableoftables'
LOADINGTEXTPROGRESS = "Chargement des couches du guichet"
UPDATETEXTPROGRESS = "Mise à jour des couches du guichet"
ESPACECO = "[ESPACE CO] "
IGNESPACECO = "IGN Espace Collaboratif"

nom_Calque_Signalement = "Signalement"
nom_Calque_Croquis_Polygone = "Croquis_EC_Polygone"
nom_Calque_Croquis_Ligne = "Croquis_EC_Ligne"
nom_Calque_Croquis_Point = "Croquis_EC_Point"

STATUS_COMMITTED = 'committed'

PROJECT_NOREGISTERED = "Votre projet QGIS doit être enregistré avant de pouvoir utiliser les fonctionnalités " \
                          "du plugin de l'espace collaboratif"
