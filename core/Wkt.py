from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsWkbTypes


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
        crsSource = QgsCoordinateReferenceSystem(self.sridSource)
        crsTarget = QgsCoordinateReferenceSystem(self.sridTarget)
        return QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())

    def toGetGeometry(self, txtGeometry):
        geometry = QgsGeometry.fromWkt(txtGeometry)
        geometry.transform(self.crsTransform)
        return "GeomFromText('{0}', {1}),".format(geometry.asWkt(), self.sridTarget)

    def toPostGeometry(self, qgsGeometry, is3D):
        # Vérification du type géométrique entre QGIS et le serveur
        # et transformation du type le cas échéant
        # Comme par exemple les équipements de transport qui sont de type géométrique
        # MULTIPOLYGON Z alors que QGIS renvoie du POLYGON Z
        serverGeometryType = self.geometryType
        serverGeometryTypePost = serverGeometryType
        # couches BDUni
        if is3D == 1:
            serverGeometryTypePost += 'Z'
        objectWkbTypeGeometry = qgsGeometry.wkbType()
        strObjectWkbTypeGeometry = QgsWkbTypes.displayString(objectWkbTypeGeometry)
        if strObjectWkbTypeGeometry != serverGeometryTypePost and not(strObjectWkbTypeGeometry.startswith(serverGeometryType)):
            qgsGeometry.convertToMultiType()
        qgsGeometry.transform(self.crsTransform)
        return '"{0}": "{1}"'.format(self.geometryName, qgsGeometry.asWkt())

    def isBoundingBoxIntersectGeometryObject(self, boundingBoxSpatialFilter, qgsGeometryObject):
        boundingBoxGeometry = QgsGeometry.fromWkt(boundingBoxSpatialFilter)
        boundingBoxGeometryEngine = QgsGeometry.createGeometryEngine(boundingBoxGeometry.constGet())
        boundingBoxGeometryEngine.prepareGeometry()
        if boundingBoxGeometryEngine.intersects(qgsGeometryObject.constGet()):
            return True
        return False
