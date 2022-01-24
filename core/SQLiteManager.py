import ntpath

from qgis.utils import spatialite_connect
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from . import ConstanteRipart as cst


class SQLiteManager(object):
    dbPath = ""
    tableAttributes = None
    is3D = None
    geometryType = None
    geometryName = None

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

    def isTableExist(self, tableName):
        connection = spatialite_connect(self.dbPath)
        sql = u"SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(tableName)
        cur = connection.cursor()
        cur.execute(sql)
        if cur.fetchone() is None:
            return False
        return True

    def setAttributesTableToSql(self, geometryName):
        columnDetruitExist = False
        typeGeometrie = ''
        #tester si la variable id n'existe pas dans tableAttributes
        sqlAttributes = "{0} INTEGER PRIMARY KEY AUTOINCREMENT,".format(cst.ID_SQLITE)
        for value in self.tableAttributes.values():
            if value['name'] == "detruit":
                columnDetruitExist = True
                sqlAttributes += "{0} {1},".format(value['name'], self.setSwitchType(value['type']))
            elif value['name'] == geometryName:
                typeGeometrie = self.setSwitchType(value['type'])
            elif value['name'] == cst.ID_SQLITE: # au cas où il y aurait déjà un attribut nommé id_sqlite
                sqlAttributes += "{0} {1},".format(cst.ID_ORIGINAL, self.setSwitchType(value['type']))
            else:
                sqlAttributes += "{0} {1},".format(value['name'], self.setSwitchType(value['type']))
        # que devient gcms_fingerprint dans la table zone_d_activite_ou_d_interet ?
        # ordre d'insertion geometrie,gcms_fingerprint
        self.geometryType = typeGeometrie
        return sqlAttributes, typeGeometrie, columnDetruitExist

    def setAddGeometryColumn(self, parameters, firstRow):
        # On détermine si les coordonnées de la géométrie de la 1ère ligne sont en 2D ou 3D
        for column, value in firstRow.items():
            # si la couche est en visualisation, la table sqlite ne contient pas la colonne gcms_fingerprint
            if column != parameters['geometryName']:
                continue
            coordinates = value.split(',')
            xyz = coordinates[0].lstrip().split(' ')
            if len(xyz) == 3:
                self.is3D = True
            else:
                self.is3D = False

        if not self.is3D:
            # Paramétrage de la colonne géométrie en 2D par défaut
            sql = "SELECT AddGeometryColumn('{0}', '{1}', {2}, '{3}', 'XY')".format(parameters['tableName'],
                                                                                    parameters['geometryName'],
                                                                                    parameters['crs'],
                                                                                    parameters['geometryType'])
        else:
            sql = "SELECT AddGeometryColumn('{0}', '{1}', {2}, '{3}', 'XYZ')".format(parameters['tableName'],
                                                                                     parameters['geometryName'],
                                                                                     parameters['crs'],
                                                                                     parameters['geometryType'])
        return sql

    def createTableFromLayer(self, tableName, tableStructure):
        # Stockage du nom du champ contenant la géométrie
        self.geometryName = tableStructure['geometryName']

        # La structure de la table à créer
        self.tableAttributes = tableStructure['attributes']
        t = self.setAttributesTableToSql(tableStructure['geometryName'])
        connection = spatialite_connect(self.dbPath)
        tmp = u"CREATE TABLE {0} (".format(tableName)
        tmp += t[0]
        pos = len(tmp)
        sql = tmp[0:pos - 1]
        sql += ')'
        cur = connection.cursor()
        cur.execute(sql)

        if len(cur.fetchall()) == 0:
            print("SQLiteManager : création de la table {0} réussie".format(tableName))
        cur.close()
        connection.commit()
        connection.close()
        #retourne True si la colonne detruit existe dans la table
        return t[2]

    def setSwitchType(self, vType):
        if vType == 'Boolean':
            return 'INTEGER'
        elif vType == 'DateTime':
            return 'TEXT'
        elif vType == 'Date':
            return 'TEXT'
        elif vType == 'Double':
            return 'REAL'
        elif vType == 'Integer':
            return 'INTEGER'
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
        elif vType == 'Document':
            return 'TEXT'
        else:
            return ''


    def getTransformer(sridSource, sridTarget):
        crsSource = QgsCoordinateReferenceSystem(sridSource)
        crsTarget = QgsCoordinateReferenceSystem(sridTarget)
        return QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())

    @staticmethod
    def setOpenBracket(value, pos, is3D):
        ch = value[0:pos]
        if 'MULTIPOLYGON' in value or 'POLYGON' in value:
            if is3D:
                ch += " Z(("
            else:
                ch += " (("
        else:
            if is3D:
                ch += " Z("
            else:
                ch += "("
        return ch

    @staticmethod
    def setCloseBracket(value, res):
        pos = res.rfind(',')
        if 'MULTIPOLYGON' in value:
            ch = "{0})))".format(res[0:pos])
        elif 'MULTILINESTRING' in value or "POLYGON" in value:
            ch = "{0}))".format(res[0:pos])
        else:
            #ch = "{0})".format(res[0:len(res) - 3])
            ch = "{0})".format(res[0:pos])
        return ch

    @staticmethod
    def setMultiGeomFromText(value, transformer, sridProject, is3D):
        pos = value.find('(')
        res = SQLiteManager.setOpenBracket(value, pos, is3D)
        erase = 0
        if 'MULTILINESTRING' in value:
            erase = 1
        elif 'MULTIPOLYGON' in value:
            erase = 2
        tmpValue = value[pos + erase:len(value) - erase]
        if erase == 2:
            tmps = tmpValue.split('),(')
        else:
            tmps = tmpValue.split('),')
        for tmp in tmps:
            if erase == 1 or erase == 2:
                res += '('
            coordinates = tmp.split(',')
            for coordinate in coordinates:
                closeBracket = False
                xyz = coordinate.lstrip().split(' ')
                X = xyz[0]
                posX = xyz[0].find('(')
                if posX != -1:
                    X = xyz[0][posX + 1:len(xyz[0])]
                Y = xyz[1]
                posY = xyz[1].find(')')
                if posY != -1:
                    Y = xyz[1][0:posY]
                pt = transformer.transform(float(X), float(Y))
                if is3D:
                    if closeBracket:
                        res += "{0} {1} {2}), ".format(str(pt.x()), str(pt.y()), xyz[2])
                    else:
                        res += "{0} {1} {2}, ".format(str(pt.x()), str(pt.y()), xyz[2])
                else:
                    if closeBracket:
                        res += "{0} {1}), ".format(str(pt.x()), str(pt.y()))
                    else:
                        res += "{0} {1}, ".format(str(pt.x()), str(pt.y()))
            if not closeBracket:
                ch = res[0:len(res) - 2]
                res = ch + '),'
            coordinates.clear()
        geom = SQLiteManager.setCloseBracket(value, res)
        return geom
        #return "GeomFromText('{0}', {1})".format(geom, sridProject)

    @staticmethod
    def setGeomFromText(value, transformer, sridProject, is3D):
        pos = value.find('(')
        res = SQLiteManager.setOpenBracket(value, pos, is3D)
        tmp = value[pos + 1:len(value) - 1]
        coordinates = tmp.split(',')
        for coordinate in coordinates:
            xyz = coordinate.lstrip().split(' ')
            posX = xyz[0].find('(')
            x = xyz[0]
            y = xyz[1]
            if posX != -1:
                x = xyz[0][posX + 1:len(xyz[0])]
            posY = xyz[1].find(')')
            if posY != -1:
                y = xyz[1][0:posY]
            pt = transformer.transform(float(x), float(y))
            if is3D:
                res += "{0} {1} {2}, ".format(str(pt.x()), str(pt.y()), xyz[2])
            else:
                res += "{0} {1}, ".format(str(pt.x()), str(pt.y()))
        geom = SQLiteManager.setCloseBracket(value, res)

        # Patch
        if geom.startswith('LineStringZ  Z'):
            geom = geom.replace('LineStringZ  Z', 'LineStringZ')

        return geom
        #return "GeomFromText('{0}', {1})".format(geom, sridProject)

    # @staticmethod
    # def formatAndTransformGeometry(value, parameters):
    #     transformer = SQLiteManager.getTransformer(parameters['sridLayer'], parameters['sridProject'])
    #     if 'MULTI' in value:
    #         if not parameters['is3d']:
    #             geomFromText = SQLiteManager.setMultiGeomFromText(value, transformer, parameters['sridProject'], False)
    #         else:
    #             geomFromText = SQLiteManager.setMultiGeomFromText(value, transformer, parameters['sridProject'], True)
    #     else:
    #         if not parameters['is3d']:
    #             geomFromText = SQLiteManager.setGeomFromText(value, transformer, parameters['sridProject'], False)
    #         else:
    #             geomFromText = SQLiteManager.setGeomFromText(value, transformer, parameters['sridProject'], True)
    #     return geomFromText

    @staticmethod
    def formatAndTransformGeometry(value, source_crs, destination_crs, is3d):
        transformer = SQLiteManager.getTransformer(source_crs, destination_crs)
        if 'MULTI' in value:
            if not is3d:
                geomFromText = SQLiteManager.setMultiGeomFromText(value, transformer, destination_crs, False)
            else:
                geomFromText = SQLiteManager.setMultiGeomFromText(value, transformer, destination_crs, True)
        else:
            if not is3d:
                geomFromText = SQLiteManager.setGeomFromText(value, transformer, destination_crs, False)
            else:
                geomFromText = SQLiteManager.setGeomFromText(value, transformer, destination_crs, True)
        return geomFromText


    def setColumnsValuesForInsert(self, attributesRow, parameters):
        tmpColumns = '('
        tmpValues = '('
        for column, value in attributesRow.items():
            # si la couche est en visualisation, la table sqlite ne contient pas la colonne gcms_fingerprint
            if column == 'gcms_fingerprint' and (parameters['role'] == 'visu' or parameters['role'] == 'ref'):
                continue
            elif column == parameters['geometryName']:
                tmpColumns += '{0},'.format(column)
                #geomFromTextTmp = SQLiteManager.formatAndTransformGeometry(value, parameters['sridLayer'], parameters['sridProject'], parameters['is3d'])
                geomFromTextTmp = self.formatAndTransformGeometry(value, parameters['sridLayer'],
                                                                           parameters['sridProject'],
                                                                           self.is3D)
                tmpValues += "GeomFromText('{0}', {1}),".format(geomFromTextTmp, parameters['sridProject'])
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
                tmpValues += "'{}',".format(value)
        pos = len(tmpColumns)
        strColumns = tmpColumns[0:pos - 1]
        strColumns += ')'
        pos = len(tmpValues)
        strValues = tmpValues[0:pos - 1]
        strValues += ')'
        return strColumns, strValues


    def insertRowsInTable(self, parameters, attributesRows):
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        total = 0

        # Ajout de la colonne géométrie à la table en fonction de la dimension des coordonnées du 1er objet rencontré
        parameters_geometry_column = {}
        parameters_geometry_column['tableName'] = parameters['tableName']
        parameters_geometry_column['geometryName'] = parameters['geometryName']
        parameters_geometry_column['crs'] = cst.EPSGCRS
        parameters_geometry_column['geometryType'] = self.geometryType

        sqlGeometryColumn = self.setAddGeometryColumn(parameters_geometry_column, attributesRows[0])
        cur.execute(sqlGeometryColumn)

        # Insertion des lignes dans la table
        for attributesRow in attributesRows:
            columnsValues = self.setColumnsValuesForInsert(attributesRow, parameters)
            sql = "INSERT INTO {0} {1} VALUES {2}".format(parameters['tableName'], columnsValues[0], columnsValues[1])
            cur.execute(sql)
            total += 1
        print("SQLiteManager : {0} enregistrements pour la table {1}".format(total, parameters['tableName']))
        cur.close()
        connection.commit()
        connection.close()

    @staticmethod
    def selectRowsInTable(tableName, ids):
        tmp = "("
        for id in ids:
            tmp += "'{}',".format(id)
        pos = len(tmp)
        listId = tmp[0:pos-1]
        listId += ')'
        connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
        cur = connection.cursor()
        sql = "SELECT cleabs, gcms_fingerprint FROM {0} WHERE {1} IN {2}".format(tableName, cst.ID_SQLITE, listId)
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
        connection.commit()

    def deleteTable(self, tableName):
        connection = spatialite_connect(self.dbPath)
        cursor = connection.cursor()
        sql = u"DROP TABLE {0}".format(tableName)
        cursor.execute(sql)
        print("SQLiteManager : table {0} détruite".format(tableName))
        cursor.close()
        connection.commit()
