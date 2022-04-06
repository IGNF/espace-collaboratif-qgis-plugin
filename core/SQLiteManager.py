import ntpath

from qgis.utils import spatialite_connect
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
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
    def isTableExist(tableName):
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        sql = u"SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(tableName)
        cur = connection.cursor()
        cur.execute(sql)
        if cur.fetchone() is None:
            return False
        return True

    def setAttributesTableToSql(self, geometryName):
        columnDetruitExist = False
        typeGeometrie = ''
        sqlAttributes = "{0} INTEGER PRIMARY KEY AUTOINCREMENT,".format(cst.ID_SQLITE)
        for value in self.tableAttributes.values():
            if self.setSwitchType(value['type']) == '':
                return "", "", ""
            if value['name'] == "detruit":
                columnDetruitExist = True
                sqlAttributes += "{0} {1},".format(value['name'], self.setSwitchType(value['type']))
            elif value['name'] == geometryName:
                typeGeometrie = self.setSwitchType(value['type'])
            elif value['name'] == cst.ID_SQLITE: # au cas où il y aurait déjà un attribut nommé id_sqlite
                sqlAttributes += "{0} {1},".format(cst.ID_ORIGINAL, self.setSwitchType(value['type']))
            else:
                sqlAttributes += "{0} {1},".format(value['name'], self.setSwitchType(value['type']))
        # il faut ajouter une colonne "is_fingerprint" qui indiquera si c'est une table BDUni qui contient gcms_fingerprint
        sqlAttributes += "{0} INTEGER".format(cst.IS_FINGERPRINT)
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
        t = self.setAttributesTableToSql(geometryName)
        if t[0] == "" and t[1] == "" and t[2] == "":
            raise Exception("Création d'une table dans SQLite impossible, un type de colonne est inconnu")

        connection = spatialite_connect(self.dbPath)
        sql = u"CREATE TABLE {0} (".format(layer.nom)
        sql += t[0]
        sql += ')'
        #print(sql)
        cur = connection.cursor()
        cur.execute(sql)
        parameters_geometry_column = {}
        parameters_geometry_column['tableName'] = layer.nom
        parameters_geometry_column['geometryName'] = tableStructure['geometryName']
        parameters_geometry_column['crs'] = cst.EPSGCRS
        parameters_geometry_column['geometryType'] = self.geometryType
        parameters_geometry_column['is3D'] = self.is3D
        sqlGeometryColumn = self.addGeometryColumn(parameters_geometry_column)
        cur.execute(sqlGeometryColumn)
        if len(cur.fetchall()) == 0:
            print("SQLiteManager : création de la table {0} réussie".format(layer.nom))
        cur.close()
        connection.commit()
        connection.close()
        # compactage de la base
        self.vacuumDatabase()
        #retourne True si la colonne detruit existe dans la table
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

    def setColumnsValuesForInsert(self, attributesRow, parameters):
        tmpColumns = '('
        tmpValues = '('
        wkt = Wkt(parameters)
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
                tmpValues += "'',"
            else:
                if type(value) == str:
                    value = value.replace("'", "''")
                if type(value) == list:
                    tmpValues += '"{}",'.format(value)
                    continue
                    # pour l'attribut like de type str mais json
                #tmpValues += '"{}",'.format(value)
                tmpValues += "'{}',".format(value)
        # si la table sqlite contient :
        # la colonne gcms_fingerprint
        # et "isTableStandard" est à False
        # alors la colonne 'is_fingerprint' est remplie à 1
        # dans les autres cas à 0
        tmpColumns += '{0})'.format(cst.IS_FINGERPRINT)
        if parameters['isStandard']:
            tmpValues += "'0')"
        else:
            tmpValues += "'1')"
        return tmpColumns, tmpValues

    def insertRowsInTable(self, parameters, attributesRows):
        totalRows = 0
        if len(attributesRows) == 0:
            print("Pas de données pour la table {0}".format(parameters['tableName']))
            return totalRows

        connection = spatialite_connect(self.dbPath)
        cur = connection.cursor()
        # Insertion des lignes dans la table
        for attributesRow in attributesRows:
            columnsValues = self.setColumnsValuesForInsert(attributesRow, parameters)
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
        listId = tmp[0:pos-1]
        listId += ')'
        result = SQLiteManager.isColumnExist(layer.name(), cst.FINGERPRINT)
        if result[0] == 1:
            sql = "SELECT {0}, {1} FROM {2} WHERE {3} IN {4}".format(layer.idNameForDatabase, cst.FINGERPRINT, layer.name(), cst.ID_SQLITE, listId)
        else:
            sql = "SELECT {0} FROM {1} WHERE {2} IN {3}".format(layer.idNameForDatabase, layer.name(), cst.ID_SQLITE, listId)
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        connection.close()
        return result

    def emptyTable(self, tableName):
        connection = spatialite_connect(self.dbPath)
        cursor = connection.cursor()
        sql = u"DELETE FROM {0}".format(tableName)
        cursor.execute(sql)
        sql = u"SELECT count(*) FROM {0}".format(tableName)
        cursor.execute(sql)
        if len(cursor.fetchall()) == 0:
            print("SQLiteManager : table {0} vidée".format(tableName))
        cursor.close()
        connection.close()

    def deleteTable(self, tableName):
        connection = spatialite_connect(self.dbPath)
        cursor = connection.cursor()
        sql = u"DROP TABLE {0}".format(tableName)
        cursor.execute(sql)
        print("SQLiteManager : table {0} détruite".format(tableName))
        cursor.close()
        connection.close()

    @staticmethod
    def isColumnExist(tableName, columnName):
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cursor = connection.cursor()
        sql = u"SELECT COUNT(*) FROM pragma_table_info('{0}') WHERE name='{1}'".format(tableName, columnName)
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    # Indispensable après le chargement d'une nouvelle couche
    def vacuumDatabase(self):
        connection = spatialite_connect(self.dbPath)
        cursor = connection.cursor()
        sql = u"VACUUM"
        cursor.execute(sql)
        cursor.close()
        connection.close()

    @staticmethod
    def createTableOfTables():
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        sql = u"CREATE TABLE IF NOT EXISTS {0} (id INTEGER PRIMARY KEY AUTOINCREMENT, layer TEXT, idName TEXT, " \
              u"standard INTEGER, database TEXT, srid INTEGER, geometryName TEXT, geometryDimension INTEGER, " \
              u"geometryType TEXT)".format(cst.TABLEOFTABLES)
        cur.execute(sql)
        cur.close()
        connection.close()

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
        sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(cst.TABLEOFTABLES, columns[0:posC-1], values[0:posV-1])
        print(sql)

        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        cur.execute(sql)
        cur.close()
        connection.commit()
        connection.close()

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
