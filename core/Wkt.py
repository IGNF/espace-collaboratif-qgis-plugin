from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsWkbTypes


class Wkt(object):

    def __init__(self, parameters) -> None:
        self.sridSource = parameters['sridSource']
        self.sridTarget = parameters['sridTarget']
        self.geometryName = parameters['geometryName']
        self.geometryType = parameters['geometryType']
        self.crsTransform = self.__setCoordinateTransform()

    def __setCoordinateTransform(self) -> QgsCoordinateTransform:
        """
        Construit un QgsCoordinateTransform pour transformer le système de référence de coordonnées source
        en système de référence de coordonnées de destination.

        :return: un QgsCoordinateTransform
        """
        crsSource = QgsCoordinateReferenceSystem(self.sridSource)
        crsTarget = QgsCoordinateReferenceSystem(self.sridTarget)
        return QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())

    def toGetGeometry(self, txtGeometry) -> str:
        """
        Transforme la géométrie au format texte en une géométrie WKT en changeant de système de coordonnées

        :param txtGeometry: la géométri d'un objet sous format texte
        :type txtGeometry: str

        :return: la partie géométrie d'une requête SQL en vue d'une insertion dans une table SQLite
        """
        geometry = QgsGeometry.fromWkt(txtGeometry)
        geometry.transform(self.crsTransform)
        return "GeomFromText('{0}', {1}),".format(geometry.asWkt(), self.sridTarget)

    @staticmethod
    def toGetLonLatFromGeometry(txtGeometry) -> ():
        """
        Transforme la géométrie au format texte en une géométrie WKT sous forme de point.

        :param txtGeometry: la géométrie d'un point d'un signalement
        :type txtGeometry: str

        :return: un tuple contenant la longitude et la latitude
        """
        geometry = QgsGeometry.fromWkt(txtGeometry)
        return geometry.asPoint().x(), geometry.asPoint().y()

    def toPostGeometry(self, qgsGeometryObject, is3D, bBDUni) -> {}:
        """
        Transformation du système de coordonnées et vérification du type géométrique entre QGIS et le serveur

        Si nécessaire transformation du type comme par exemple : les équipements de transport qui sont
        de type géométrique MULTIPOLYGON Z sur le serveur de l'espace collaboratif alors que QGIS renvoie
        un type POLYGON Z

        Cas particulier de la BDUni : les Z sont codés à -1000 en cas de création d'objet, ajout de point, déplacement.
        Voir ticket http://sd-redmine.ign.fr/issues/15746

        :param qgsGeometryObject: la géométrie QGIS d'un objet de la carte
        :type qgsGeometryObject: QgsGeometry

        :param is3D: à 1 si la géométrie est 3D
        :type is3D: int

        :param bBDUni: à True si la couche appartient à la BDUni
        :type bBDUni: bool

        :return: dict avec comme clé : le nom de la géométrie et valeur : la géométrie de l'objet au format WKT
        """
        serverGeometryType = self.geometryType
        serverGeometryTypePost = serverGeometryType
        # couches BDUni
        if is3D == 1:
            serverGeometryTypePost += 'Z'
        objectWkbTypeGeometry = qgsGeometryObject.wkbType()
        strObjectWkbTypeGeometry = QgsWkbTypes.displayString(objectWkbTypeGeometry)
        if strObjectWkbTypeGeometry != serverGeometryTypePost \
                and not(strObjectWkbTypeGeometry.startswith(serverGeometryType)):
            qgsGeometryObject.convertToMultiType()
        qgsGeometryObject.transform(self.crsTransform)

        # Cas particulier de la BDUni
        if bBDUni is True and is3D == 1:
            geometryWithModifiedZ = qgsGeometryObject.get()
            geometryWithModifiedZ.dropZValue()
            geometryWithModifiedZ.addZValue(-1000.)
            qgsGeometryObject.set(geometryWithModifiedZ)

        return {self.geometryName: qgsGeometryObject.asWkt()}

    def isBoundingBoxIntersectGeometryObject(self, boundingBoxSpatialFilter, qgsGeometryObject) -> bool:
        """
        Recherche si la géométrie d'un objet intersecte la zone de travail.

        :param boundingBoxSpatialFilter: la géométrie au format WKT de la boite englobante d'une zone de travail
        :type boundingBoxSpatialFilter: str

        :param qgsGeometryObject: la géométrie QGIS d'un objet de la carte
        :type qgsGeometryObject: QgsGeometry

        :return: True si la géométrie intersecte, False sinon
        """
        boundingBoxGeometry = QgsGeometry.fromWkt(boundingBoxSpatialFilter)
        boundingBoxGeometryEngine = QgsGeometry.createGeometryEngine(boundingBoxGeometry.constGet())
        boundingBoxGeometryEngine.prepareGeometry()
        if boundingBoxGeometryEngine.intersects(qgsGeometryObject.constGet()):
            return True
        return False
