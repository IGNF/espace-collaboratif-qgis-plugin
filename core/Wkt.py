from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsWkbTypes,\
    QgsPoint, QgsAbstractGeometry


class Wkt(object):
    sridSource = None
    sridTarget = None
    geometryName = None
    geometryType = None
    crsTransform = None

    def __init__(self, parameters):
        self.sridSource = parameters['sridSource']
        self.sridTarget = parameters['sridTarget']
        self.geometryName = parameters['geometryName']
        self.geometryType = parameters['geometryType']
        self.crsTransform = self.setCoordinateTransform()

    def setCoordinateTransform(self):
        crsSource = QgsCoordinateReferenceSystem.fromEpsgId(self.sridSource)
        crsTarget = QgsCoordinateReferenceSystem.fromEpsgId(self.sridTarget)
        return QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())

    def transformGeometry(self, geom):
        tr = self.setCoordinateTransform()
        geom.transform(tr)
        return geom

    def toGetGeometry(self, txtGeometry):
        geometry = QgsGeometry.fromWkt(txtGeometry)
        geometry.transform(self.crsTransform)
        return "GeomFromText('{0}', {1}),".format(geometry.asWkt(), self.sridTarget)

    def toPostGeometry(self, qgsGeometryObject, is3D, bBDUni):
        # Vérification du type géométrique entre QGIS et le serveur
        # et transformation du type le cas échéant
        # Comme par exemple les équipements de transport qui sont de type géométrique
        # MULTIPOLYGON Z alors que QGIS renvoie du POLYGON Z
        serverGeometryType = self.geometryType
        serverGeometryTypePost = serverGeometryType
        # couches BDUni
        if is3D == 1:
            serverGeometryTypePost += 'Z'
        objectWkbTypeGeometry = qgsGeometryObject.wkbType()
        strObjectWkbTypeGeometry = QgsWkbTypes.displayString(objectWkbTypeGeometry)
        if strObjectWkbTypeGeometry != serverGeometryTypePost and not(strObjectWkbTypeGeometry.startswith(serverGeometryType)):
            qgsGeometryObject.convertToMultiType()
        qgsGeometryObject.transform(self.crsTransform)

        # Cas particulier de la BDUni, voir ticket http://sd-redmine.ign.fr/issues/15746
        if bBDUni is True and is3D == 1:
            geometryWithModifiedZ = qgsGeometryObject.get()
            geometryWithModifiedZ.dropZValue()
            geometryWithModifiedZ.addZValue(-1000.)
            qgsGeometryObject.set(geometryWithModifiedZ)

        geomAsWkt = qgsGeometryObject.asWkt()
        #CompoundCurve (
        if geomAsWkt.find("CompoundCurve (") != -1:
            tmp = geomAsWkt.replace("CompoundCurve (", " ")
            geomAsWkt = tmp[0:len(tmp) - 1]
        return '"{0}": "{1}"'.format(self.geometryName, geomAsWkt)

    def isBoundingBoxIntersectGeometryObject(self, boundingBoxSpatialFilter, qgsGeometryObject):
        boundingBoxGeometry = QgsGeometry.fromWkt(boundingBoxSpatialFilter)
        boundingBoxGeometryEngine = QgsGeometry.createGeometryEngine(boundingBoxGeometry.constGet())
        boundingBoxGeometryEngine.prepareGeometry()
        if boundingBoxGeometryEngine.intersects(qgsGeometryObject.constGet()):
            return True
        return False

    def isGeometryObjectIntersectSpatialFilter(self, spatialFilterGeometry, qgsGeometryObject):
        objectGeometryEngine = QgsGeometry.createGeometryEngine(qgsGeometryObject.constGet())
        objectGeometryEngine.prepareGeometry()
        if objectGeometryEngine.intersects(spatialFilterGeometry.constGet()):
            return True
        return False
