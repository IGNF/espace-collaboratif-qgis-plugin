from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsGeometry


class Wkt(object):
    sridSource = None
    sridTarget = None
    crsTransform = None
    geometryName = None

    def __init__(self, parameters):
        self.sridSource = parameters['sridSource']
        self.sridTarget = parameters['sridTarget']
        self.geometryName = parameters['geometryName']
        self.crsTransform = self.setCoordinateTransform()

    def setCoordinateTransform(self):
        crsSource = QgsCoordinateReferenceSystem(self.sridSource)
        crsTarget = QgsCoordinateReferenceSystem(self.sridTarget)
        return QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())

    def toGetGeometry(self, txtGeometry):
        geometry = QgsGeometry.fromWkt(txtGeometry)
        geometry.transform(self.crsTransform)
        return "GeomFromText('{0}', {1}),".format(geometry.asWkt(), self.sridTarget)

    def toPostGeometry(self, qgsGeometry):
        qgsGeometry.transform(self.crsTransform)
        return '"{0}": "{1}"'.format(self.geometryName, qgsGeometry.asWkt())
