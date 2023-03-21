import ntpath
import json

from qgis.utils import spatialite_connect
from qgis.core import QgsProject, QgsGeometry
from . import ConstanteRipart as cst
from .Wkt import Wkt


class SQLiteManager(object):
    dbPath = ""
    tableAttributes = None
    is3D = None
    geometryType = None

    def __init__(self):
        self.dbPath = SQLiteManager.getBaseSqlitePath()

    @staticmethod
    def getBaseSqlitePath():
        projectDir = QgsProject.instance().homePath()
        fname = ntpath.basename(QgsProject.instance().fileName())
        projectFileName = fname[:fname.find(".")]
        dbName = projectFileName + "_espaceco"
        dbPath = projectDir + "/" + dbName + ".sqlite"
        return dbPath

    @staticmethod
    def executeSQL(sql):
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        cur.close()
        connection.commit()
        connection.close()

    @staticmethod
    def isTableExist(tableName):
        bFind = True
        dbPath = SQLiteManager.getBaseSqlitePath()
        # si la base SQLite n'existe pas, dbPath contient '/_espaceco.sqlite'
        # Par exemple un projet vierge dans lequel on ajoute une couche
        if dbPath == '/_espaceco.sqlite':
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

    def setAttributesTableToSql(self, geometryName, layer):
        columnDetruitExist = False
        typeGeometrie = ''
        # sqlAttributes = "{0} INTEGER PRIMARY KEY AUTOINCREMENT,".format(cst.ID_SQLITE)
        sqlAttributes = ""
        for value in self.tableAttributes.values():
            if self.setSwitchType(value['type']) == '':
                return "", "", ""
            if value['name'] == "detruit":
                columnDetruitExist = True
                sqlAttributes += "{0} {1},".format(value['name'], self.setSwitchType(value['type']))
            elif value['name'] == geometryName:
                typeGeometrie = self.setSwitchType(value['type'])
            # au cas où il y aurait déjà un attribut nommé id_sqlite
            elif value['name'] == cst.ID_SQLITE:
                sqlAttributes += "{0} {1},".format(cst.ID_ORIGINAL, self.setSwitchType(value['type']))
            # TODO Noémie : 29/7/22 Arnaud m'a indiqué que gcms_fingerprint et gcms_numrec ne doivent pas apparaitre
            # TODO comme attributs cachés vis à vis de l'extérieur, cf les urls suivantes
            # TODO (BIEN) https://qlf-collaboratif.ign.fr/collaboratif-3.4/gcms/database/bduni_recette_test/feature-type/equipement_de_transport.json
            # TODO (PAS BIEN) https://espacecollaboratif.ign.fr/gcms/database/bduni_interne_qualif_fxx/feature-type/equipement_de_transport.json
            elif value['name'] == cst.FINGERPRINT or value['name'] == cst.NUMREC:
                continue
            else:
                sqlAttributes += "{0} {1},".format(value['name'], self.setSwitchType(value['type']))
        # Anomalie 17196, l'identifiant ID_SQLITE et FINGERPRINT sont positionnés en dernier dans le formulaire
        sqlAttributes += "{0} INTEGER PRIMARY KEY AUTOINCREMENT,".format(cst.ID_SQLITE)
        if not layer.isStandard:
            sqlAttributes += "{0} TEXT".format(cst.FINGERPRINT)
        # ordre d'insertion geometrie, gcms_fingerprint
        self.geometryType = typeGeometrie
        return sqlAttributes, typeGeometrie, columnDetruitExist

    def addGeometryColumn(self, parameters):
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

    def createTableFromLayer(self, layer, tableStructure):
        # Stockage du nom du champ contenant la géométrie
        geometryName = tableStructure['geometryName']
        self.is3D = tableStructure['attributes'][geometryName]['is3d']
        # La structure de la table à créer
        self.tableAttributes = tableStructure['attributes']
        t = self.setAttributesTableToSql(geometryName, layer)
        if t[0] == "" and t[1] == "" and t[2] == "":
            raise Exception("Création d'une table dans SQLite impossible, un type de colonne est inconnu")

        connection = spatialite_connect(self.dbPath)
        sql = u"CREATE TABLE {0} (".format(layer.nom)
        sql += t[0]
        sql += ')'
        cur = connection.cursor()
        print(sql)
        cur.execute(sql)
        '''sqlSpatial = 'SELECT InitSpatialMetaData()'
        print(sqlSpatial)
        cur.execute(sqlSpatial)'''
        parameters_geometry_column = {'tableName': layer.nom, 'geometryName': tableStructure['geometryName'],
                                      'crs': cst.EPSGCRS, 'geometryType': self.geometryType, 'is3D': self.is3D}
        sqlGeometryColumn = self.addGeometryColumn(parameters_geometry_column)
        print(sqlGeometryColumn)
        cur.execute(sqlGeometryColumn)
        if len(cur.fetchall()) == 0:
            print("SQLiteManager : création de la table {0} réussie".format(layer.nom))
        cur.close()
        connection.commit()
        connection.close()
        # compactage de la base
        SQLiteManager.vacuumDatabase()
        # retourne True si la colonne detruit existe dans la table
        return t[2]

    def setSwitchType(self, vType):
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

    def setColumnsValuesForInsertWithSpatialFilter(self, attributesRow, parameters, bboxWorkingArea, wkt):
        tmpColumns = '('
        tmpValues = '('
        for column, value in attributesRow.items():
            if column == parameters['geometryName']:
                # si la géometrie n'est pas dans la zone de travail alors on renvoie un tuple avec du vide
                geom = QgsGeometry.fromWkt(value)
                newGeom = wkt.transformGeometry(geom)
                if not wkt.isGeometryObjectIntersectSpatialFilter(bboxWorkingArea, newGeom):
                    return "", ""
                tmpColumns += '{0},'.format(column)
                tmpValues += wkt.toGetGeometry(value)
                continue
            elif column == cst.ID_SQLITE:
                tmpColumns += '{0},'.format(cst.ID_ORIGINAL)
            else:
                tmpColumns += '{0},'.format(column)
            if value is None:
                tmpValues += "'',"
            else:
                if type(value) == str:
                    value = value.replace("'", "''")
                if type(value) == list:
                    listToJson = ''
                    dict_object = {}
                    for lv in value:
                        for k, v in lv.items():
                            if v is None:
                                dict_object[k] = v
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
        # sinon on renvoie un tuple contenant l'ensemble des colonnes et valeurs pour l'insertion dans la table
        return strColumns, strValues

    def setColumnsValuesForInsert(self, attributesRow, parameters, wkt):
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
                tmpColumns += '{0},'.format(column)

            if value is None:
                tmpValues += "'NULL',"
            else:
                if type(value) == str:
                    value = value.replace("'", "''")
                if type(value) == bool:
                    if value:
                        value = 1
                    elif not value:
                        value = 0
                if type(value) == list:
                    listToJson = ''
                    dict_object = {}
                    for lv in value:
                        for k, v in lv.items():
                            if v is None:
                                dict_object[k] = v
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
    def deleteRowsInTableBDUni(tableName, keys):
        tmp = ''
        for key in keys:
            tmp += '"{0}", '.format(key[0])
        strCleabs = tmp[0:len(tmp) - 2]
        sql = 'DELETE FROM {0} WHERE cleabs IN ({1})'.format(tableName, strCleabs)
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def setActionsInTableBDUni(tableName, itemsTransaction):
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

    # Non utilisé et pas mis à jour
    # def insertRowsInTableWithSpatialFilter(self, parameters, attributesRows, bboxWorkingArea):
    #     totalRows = 0
    #     if len(attributesRows) == 0:
    #         return totalRows
    #     wkt = Wkt(parameters)
    #     # Insertion des lignes dans la table
    #     connection = spatialite_connect(self.dbPath)
    #     cur = connection.cursor()
    #     for attributesRow in attributesRows:
    #         columnsValues = self.setColumnsValuesForInsertWithSpatialFilter(attributesRow, parameters, bboxWorkingArea, wkt)
    #         # si le tuple est vide alors l'objet est en dehors de la zone de travail
    #         if columnsValues[0] == '' and columnsValues[1] == '':
    #             continue
    #         sql = "INSERT INTO {0} {1} VALUES {2}".format(parameters['tableName'], columnsValues[0], columnsValues[1])
    #         cur.execute(sql)
    #         totalRows += 1
    #     cur.close()
    #     connection.commit()
    #     connection.close()
    #     return totalRows

    def insertRowsInTable(self, parameters, attributesRows):
        totalRows = 0
        if len(attributesRows) == 0:
            return totalRows
        wkt = Wkt(parameters)
        # Insertion des lignes dans la table
        connection = spatialite_connect(self.dbPath)
        cur = connection.cursor()
        for attributesRow in attributesRows:
            columnsValues = self.setColumnsValuesForInsert(attributesRow, parameters, wkt)
            sql = "INSERT INTO {0} {1} VALUES {2}".format(parameters['tableName'], columnsValues[0], columnsValues[1])
            cur.execute(sql)
            totalRows += 1
        cur.close()
        connection.commit()
        connection.close()
        return totalRows

    @staticmethod
    def selectRowsInTable(layer, ids):
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
        result = cur.fetchall()
        cur.close()
        connection.close()
        return result

    @staticmethod
    def emptyTable(tableName):
        sql = u"DELETE FROM {0}".format(tableName)
        SQLiteManager.executeSQL(sql)
        print("SQLiteManager : table {0} vidée".format(tableName))

    @staticmethod
    def deleteTable(tableName):
        sql = u"DROP TABLE {0}".format(tableName)
        SQLiteManager.executeSQL(sql)
        print("SQLiteManager : table {0} détruite".format(tableName))

    @staticmethod
    def isColumnExist(tableName, columnName):
        sql = u"SELECT COUNT(*) FROM pragma_table_info('{0}') WHERE name='{1}'".format(tableName, columnName)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def selectColumnFromTable(tableName, columnName):
        sql = u"SELECT {0} FROM {1}".format(columnName, tableName)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def selectColumnFromTableWithCondition(tableName, columnName, key):
        sql = u"SELECT {0} FROM {1} WHERE {2} = '{3}'".format(columnName, tableName, columnName, key)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    # Indispensable après le chargement d'une nouvelle couche
    @staticmethod
    def vacuumDatabase():
        sql = u"VACUUM"
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def updateNumrecTableOfTables(layer, numrec):
        sql = "UPDATE {0} SET numrec = {1} WHERE layer = '{2}'".format(cst.TABLEOFTABLES, numrec, layer)
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def selectLayersFromTableOfTables():
        sql = "SELECT layer FROM {0}".format(cst.TABLEOFTABLES)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        connection.close()
        return result

    @staticmethod
    def selectNumrecTableOfTables(layer):
        sql = "SELECT numrec FROM {0} where layer = '{1}'".format(cst.TABLEOFTABLES, layer)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        cur.close()
        connection.close()
        return result[0]

    @staticmethod
    def createTableOfTables():
        sql = u"CREATE TABLE IF NOT EXISTS {0} (id INTEGER PRIMARY KEY AUTOINCREMENT, layer TEXT, idName TEXT, " \
              u"standard INTEGER, database TEXT, srid INTEGER, geometryName TEXT, geometryDimension INTEGER, " \
              u"geometryType TEXT, numrec INTEGER)".format(cst.TABLEOFTABLES)
        SQLiteManager.executeSQL(sql)

    @staticmethod
    def InsertIntoTableOfTables(parameters):
        # TODO
        # Si l'enregistrement existe déjà, on sort ou on update ?
        result = SQLiteManager.selectRowsInTableOfTables(parameters['layer'])
        if len(result) == 1:
            return

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
    def selectRowsInTableOfTables(tableName):
        result = None
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
