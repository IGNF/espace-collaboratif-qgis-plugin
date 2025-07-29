import ntpath
import json
import os.path
from qgis.utils import spatialite_connect
from qgis.core import QgsProject
from . import Constantes as cst
from .Wkt import Wkt


class SQLiteManager(object):
    """
    Classe permettant la gestion d'une base SQLite liée à un projet QGIS.
    """

    def __init__(self) -> None:
        """
        Initialisation de la gestion d'une base SQLite avec son chemin complet.
        Par exemple : .../ProjetQGIS/monprojet_espaceco.sqlite
        """
        self.__dbPath = SQLiteManager.getBaseSqlitePath()

    @staticmethod
    def getBaseSqlitePath() -> str:
        """
        Recherche le chemin complet de la base SQLite.
        Exemple : .../ProjetQGIS/monprojet_espaceco.sqlite
        NB : le nom est toujours préfixé par '_espaceco'

        :return: retourne le chemin et le nom de la base de la base SQlite.
        """
        projectDir = QgsProject.instance().homePath()
        fname = ntpath.basename(QgsProject.instance().fileName())
        projectFileName = fname[:fname.find(".")]
        dbName = "{}_espaceco".format(projectFileName)
        dbPath = "{0}/{1}.sqlite".format(projectDir, dbName)
        return dbPath

    @staticmethod
    def executeSQL(sql) -> None:
        """
        Execute un code sql en ouvrant/fermant une transaction à la table SQLite

        :param sql: la commande sql à lancer
        :type sql: str
        """
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        cur.close()
        connection.commit()
        connection.close()

    @staticmethod
    def isTableExist(tableName) -> bool:
        """
        Vérifie si une table existe dans la base SQLite.

        :param tableName: le nom de la table à rechercher
        :type tableName: str

        :return: True si la table existe, False Si la base SQLite n'est pas trouvée
       """
        bFind = True
        dbPath = SQLiteManager.getBaseSqlitePath()
        # Si la base SQLite n'existe pas, on passe
        if not os.path.isfile(dbPath):
            return False
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        sql = u"SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(tableName)
        cur = connection.cursor()
        cur.execute(sql)
        if cur.fetchone() is None:
            bFind = False
        cur.close()
        connection.close()
        return bFind

    def __setAttributesTableToSql(self, layer) -> ():
        """
        Écrit la partie SQL pour les attributs de la couche passée en paramètres.
        En déduit le type de géométrie de la couche et si la colonne détruit doit exister dans la table
        (uniquement pour les tables BDUni).

        :param layer: une couche du projet QGIS
        :type layer: QgsVectorLayer

        :return: un tuple contenant la commande SQL, le type de géométrie et un booléen à True si c'est une couche BDUni
        """

        columnDetruitExist = False
        typeGeometrie = ''
        sqlAttributes = ''
        for value in layer.attributes:
            if self.__setSwitchType(value['type']) == '':
                return "", "", False
            if value['name'] == "detruit":
                columnDetruitExist = True
                sqlAttributes += "{0} {1},".format(value['name'], self.__setSwitchType(value['type']))
            elif value['name'] == layer.geometryName:
                typeGeometrie = self.__setSwitchType(value['type'])
            # au cas où il y aurait déjà un attribut nommé id_sqlite
            elif value['name'] == cst.ID_SQLITE:
                sqlAttributes += "{0} {1},".format(cst.ID_ORIGINAL, self.__setSwitchType(value['type']))
            # TODO Noémie : 29/7/22 Arnaud m'a indiqué que gcms_fingerprint et gcms_numrec ne doivent pas apparaitre
            #  TODO comme attributs cachés vis à vis de l'extérieur, cf les urls suivantes TODO (BIEN)
            #   https://qlf-collaboratif.ign.fr/collaboratif-3.4/gcms/database/bduni_recette_test/feature-type
            #   /equipement_de_transport.json TODO (PAS BIEN)
            #    https://espacecollaboratif.ign.fr/gcms/database/bduni_interne_qualif_fxx/feature-type
            #    /equipement_de_transport.json
            elif value['name'] == cst.FINGERPRINT or value['name'] == cst.NUMREC:
                continue
            else:
                tmp = value['name'].replace(' ', '')
                sqlAttributes += "{0} {1},".format(tmp, self.__setSwitchType(value['type']))
        # Anomalie 17196, l'identifiant ID_SQLITE et FINGERPRINT sont positionnés en dernier dans le formulaire
        sqlAttributes += "{0} INTEGER PRIMARY KEY AUTOINCREMENT".format(cst.ID_SQLITE)
        if not layer.isStandard:
            # ordre d'insertion geometrie puis gcms_fingerprint
            sqlAttributes += ",{0} TEXT".format(cst.FINGERPRINT)
        return sqlAttributes, typeGeometrie, columnDetruitExist

    def __addGeometryColumn(self, parameters) -> str:
        """
        Ajout de la colonne géométrie (2D ou 3D) à une table.

        :param parameters: dictionnaire contenant le nom de la table, le nom de la géométrie,
                           le système de référence de coordonnées, le type de géométrie
                           et un booléen à True si la couche est 3D.

        :return: la partie de la commande SQL liée à la géométrie
        """
        # Paramétrage de la colonne géométrie en 2D par défaut
        if parameters['is3D']:
            sql = "SELECT AddGeometryColumn('{0}', '{1}', {2}, '{3}', 'XYZ')".format(parameters['tableName'],
                                                                                     parameters['geometryName'],
                                                                                     parameters['crs'],
                                                                                     parameters['geometryType'])
        else:
            sql = "SELECT AddGeometryColumn('{0}', '{1}', {2}, '{3}', 'XY')".format(parameters['tableName'],
                                                                                    parameters['geometryName'],
                                                                                    parameters['crs'],
                                                                                    parameters['geometryType'])
        return sql

    def createTableFromLayer(self, layer) -> bool:
        """
        Création d'une table dans la base SQLite du projet en cours pour une couche passée en paramètre.
        La base SQLite est compactée après chaque création de table.

        :param layer: une couche du projet QGIS
        :type layer: QgsVectorLayer

        :return: un booléen à True, si c'est une couche BDUni, False sinon
        """
        t = self.__setAttributesTableToSql(layer)
        if t[0] == "" and t[1] == "" and t[2] is False:
            raise Exception("SQLite : création de la table {} impossible, "
                            "un type de colonne est inconnu".format(layer.name))
        connection = spatialite_connect(self.__dbPath)
        sql = u"CREATE TABLE {0} (".format(layer.name)
        sql += t[0]
        sql += ')'
        cur = connection.cursor()
        cur.execute(sql)
        parameters_geometry_column = {'tableName': layer.name, 'geometryName': layer.geometryName,
                                      'crs': cst.EPSGCRS4326, 'geometryType': t[1], 'is3D': layer.is3d}
        sqlGeometryColumn = self.__addGeometryColumn(parameters_geometry_column)
        cur.execute(sqlGeometryColumn)
        if not SQLiteManager.isTableExist(layer.name):
            raise Exception("SQLiteManager : création de la table {} impossible.".format(layer.name))
        print("SQLiteManager : table {} créée.".format(layer.name))
        connection.commit()
        cur.close()
        connection.close()
        # compactage de la base
        SQLiteManager.vacuumDatabase()
        return t[2]

    def __setSwitchType(self, vType) -> str:
        """
        Correspondance entre un type d'attribut d'une classe d'objet d'une couche QGIS
        et un type de colonne d'une table SQLite.

        :param vType: la valeur d'un type d'attribut
        :type vType: str

        :return: le type de colonne SQLite
        """
        if vType == 'Boolean':
            return 'INTEGER'
        elif vType == 'Integer':
            return 'INTEGER'
        elif vType == 'Double':
            return 'REAL'
        elif vType == 'DateTime':
            return 'TEXT'
        elif vType == 'Document':
            return 'TEXT'
        elif vType == 'Like':
            return 'TEXT'
        elif vType == 'JsonValue':
            return 'TEXT'
        elif vType == 'Date':
            return 'TEXT'
        elif vType == 'String':
            return 'TEXT'
        elif vType == 'YearMonth':
            return 'TEXT'
        elif vType == 'Year':
            return 'TEXT'
        elif vType == "LineString":
            return 'LINESTRING'
        elif vType == 'MultiLineString':
            return 'MULTILINESTRING'
        elif vType == 'Point':
            return 'POINT'
        elif vType == 'MultiPoint':
            return 'MULTIPOINT'
        elif vType == 'Polygon':
            return 'POLYGON'
        elif vType == 'MultiPolygon':
            return 'MULTIPOLYGON'
        elif vType == 'Geometry':
            return ''
        else:
            return ''

    def __setColumnsValuesForInsert(self, attributesRow, parameters, wkt) -> ():
        """
        Établir la partie insertion colonne/valeur et la partie géométrique d'une requête SQL.

        :param attributesRow: l'ensemble des attributs d'un objet QGIS sous la forme nom/valeur
        :type attributesRow: dict

        :param parameters: les paramètres nécessaires au codage d'une commande SQL
        :type parameters: dict

        :param wkt: l'objet permettant de coder la géométrie en WKT
        :type wkt: Wkt

        :return: tuple contenant les colonnes et les valeurs pour une table SQLite
        """
        tmpColumns = '('
        tmpValues = '('
        for column, value in attributesRow.items():
            if column == parameters['geometryName']:
                tmpColumns += '{0},'.format(column)
                tmpValues += wkt.toGetGeometry(value)
                continue
            elif column == cst.ID_SQLITE:
                tmpColumns += '{0},'.format(cst.ID_ORIGINAL)
            else:
                # un nom de colonne ne doit pas contenir d'espace
                if column.find(' ') != -1:
                    message = "Le nom de colonne [{}] ne doit pas contenir d'espace, il est impossible d'importer " \
                              "la couche, veuillez demander à revoir la configuration de la table sur le serveur."\
                        .format(column)
                    raise Exception(message)
                tmpColumns += '{0},'.format(column)

            if value is None:
                tmpValues += "'NULL',"
            else:
                if type(value) is dict:
                    if 'username' in value:
                        value = value['username']
                elif type(value) is str:
                    value = value.replace("'", "''")
                elif type(value) is bool:
                    if value:
                        value = 1
                    elif not value:
                        value = 0
                elif type(value) is list:
                    listToJson = ''
                    dict_object = {}
                    for lv in value:
                        for k, v in lv.items():
                            if v is None:
                                dict_object[k] = 'NULL'
                            else:
                                dict_object[k] = v.replace("'", "''")
                        listToJson = "'{}',".format(json.dumps(dict_object, sort_keys=True, indent=2))
                    tmpValues += listToJson
                    continue
                tmpValues += "'{}',".format(value)
        pos = len(tmpColumns)
        strColumns = tmpColumns[0:pos - 1]
        strColumns += ')'
        pos = len(tmpValues)
        strValues = tmpValues[0:pos - 1]
        strValues += ')'
        return strColumns, strValues

    @staticmethod
    def deleteRowsInTableBDUni(tableName, keys) -> None:
        """
        Suppression des enregistrements d'une table BDUni en fonction d'une liste de clés primaires données en entrée.

        :param tableName: nom de la table dont les enregistrements doivent être supprimés
        :type tableName: str

        :param keys: liste par table de clés primaires
        :type keys: list
        """
        if not SQLiteManager.isTableExist(tableName):
            message = "SQLiteManager.deleteRowsInTableBDUni : la table {} de la base SQLite du projet n'existe pas." \
                      " Il faut lancer au moins une extraction de données pour créer celle-ci.".format(tableName)
            raise Exception(message)
        tmp = ''
        for key in keys:
            tmp += '"{0}", '.format(key[0])
        strCleabs = tmp[0:len(tmp) - 2]
        sql = 'DELETE FROM {0} WHERE cleabs IN ({1})'.format(tableName, strCleabs)
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def setActionsInTableBDUni(tableName, itemsTransaction) -> None:
        """
        Supprime les enregistrements d'une table BDUni en fonction des actions (update et delete) de synchronisation.

        :param tableName: nom de la table dont les enregistrements doivent être supprimés
        :type tableName: str

        :param itemsTransaction: contient les items nécessaires à la suppression des enregistrements
        :type itemsTransaction: dict
        """
        if not SQLiteManager.isTableExist(tableName):
            message = "SQLiteManager.setActionsInTableBDUni : la table {} de la base SQLite du projet n'existe pas." \
                      " Il faut lancer au moins une extraction de données pour créer celle-ci.".format(tableName)
            raise Exception(message)
        cleabss = []
        for item in itemsTransaction:
            data = json.loads(item)
            if data['state'] == 'Insert':
                continue
            if data['state'] == 'Update' or data['state'] == 'Delete':
                cleabss.append(data['feature']['cleabs'])
        # Si la transaction ne contient que des créations, il n'y a pas d'enregistrements à détruire
        if len(cleabss) > 0:
            SQLiteManager.deleteRowsInTableBDUni(tableName, cleabss)

    # Insère un ou plusieurs enregistrements dans une table en fonction de la liste des attributs donnée en entrée
    def insertRowsInTable(self, parameters, attributesRows) -> int:
        totalRows = 0
        if len(attributesRows) == 0:
            return totalRows
        wkt = Wkt(parameters)
        # Insertion des lignes dans la table
        connection = spatialite_connect(self.__dbPath)
        cur = connection.cursor()
        for attributesRow in attributesRows:
            columnsValues = self.__setColumnsValuesForInsert(attributesRow, parameters, wkt)
            sql = "INSERT INTO {0} {1} VALUES {2}".format(parameters['tableName'], columnsValues[0], columnsValues[1])
            cur.execute(sql)
            totalRows += 1
        cur.close()
        connection.commit()
        connection.close()
        return totalRows

    @staticmethod
    #
    def selectRowsInTable(layer, ids) -> list:
        """
        Retourne le nom de la clé primaire (et la clé MD5 d'une empreinte numérique de l'objet) pour une table non BDUni
        ou retourne le nom de la clé primaire et la clé MD5 d'une empreinte pour une table BDUni.
        """
        tmp = "("
        for idTmp in ids:
            tmp += "'{}',".format(idTmp)
        pos = len(tmp)
        listId = tmp[0:pos - 1]
        listId += ')'
        result = SQLiteManager.isColumnExist(layer.name(), cst.FINGERPRINT)
        if result[0] == 1:
            sql = "SELECT {0}, {1} FROM {2} WHERE {3} IN {4}".format(layer.idNameForDatabase, cst.FINGERPRINT,
                                                                     layer.name(), cst.ID_SQLITE, listId)
        else:
            sql = "SELECT {0} FROM {1} WHERE {2} IN {3}".format(layer.idNameForDatabase, layer.name(), cst.ID_SQLITE,
                                                                listId)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        connection.close()
        return res

    @staticmethod
    def emptyTable(tableName) -> None:
        """
        Suppression de tous les enregistrements d'une table.

        :param tableName: nom de la table
        :type tableName: str
        """
        if not SQLiteManager.isTableExist(tableName):
            message = "SQLiteManager.emptyTable : la table {} de la base SQLite du projet n'existe pas. Il faut " \
                      "lancer au moins une extraction de données pour créer celle-ci.".format(tableName)
            raise Exception(message)
        sql = u"DELETE FROM {0}".format(tableName)
        SQLiteManager.executeSQL(sql)
        print("SQLiteManager : table {0} vidée".format(tableName))

    @staticmethod
    def deleteTable(tableName) -> None:
        """
        Suppression d'une table dans la base SQLite.

        :param tableName: nom de la table
        :type tableName: str
        """
        if not SQLiteManager.isTableExist(tableName):
            message = "SQLiteManager.deleleTable : la table {} de la base SQLite du projet n'existe pas. Il faut " \
                      "lancer au moins une extraction de données pour créer celle-ci.".format(tableName)
            raise Exception(message)
        sql = u"DROP TABLE {0}".format(tableName)
        SQLiteManager.executeSQL(sql)
        print("SQLiteManager : table {0} détruite".format(tableName))

    @staticmethod
    def isColumnExist(tableName, columnName) -> ():
        """
        :param tableName: nom de la table
        :type tableName: str

        :param columnName: nom de la colonne
        :type columnName: str

        :return: un tuple dont le premier élément est égale à 1 si la colonne existe dans la table
        """
        if not SQLiteManager.isTableExist(tableName):
            message = "SQLiteManager.isColumnExist : la table {} de la base SQLite du projet n'existe pas. Il faut" \
                      " lancer au moins une extraction de données pour créer celle-ci.".format(tableName)
            raise Exception(message)
        sql = u"SELECT COUNT(*) FROM pragma_table_info('{0}') WHERE name='{1}'".format(tableName, columnName)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def selectColumnFromTable(tableName, columnName) -> ():
        """
        :param tableName: nom de la table
        :type tableName: str

        :param columnName: nom de la colonne
        :type columnName: str

        :return: la valeur d'une colonne pour une table donnée.
        """
        if not SQLiteManager.isTableExist(tableName):
            message = "SQLiteManager.selectColumnFromTable : la table {} de la base SQLite du projet n'existe pas." \
                      " Il faut lancer au moins une extraction de données pour créer celle-ci.".format(tableName)
            raise Exception(message)
        sql = u"SELECT {0} FROM {1}".format(columnName, tableName)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def selectColumnFromTableWithCondition(columnName, tableName, conditionColumn, conditionValue) -> ():
        """
        Retourne la valeur d'une colonne selon une condition d'égalité.

        :param columnName: nom de la colonne
        :type columnName: str

        :param tableName: nom de la table
        :type tableName: str

        :param conditionColumn: nom de la colonne faisant partie de la condition
        :type conditionColumn: str

        :param conditionValue: la valeur de la condition d'égalité
        :type conditionValue: str
        """
        if not SQLiteManager.isTableExist(tableName):
            message = "SQLiteManager.selectColumnFromTableWithCondition : la table {} de la base SQLite du projet" \
                      " n'existe pas. Il faut lancer au moins une extraction de données" \
                      " pour créer celle-ci.".format(tableName)
            raise Exception(message)
        sql = u"SELECT {0} FROM {1} WHERE {2} = '{3}'".format(columnName, tableName, conditionColumn, conditionValue)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def vacuumDatabase() -> None:
        """
        Compactage de la base SQLite (indispensable après le chargement d'une nouvelle couche).
        """
        sql = u"VACUUM"
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def updateNumrecTableOfTables(layer, numrec) -> None:
        """
        Met à jour le numéro de synchronisation pour une couche de la table des tables.

        :param layer: nom de la couche
        :type layer: str

        :param numrec: numéro de dernière mise à jour d'une base
        :type numrec: int
        """
        sql = "UPDATE {0} SET numrec = {1} WHERE layer = '{2}'".format(cst.TABLEOFTABLES, numrec, layer)
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def selectLayersFromTableOfTables() -> list:
        """
        :return: l'ensemble des noms de couches stockées dans la table des tables.
        """
        sql = "SELECT layer FROM {0}".format(cst.TABLEOFTABLES)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        connection.close()
        return result

    @staticmethod
    def selectNumrecTableOfTables(layer) -> int:
        """
        :param layer: le nom de la couche
        :type layer: str

        return: le dernier numéro de synchronisation pour une couche BDUni, 0 pour une table standard
        """
        sql = "SELECT numrec FROM {0} where layer = '{1}'".format(cst.TABLEOFTABLES, layer)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        cur.close()
        connection.close()
        return result[0]

    @staticmethod
    #
    def createTableOfTables() -> None:
        """
        Création de la table des tables qui permet de stocker les informations nécessaires en vue d'une synchronisation
        vers le serveur de l'espace collaboratif.
        """
        sql = u"CREATE TABLE IF NOT EXISTS {0} (id INTEGER PRIMARY KEY AUTOINCREMENT, layer TEXT, idName TEXT, " \
              u"standard BOOL, database TEXT, databaseid INTEGER, srid INTEGER, geometryName TEXT, " \
              u"geometryDimension INTEGER, geometryType TEXT, numrec INTEGER, " \
              u"tableid INTEGER)".format(cst.TABLEOFTABLES)
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def InsertIntoTableOfTables(parameters) -> None:
        """
        Insère un enregistrement dans la table des tables. Si l'enregistrement existe déjà, on le détruit
        avant d'insérer le nouveau.

        :param parameters: les clés/valeurs pour une insertion
        :type parameters: dict

        """
        result = SQLiteManager.selectRowsInTableOfTables(parameters['layer'])
        if len(result) == 1:
            sql = "DELETE FROM {0} WHERE layer = '{1}'".format(cst.TABLEOFTABLES, parameters['layer'])
            SQLiteManager.executeSQL(sql)

        columns = ''
        values = ''
        for col, val in parameters.items():
            columns += "'{0}',".format(col)
            if type(val) == int:
                values += "{0},".format(val)
            else:
                values += "'{0}',".format(val)
        posC = len(columns)
        posV = len(values)
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(cst.TABLEOFTABLES, columns[0:posC - 1], values[0:posV - 1])
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def selectRowsInTableOfTables(tableName) -> list:
        """
        Retourne toutes les colonnes de la table des tables pour un enregistrement d'une table.

        :param tableName: le nom de la table
        :type tableName: str
        """
        result = []
        # Est-ce que la table existe ?
        if not SQLiteManager.isTableExist(cst.TABLEOFTABLES):
            return result

        sql = "SELECT * FROM {0} WHERE layer = '{1}'".format(cst.TABLEOFTABLES, tableName)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        connection.close()
        return result

    @staticmethod
    def createReportTable() -> None:
        """
        Création de la table des signalements.
        """
        sql = u"CREATE TABLE Signalement (" + \
              u"id INTEGER NOT NULL PRIMARY KEY, " + \
              u"NoSignalement INTEGER, " + \
              u"Auteur TEXT, " + \
              u"Commune TEXT, " + \
              u"Insee TEXT, " + \
              u"Département TEXT, " + \
              u"Département_id TEXT, " + \
              u"Date_création TEXT, " + \
              u"Date_MAJ TEXT, " + \
              u"Date_validation TEXT, " + \
              u"Thèmes TEXT, " + \
              u"Statut TEXT, " + \
              u"Message TEXT, " + \
              u"Réponses TEXT, " + \
              u"URL TEXT, " + \
              u"URL_privé TEXT, " + \
              u"Document TEXT, " + \
              u"Autorisation TEXT)"
        SQLiteManager.executeSQL(sql)
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('Signalement', 'geom', " + str(cst.EPSGCRS4326) + ", 'POINT', 'XY')"
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def createSketchTable(nameTable, geometryType) -> None:
        """
        Création d'une table de croquis.

        :param nameTable: nom de la table du croquis
        :type nameTable: str

        :param geometryType: le type de géométrie du croquis
        :type geometryType: str
        """
        sql = u"CREATE TABLE " + nameTable + " (" + \
              u"id INTEGER NOT NULL PRIMARY KEY, " + \
              u"NoSignalement INTEGER, " + \
              u"Nom TEXT, " + \
              u"Attributs_croquis, " + \
              u"Lien_objet_BDUNI TEXT) "
        SQLiteManager.executeSQL(sql)
        # creating a POINT or LINE or POLYGON Geometry column
        sql = "SELECT AddGeometryColumn('" + nameTable + "',"
        sql += "'geom', " + str(cst.EPSGCRS4326) + ", '" + geometryType + "', 'XY')"
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def setEmptyTablesReportAndSketchs(tablesList) -> None:
        """
        Suppression de tous les enregistrements de toutes les tables d'une liste. (Signalement, Croquis_EC_Polygone,
        Croquis_EC_Ligne et Croquis_EC_Point.
        """
        for table in tablesList:
            SQLiteManager.emptyTable(table)
        SQLiteManager.vacuumDatabase()

    @staticmethod
    def updateTable(parameters) -> None:
        """
        Met à jour un enregistrement d'une table en fonction d'une condition.

        :param parameters: les items ('name', 'attributes', 'condition') nécessaires pour la mise à jour d'une table
        :type parameters: dict
        """
        sql = "UPDATE {0} SET {1} WHERE {2}".format(parameters['name'], parameters['attributes'],
                                                    parameters['condition'])
        SQLiteManager.executeSQL(sql)
