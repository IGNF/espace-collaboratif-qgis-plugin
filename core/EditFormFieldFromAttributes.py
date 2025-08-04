# -*- coding: utf-8 -*-
"""
Created on 23 oct. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""
from qgis.core import QgsEditorWidgetSetup, QgsFieldConstraints, QgsDefaultValue
from .GuichetVectorLayer import GuichetVectorLayer


class EditFormFieldFromAttributes(object):
    """
    Mise en forme des champs dans le formulaire d'attributs QGIS.
    Pour accéder au formulaire dans QGIS : [ Couche/Propriétés.../Formulaire d'attributs ]
    """

    def __init__(self, layer, data) -> None:
        """
        Initialisation de la classe avec la couche active (layer) et les données récupérées au format json (data).

        :param layer: couche GQIS active
        :type layer: GuichetVectorLayer

        :param data: données récupérées par requête
        :type data: dict
        """
        # les données
        self.data = data
        # couche concernée
        self.layer = layer
        self.index = None
        self.name = None

    def readDataAndApplyConstraints(self) -> None:
        """
        Lecture des données pour appliquer les contraintes des attributs de l'espace collaboratif
        sur les champs d'une couche QGIS. Par exemple :
        {
            'table_id': 4362,
            'crs': None,
            'enum': None,
            'default_value': None,
            'read_only': False,
            'id': 71688,
            'type': 'String',
            'target_table': None,
            'target_entity': None,
            'name': 'cleabs',
            'short_name': 'ID',
            'title': 'Cleabs',
            'description': "Identifiant unique de l'objet. ",
            'min_length': None,
            'max_length': 24,
            'nullable': False,
            'unique': False,
            'srid': None,
            'position': 1,
            'min_value': None,
            'max_value': None,
            'pattern': None,
            'is3d': False,
            'constraint': None,
            'condition_field': None,
            'computed': False,
            'automatic': False,
            'custom_id': False,
            'formula': None,
            'json_schema': None,
            'jeux_attributs': None,
            'queryable': True,
            'required': False,
            'mime_types': None
        }
        """
        for v in self.data:
            if v['name'] is None:
                continue
            self.name = v['name']
            self.index = self.layer.fields().indexOf(self.name)
            self.setFieldAlias(v['title'])
            self.setFieldSwitchType(v['type'], v['default_value'])
            self.setFieldConstraintNotNull(v['nullable'])
            self.setFieldConstraintUnique(v['unique'])
            constraints = [self.setFieldExpressionConstraintMinMaxLength(v['min_length'], v['max_length'],
                                                                         v['nullable']),
                           self.setFieldExpressionConstraintMinMaxValue(v['min_value'], v['max_value'], v['type'],
                                                                        v['name']),
                           self.setFieldExpressionConstraintPattern(v['pattern'], v['type'], v['nullable']),
                           self.setFieldExpressionConstraintMapping(v['constraint'], v['condition_field'])]
            self.setFieldAllConstraints(constraints, v['nullable'])
            self.setFieldListOfValues(v['enum'], v['default_value'])
            self.setFieldReadOnly(v['read_only'])
            # self.setFieldReadOnly(v['computed'])

    def setFieldAllConstraints(self, constraints, bNullable) -> None:
        """
        Applique une liste de contraintes (dont la valeur 'NULL') à un champ en les concaténant sous forme d'expression.
        Ces contraintes sont séparées par un AND.

        :param constraints: l'ensemble des contraintes d'un attribut
        :type constraints: list

        :param bNullable: indique si un champ peut contenir la valeur nulle
        :type bNullable: bool
        """
        expressionAllConstraints = ''

        for c in constraints:
            if c == 'None':
                continue
            expressionAllConstraints += "({}) AND ".format(c)

        if expressionAllConstraints != '' and bNullable:
            expressionAllConstraints = "\"{0}\" is null or \"{0}\" = 'null' or \"{0}\" = 'NULL' " \
                                       "or ({1})".format(self.name, expressionAllConstraints)
            # Suppression du dernier AND inutile
            expressionAllConstraints = expressionAllConstraints[0:len(expressionAllConstraints) - 6]
            expressionAllConstraints += ')'
            self.layer.setConstraintExpression(self.index, expressionAllConstraints)
        elif expressionAllConstraints == '' and bNullable:
            expressionAllConstraints = "\"{0}\" is null or \"{0}\" = 'null' or \"{0}\" = 'NULL'".format(self.name)
            self.layer.setConstraintExpression(self.index, expressionAllConstraints)
        elif expressionAllConstraints != '' and not bNullable:
            # Suppression du dernier AND inutile
            expressionAllConstraints = expressionAllConstraints[0:len(expressionAllConstraints) - 6]
            expressionAllConstraints += ')'
            self.layer.setConstraintExpression(self.index, expressionAllConstraints)

    def setFieldSwitchType(self, vType, default_value) -> None:
        """
        Passage d'un type de champ de l'espace collaboratif à un type de champ QGIS. Au passage, la valeur par défaut
        est ajoutée.

        La liste des types :
        'Boolean', 'DateTime', 'Date', 'Double', 'Integer', 'JsonValue', 'Document', 'Like', 'String', 'Year',
        'YearMonth', 'Geometry', 'GeometryCollection', 'Point', 'MultiPoint', 'LineString', 'MultiLineString',
        'Polygon', 'MultiPolygon'

        Pour retrouver un widget particulier sur un champ QGIS, voici un bout de code bien utile.
        (Exemple : Type d'outil/Edition de texte = TextEdit ou Type d'outil/Liste de valeurs = ValueMap)

        layer = self.context.iface.activeLayer()
        fields = layer.fields()
        for field in fields:
        name = field.name()
        if name != 'test': continue
        index = fields.indexOf(name)
        ews = layer.editorWidgetSetup(index)
        print("Type: {}".format(ews.type()))
        print("Config: {}".format(ews.config()))

        :param vType: valeur du type de champ, si None, sortie de fonction
        :type vType: str

        :param default_value: valeur par défaut
        :type default_value: str
        """
        if vType is None:
            return

        if vType == 'Boolean':
            self.setFieldBoolean(default_value)

        elif vType == 'DateTime':
            self.setFieldDateTime(default_value)

        elif vType == 'Date':
            self.setFieldDate(default_value)

        elif vType == 'Double':
            self.setFieldDouble(default_value)

        elif vType == 'Integer':
            self.setFieldInteger(default_value)

        elif vType == 'JsonValue':
            self.setJsonValue()

        elif vType == 'Document':
            self.setDocument()

        elif vType == 'String':
            self.setFieldString(default_value)

        elif vType == 'Year':
            self.setFieldYear(default_value)

        elif vType == 'YearMonth':
            self.setFieldYearMonth(default_value)

        else:
            return

    def setFormEditor(self, QgsEWS_type, QgsEWS_config) -> None:
        """
        Initialisation de la classe QgsEditorWidgetSetupMise et applique la mise en forme du champ
        dans le formulaire d'attributs QGIS.

        :param QgsEWS_type: le type de champ mode QGIS, par exemple : TextEdit
        :type QgsEWS_type: str

        :param QgsEWS_config: la configuration du champ mode QGIS, par exemple {'IsMultiline': False, 'UseHtml': False}
        :type QgsEWS_config: dict
        """
        setup = QgsEditorWidgetSetup(QgsEWS_type, QgsEWS_config)
        self.layer.setEditorWidgetSetup(self.index, setup)

    def setFieldAlias(self, alias) -> None:
        """
        Un attribut QGIS peut porter un 'Alias' [ Couche/Propriétés.../Formulaire d'attributs/Général > Alias ].
        L'item 'title' du collaboratif porte cette valeur qui est appliquée sur le champ QGIS en cours.
        Exemple : le champ 'numero' porte l'alias 'Numéro'.

        :param alias: la valeur issue du collaboratif, si None ou vide, sortie de fonction
        :type alias: str
        """
        if alias is None or alias == '':
            return
        self.layer.setFieldAlias(self.index, alias)

    def setFieldConstraintNotNull(self, bNullable) -> None:
        """
        Applique une contrainte de valeur non nulle au champ en cours.
        Attention, c'est inversé entre les valeurs true/false de l'API et celles de la case à cocher QGIS :
        - Nullable True --> case décochée
        - Nullable False --> case cochée (ConstraintNotNull = 1)
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Contraintes > Non nul ]

        :param bNullable: si None ou vide, sortie de fonction
        :type bNullable: bool
        """
        if bNullable is None or bNullable is True or bNullable == '' or self.name == self.layer.idNameForDatabase:
            return
        self.layer.setFieldConstraint(self.index, QgsFieldConstraints.Constraint.ConstraintNotNull)

    def setFieldConstraintUnique(self, bUnique) -> None:
        """
        Applique une contrainte de valeur unique au champ en cours.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Contraintes > Unique ]

        :param bUnique: à True si la valeur du champ doit être unique, si None ou vide, sortie de fonction
        :type bUnique: bool
        """
        if bUnique is None or bUnique is False or bUnique == '':
            return
        self.layer.setFieldConstraint(self.index, QgsFieldConstraints.Constraint.ConstraintUnique)

    def setFieldReadOnly(self, bReadOnly) -> None:
        """
        Applique au champ en cours une valeur d'édition.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Général > Editable ]
        La fonction 'setReadOnly' doit être mis à True pour que le champ ne soit pas éditable.
        Cas particulier du champ 'idNameForDatabase', il n'est pas éditable. L'id par exemple.

        :param bReadOnly: à True si le champ ne doit pas être éditable
        :type bReadOnly: bool
        """
        if self.name == self.layer.idNameForDatabase or bReadOnly:
            formConfig = self.layer.editFormConfig()
            formConfig.setReadOnly(self.index, True)
            self.layer.setEditFormConfig(formConfig)

    '''
    Contraintes > Expression (min_value/max_value)
    
    - Quand nullable = true, ce n'est apparemment pas suffisant pour les attributs de type String
    de juste laisser la case "Non nul" décochée. La valeur NULL n'est quand même pas acceptée.
    Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...
    
    - Pour que les contraintes sur les DateTime soient prises en compte, il faut remplacer l'espace
    entre la date et l'heure par un T majuscule : '2020-07-31 12:15:00' => '2020-07-31T12:15:00'
    
    - Si les les valeurs d'attributs de type : Date, DateTime et YearMonth ne sont pas entre quotes,
    la contrainte ne fonctionne pas.
    Il faut avoir : "date_nom" >= '2020-06-01' and "date_nom" <= '2021-06-30' 
    '''

    def setFieldExpressionConstraintMinMaxValue(self, minValue, maxValue, vType, vName) -> str:
        """
        Applique une contrainte d'expression de valeurs minimale et maximale au champ en cours.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Contraintes > Expression (min_value/max_value) ]
        Cas particuliers :
         - Quand nullable = true, ce n'est apparemment pas suffisant pour les attributs de type String
           de juste laisser la case "Non nul" décochée. La valeur NULL n'est quand même pas acceptée.
           Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...

         - Pour que les contraintes sur les DateTime soient prises en compte, il faut remplacer l'espace
           entre la date et l'heure par un T majuscule : '2020-07-31 12:15:00' => '2020-07-31T12:15:00'

         - Si les les valeurs d'attributs de type : Date, DateTime et YearMonth ne sont pas entre quotes,
           la contrainte ne fonctionne pas.
           Il faut avoir : "date_nom" >= '2020-06-01' and "date_nom" <= '2021-06-30'

        :param minValue: valeur minimum
        :type minValue: str

        :param maxValue: valeur maximale
        :type maxValue: str

        :param vType: valeur du type de champ
        :type vType: str

        :param vName: valeur du champ
        :type vName: str

        :return: l'expression mise en forme
        """
        expTmp = None
        if (minValue is None and maxValue is None) or (minValue == '' and maxValue == '') or self.name == vName:
            return 'None'

        if vType == 'DateTime':
            minValue = minValue.replace(' ', 'T')
            maxValue = maxValue.replace(' ', 'T')

        listExpressions = []

        # minValue
        if minValue is not None and minValue != '':
            if vType == 'Date' or vType == 'DateTime' or vType == 'YearMonth':
                expTmp = "\"{}\" >= \'{}\'".format(self.name, minValue)
            else:
                expTmp = "\"{}\" >= {}".format(self.name, minValue)
        listExpressions.append(expTmp)

        # maxValue
        if maxValue is not None and maxValue != '':
            if vType == 'Date' or vType == 'DateTime' or vType == 'YearMonth':
                expTmp = "\"{}\" <= \'{}\'".format(self.name, maxValue)
            else:
                expTmp = "\"{}\" <= {}".format(self.name, maxValue)
        listExpressions.append(expTmp)

        if len(listExpressions) == 0:
            return 'None'
        elif len(listExpressions) == 1:
            expression = listExpressions[0]
        else:
            expression = "{} and {}".format(listExpressions[0], listExpressions[1])
        return expression

    def setFieldExpressionConstraintMapping(self, constraintField, conditionField) -> str:
        """
        Ajout d'une contrainte qui vérifie que pour la valeur d'un champ correspond une ou plusieurs valeurs
        d'un autre champ.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Contraintes > Expression
        Exemple : si le champ "nature" est égal à 'Carrefour' alors le champ "nature_detaillee" doit être rempli
        par une des valeurs suivantes 'Echangeur', 'Rond-point', 'Echangeur complet', 'Echangeur partiel'
        La contrainte est de type :
           CASE
            - WHEN "nature" = 'Aérogare' THEN array_contains(array('NULL'),"nature_detaillee")
            - WHEN "nature" = 'Aire de repos ou de service' THEN array_contains(array('Aire de repos','Aire de service'),
              "nature_detaillee")
            - WHEN "nature" = 'Aire de triage' THEN ''
            - WHEN "nature" = 'Carrefour' THEN array_contains(array('Echangeur','Rond-point','Echangeur complet',
              'Echangeur partiel'),"nature_detaillee")
            - WHEN "nature" = 'Arrêt voyageurs' THEN array_contains(array('Arrêt touristique saisonnier',
              'Arrêt routier ferroviaire'),"nature_detaillee")
        END

        :param constraintField: la liste des contraintes sur le champ, si None, sortie de fonction
        :type constraintField: dict

        :param conditionField: le champ qui porte la condition, si None, sortie de fonction
        :type conditionField: str

        :return: la contrainte par expression
        """
        if constraintField is None and conditionField is None:
            return 'None'
        if constraintField['type'] != 'mapping':
            return 'None'
        expression = 'CASE'
        for k, v in constraintField['mapping'].items():
            # le caractère apostrophe est doublé
            nameField = conditionField.replace("'", "''")
            valueField = k.replace("'", "''")
            expression += ' WHEN "{}"=\'{}\''.format(nameField, valueField)
            if len(v) == 0:
                # le champ à valider peut-être vide
                expression += ' THEN array_contains(array(\'NULL\'),"{}")'.format(self.name)
            else:
                values = ''
                for tmp in v:
                    # Le caractère apostrophe est doublé
                    val = tmp.replace("'", "''")
                    values += "'{}',".format(val)
                # si array_contains retourne true, alors la valeur affectée au champ est bien contenue dans le tableau
                expression += ' THEN array_contains(array({}),"{}")'.format(values[0:len(values) - 1], self.name)
        expression += " END"
        return expression

    def setFieldExpressionConstraintMinMaxLength(self, minLength, maxLength, bNullable) -> str:
        """
        Applique au champ en cours une contrainte de longueur minimum et maximum.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Contraintes > Expression (minLength/maxLength)
        Quand nullable = true, ce n'est apparemment pas suffisant pour les attributs de type String
        de juste laisser la case "Non nul" décochée. La valeur NULL n'est quand même pas acceptée.
        Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...

        :param minLength: longueur minimum, si None ou vide : sortie de fonction
        :type minLength: str

        :param maxLength: longueur maximum, si None ou vide : sortie de fonction
        :type maxLength: str

        :param bNullable: à True si la valeur peut-être nulle
        :type bNullable: bool

        :return: l'expression mise en forme
        """
        if (minLength is None and maxLength is None) or \
                (minLength == '' and maxLength == '') or \
                self.name == self.layer.idNameForDatabase:
            return 'None'

        listExpressions = []

        # minLength
        if minLength is not None and minLength != '':
            expTmp = "length(\"{}\") >= {}".format(self.name, minLength)
            listExpressions.append(expTmp)

        # maxLength
        if maxLength is not None and minLength != '':
            expTmp = "length(\"{}\") <= {}".format(self.name, maxLength)
            listExpressions.append(expTmp)

        # Expression
        if len(listExpressions) == 0:
            return 'None'
        elif len(listExpressions) == 1:
            expression = listExpressions[0]
        else:
            expression = "{} and {}".format(listExpressions[0], listExpressions[1])

        # Cas particulier des string nullable
        if bNullable is True:
            expression = "\"{0}\" is null or \"{0}\" = 'null' or \"{0}\" = 'NULL' or ({1})".format(self.name,
                                                                                                   expression)
        return expression

    def setFieldExpressionConstraintPattern(self, pattern, vType, bNullable) -> str:
        """
        Ajout d'un modèle de contrainte sur le champ en cours.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Contraintes > Expression ]
        Quand nullable = True, ce n'est apparemment pas suffisant pour les attributs de type String
        de juste laisser la case "Non null" décochée. La valeur NULL n'est quand même pas acceptée.
        Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...

        :param pattern: le modèle de contrainte, si None ou vide : sortie de fonction
        :type pattern: str

        :param vType: le type de champ
        :type vType: str

        :param bNullable: à True, si la valeur du champ peut-être nulle
        :type bNullable: bool

        :return: l'expression mise en forme
        """
        if pattern is None or pattern == '' or self.name == self.layer.idNameForDatabase:
            return 'None'

        newPattern = pattern.replace('\\', '\\\\')
        expression = "regexp_match(\"{}\", '{}') != 0".format(self.name, newPattern)

        if vType == 'String' and bNullable is True:
            expression = "\"{0}\" is null or \"{0}\" = 'null' or \"{0}\" = 'NULL' or {1}".format(self.name, expression)
        return expression

    def setFieldString(self, defaultString) -> None:
        """
        Applique au champ en cours, une valeur texte par défaut.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Edition de texte ]

        :param defaultString: le texte, si None ou vide : sortir de fonction
        :type defaultString: str
        """
        # Type: TextEdit
        QgsEWS_type = 'TextEdit'
        # Config: {'IsMultiline': False, 'UseHtml': False}
        QgsEWS_config = {'IsMultiline': False, 'UseHtml': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultString is None or defaultString == '':
            return

        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultString)))

    def setFieldBoolean(self, defaultState) -> None:
        """
        Applique au champ en cours, une valeur par défaut de type case à cocher.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Case à cocher ]

        :param defaultState: peut prendre les valeurs None, vide, true, false
        :type defaultState: str
        """
        # Type: ValueMap
        QgsEWS_type = 'ValueMap'
        # Cas BDUNi
        attribute_values = {"Oui": '1', "Non": '0', "": 'NULL'}
        # Config: {'map': {'A compléter': 'NR', 'Coupe rase': 'C', 'Peuplement sain': 'S'}}
        QgsEWS_config = {'map': attribute_values}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultState is None or defaultState == '':
            defaultState = 'NULL'
        elif defaultState == 'true':
            defaultState = '1'
        elif defaultState == 'false':
            defaultState = '0'
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultState)))

    def setFieldInteger(self, defaultInteger) -> None:
        """
        Applique au champ en cours, une valeur par défaut de type entier. Une regex vérifie que la chaine de caractères
        ne contient que des nombres.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Plage ]

        :param defaultInteger: une valeur représentant un entier
        :type defaultInteger: str
        """
        # Il vaut mieux utiliser un TextEdit contraint par regex pour pouvoir gérer les valeurs null car le
        # type Range ne les accepte pas.
        # Type : TextEdit
        QgsEWS_type = 'TextEdit'
        # Config: {'IsMultiline': False, 'UseHtml': False}
        QgsEWS_config = {'IsMultiline': False, 'UseHtml': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultInteger is None or defaultInteger == '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultInteger))

        # Vérification que la chaine ne contient que des nombres
        expression = "regexp_match(\"{}\", '[0-9]+') != 0".format(self.name)
        self.layer.setConstraintExpression(self.index, expression)

    def setFieldDouble(self, defaultDouble) -> None:
        """
        Applique au champ en cours, une valeur par défaut de type float. Une regex vérifie que la chaine de caractères
        ne contient que des nombres.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Plage ]

        :param defaultDouble: une valeur représentant un nombre à virgule
        :type defaultDouble: str
        """
        # Il vaut mieux utiliser un TextEdit contraint par regex pour pouvoir gérer les valeurs null car le
        # type Range ne les accepte pas.
        # Type : TextEdit
        QgsEWS_type = 'TextEdit'
        # Config: {'IsMultiline': False, 'UseHtml': False}
        QgsEWS_config = {'IsMultiline': False, 'UseHtml': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDouble is None or defaultDouble == '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultDouble))

        # Vérification que la chaine ne contient que des nombres
        expression = "regexp_match(\"{}\", '[0-9]+(\\.[0-9]+)') != 0".format(self.name)
        self.layer.setConstraintExpression(self.index, expression)

    def setFieldDate(self, defaultDate) -> None:
        """
        Applique au champ en cours, une date par défaut.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Date/Heure ]

        :param defaultDate: peut prendre les valeurs NULL, '2020-10-01', 'CURRENT_DATE'
                            si None ou vide : sortie de fonction
        :type defaultDate: str
        """
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd',
        # 'field_format': 'yyyy-MM-dd', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd',
                         'field_format': 'yyyy-MM-dd', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDate is None or defaultDate == '':
            return
        if defaultDate == 'CURRENT_DATE':
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue('to_date(now())'))
        else:
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultDate)))

    def setFieldDateTime(self, defaultDateTime) -> None:
        """
        Applique au champ en cours, une date/time par défaut.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Date/Heure ]

        :param defaultDateTime: peut prendre les valeurs NULL, '2020-10-01 00:00:00', 'CURRENT_DATE'
                                si None ou vide : sortie de fonction
        :type defaultDateTime: str
        """
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd HH:mm:ss',
        # 'field_format': 'yyyy-MM-dd HH:mm:ss', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd HH:mm:ss',
                         'field_format': 'yyyy-MM-dd HH:mm:ss', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDateTime is None or defaultDateTime == '':
            return
        if defaultDateTime == 'CURRENT_DATE':
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue('now()'))
        else:
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultDateTime)))

    def setDocument(self) -> None:
        return

    def setJsonValue(self) -> None:
        """
        Applique par défaut une vue JSON de type arborescence/indenté au champ en cours.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Vue JSON ]
        """
        # Type:JsonEdit
        QgsEWS_type = 'JsonEdit'
        # Config:{'DefaultView': 1, 'FormatJson': 0} arborescence/indenté
        QgsEWS_config = {'DefaultView': 1, 'FormatJson': 0}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

    def setFieldYear(self, defaultYear) -> None:
        """
        Applique au champ en cours, une année par défaut.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Date/Heure ]

        :param defaultYear: une année, si None ou vide : sortie de fonction
        :type defaultYear: str
        """
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy', 'field_format': 'yyyy',
        # 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy', 'field_format': 'yyyy',
                         'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultYear is None or defaultYear == '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultYear)))

    def setFieldYearMonth(self, defaultYearMonth) -> None:
        """
        Applique au champ en cours, une Date/Heure par défaut.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Date/Heure ]

        :param defaultYearMonth: une valeur, exemple '2010-10', si vide ou None : sortie de fonction
        :type defaultYearMonth: str
        """
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy-MM',
        # 'field_format': 'yyyy-MM', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy-MM',
                         'field_format': 'yyyy-MM', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)
        if defaultYearMonth is None or defaultYearMonth == '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultYearMonth)))

    def setFieldListOfValues(self, listOfValues, defaultListValue) -> None:
        """
        Applique sur le champ en cours une liste de valeurs.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Liste de valeurs ]

        :param listOfValues: valeurs de liste, exemple ["LGV","Métro","Sans objet",null] ou
                             {'A compléter': 'NR', 'Coupe rase': 'C', 'Peuplement sain': 'S'}
                             si None ou vide : sortie de fonction
        :type listOfValues: list, dict

        :param defaultListValue: une des valeurs de liste
        :type defaultListValue: str

        """
        if listOfValues is None or listOfValues == '':
            return

        attribute_values = {}
        if type(listOfValues) is list:
            for value in listOfValues:
                if value is None:
                    attribute_values[""] = 'NULL'
                    continue
                attribute_values[value] = value

        if type(listOfValues) is dict:
            for attribute, value in listOfValues.items():
                if attribute is None:
                    attribute_values[""] = 'NULL'
                    continue
                attribute_values[attribute] = value

        # Type: ValueMap
        QgsEWS_type = 'ValueMap'
        # Config: {'map': {'A compléter': 'NR', 'Coupe rase': 'C', 'Peuplement sain': 'S'}}
        QgsEWS_config = {'map': attribute_values}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultListValue is None or defaultListValue == '':
            defaultListValue = 'NULL'
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultListValue)))
