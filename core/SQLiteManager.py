import ntpath

from qgis.core import QgsProject
from qgis.utils import spatialite_connect


class SQLiteManager(object):

    projectInstance = None
    dbPath = ""

    def __init__(self):
        self.projectInstance = QgsProject.instance()
        self.dbPath = SQLiteManager.getBaseSqlitePath()

    @staticmethod
    def getBaseSqlitePath():
        projectDir = QgsProject.instance().homePath()
        fname = ntpath.basename(QgsProject.instance().fileName())
        projectFileName = fname[:fname.find(".")]
        dbName = projectFileName + "_espaceco"
        dbPath = projectDir + "/" + dbName + ".sqlite"
        return dbPath

    def createTableFromLayerIfNotExist(self, nameTable):
        try:
            connection = spatialite_connect(self.dbPath)
            sql = u"SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(nameTable)
            cur = connection.cursor()
            cur.execute(sql)
            if cur.fetchone() is None:
                # Création de la table si elle n'existe pas
                self.createTableFromLayer(connection, nameTable)
            # Si elle existe, il faut la vider
            self.emptyTable(connection, nameTable)

        finally:
            cur.close()
            connection.close()

    def createTableFromLayer(self, connection, nameTable):
        try:
            sql = u"CREATE TABLE {0} (id TEXT, cleabs TEXT, fingerprint TEXT)".format(nameTable)
            cur = connection.cursor()
            cur.execute(sql)
            rowcount = cur.rowcount
            if rowcount == 1:
                print("SQLiteManager : création de la table {0} réussie".format(nameTable))
            connection.commit()
        finally:
            cur.close()
            connection.close()

    def insertRowInTable(self, connection, nameTable, id, cleabs, fingerprint):
        try:
            sql = u"INSERT INTO " + nameTable
            sql += u" (id, cleabs, fingerprint) VALUES (" + id + cleabs + fingerprint + ")"
            cur = connection.cursor()
            cur.execute(sql)
            rowcount = cur.rowcount
            if rowcount:
                print("SQLiteManager : {0} enregistrements pour la table {1}".format(rowcount, nameTable))
            connection.commit()
        finally:
            cur.close()
            connection.close()

    def insertRowsInTable(self, correspondence, nameTable):
        try:
            connection = spatialite_connect(self.dbPath)
            cur = connection.cursor()
            sql = "INSERT INTO {} VALUES (?, ?, ?)".format(nameTable)
            cur.executemany(sql, correspondence)
            rowcount = cur.rowcount
            if rowcount:
                print("SQLiteManager : {0} enregistrements pour la table {1}".format(rowcount, nameTable))
            connection.commit()
        finally:
            cur.close()
            connection.close()

    @staticmethod
    def selectRowsInTable(nameTable, ids):
        try:
            tmp = "("
            for id in ids:
                tmp += "'{}',".format(id)
            pos = len(tmp)
            listId = tmp[0:pos-1]
            listId += ')'
            connection = spatialite_connect(SQLiteManager.getBaseSqlitePath())
            cur = connection.cursor()
            sql = "SELECT cleabs, fingerprint FROM {0} WHERE id IN {1}".format(nameTable, listId)
            cur.execute(sql)
            result = cur.fetchall()
            print(result)
            return result
        finally:
            cur.close()
            connection.close()

    def selectRowInTable(self, nameTable, id):
        try:
            connection = spatialite_connect(self.dbPath)
            cur = connection.cursor()
            sql = "SELECT cleabs, fingerprint FROM {0} WHERE id = '{1}'".format(nameTable, id)
            cur.execute(sql)
            result = cur.fetchone()
            print(result)
            return result
        finally:
            cur.close()
            connection.close()

    def emptyTable(self, connection, nameTable):
        cursor = connection.cursor()
        try:
            sql = u"DELETE FROM {0}".format(nameTable)
            cursor.execute(sql)
            sql = u"SELECT count(*) FROM {0}".format(nameTable)
            cursor.execute(sql)
            rowcount = cursor.rowcount
            if rowcount == -1:
                print("SQLiteManager : table {0} vidée".format(nameTable))
        finally:
            cursor.close()
