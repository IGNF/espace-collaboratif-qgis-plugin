from qgis.core import QgsVectorLayer, QgsEditorWidgetSetup, QgsFieldConstraints, QgsDefaultValue, QgsEditFormConfig

'''
Mise en forme des champs dans le formulaire d'attributs QGIS
'''


class EditFormFieldFromAttributes(object):
    # les données
    data = None
    # couche concernée
    layer = None
    # nom du champ
    name = None
    # n° du champ dans la liste des champs de l'objet
    index = None

    '''
    Initialisation de la classe avec la couche active (layer) et les données récupérées (data)
    au format json par la fonction core.client.py/connexionFeatureTypeJson
    '''
    def __init__(self, layer, data):
        self.data = data
        self.layer = layer

    '''
    Lecture des clé/valeurs de l'item 'attributes', par exemple
    "commentaire_nom": {"crs": null, "default_value": null, "id": 30180, "target_type": null, "name": "commentaire_nom",
    "short_name": "commentair", "title": "commentaire_nom", "description": "Ceci est un commentaire à remplir par l'utilisateur.",
    "min_length": null, "max_length": 255, "nullable": true, "unique": false, "srid": null, "position": 3, "listOfValues": "",
    "min_value": null, "max_value": null, "pattern": null, "is3d": false, "readOnly": false, "condition": null,
    "condition_field": null, "computed": false, "automatic": false, "formula": null, "queryable": false,
    "required": false, "mime_types": null, "type": "String"}
    '''
    def readData(self):
        valeurs = self.data['attributes']
        for c, v in valeurs.items():
            self.name = v['name']
            self.index = self.layer.fields().indexOf(self.name)
            self.setFieldTitle(v['title'])
            self.setFieldSwitchType(v['type'], v['default_value'])
            self.setFieldConstraintNotNull(v['nullable'])
            self.setFieldExpressionConstraintMinMaxLength(v['min_length'], v['max_length'], v['type'], v['nullable'])
            self.setFieldExpressionConstraintMinMaxValue(v['min_value'], v['max_value'], v['type'], v['nullable'])
            self.setFieldExpressionConstraintPattern(v['pattern'], v['type'], v['nullable'])
            self.setFieldConstraintUnique(v['unique'])
            self.setFieldListOfValues(v['listOfValues'], v['default_value'])
            self.setFieldReadOnly(v['readOnly'], v['automatic'])

    '''
    Formatage du champ en fonction du type collaboratif
    '''
    def setFieldSwitchType(self, vType, default_value):

        if vType == 'Boolean':
            self.setFieldBoolean(default_value)
            return

        if vType == 'DateTime':
            self.setFieldDateTime(default_value)
            return

        if vType == 'Date':
            self.setFieldDate(default_value)
            return

        if vType == 'Double':
            self.setFieldDouble(default_value)
            return

        if vType == 'Integer':
            self.setFieldInteger(default_value)
            return

        if vType == 'String':
            self.setFieldString(default_value)
            return

        if vType == 'YearMonth':
            self.setFieldYearMonth(default_value)
            return

        if vType == 'Year':
            self.setFieldYear(default_value)
            return

    '''
    Mise en forme du champ dans le formulaire d'attributs QGIS
    '''
    def setFormEditor(self, QgsEWS_type, QgsEWS_config):

        setup = QgsEditorWidgetSetup(QgsEWS_type, QgsEWS_config)
        self.layer.setEditorWidgetSetup(self.index, setup)

    '''
    Général > Alias
    
    L'item "title" du collaboratif devient dans le formulaire d'attributs QGIS l'Alias
    '''
    def setFieldTitle(self, title):

        if title is None or title is '':
            return

        self.layer.setFieldAlias(self.index, title)

    '''
    Contraintes > Non nul
    
    - Attention, c'est inversé entre les valeurs true/false de l'API et celles de la case à cocher QGIS :
    Nullable True --> case décochée
    Nullable False --> case cochée (ConstraintNotNull = 1)
    '''
    def setFieldConstraintNotNull(self, bNullable):

        if bNullable is None or bNullable is True or bNullable == '':
            return

        self.layer.setFieldConstraint(self.index, QgsFieldConstraints.Constraint.ConstraintNotNull)

    '''
    Contraintes > Unique
    
    - bUnique = True
    '''
    def setFieldConstraintUnique(self, bUnique):

        if bUnique is None or bUnique is False or bUnique == '':
            return

        self.layer.setFieldConstraint(self.index, QgsFieldConstraints.Constraint.ConstraintUnique)

    '''
    Général > Editable
    
    - readOnly = False,
      automatic = True (la valeur du champ est calculée directement par le serveur donc l'utilisateur
      ne doit normalement pas la remplir)
      champ = id
      The widget at the given index will not be editable
    '''
    def setFieldReadOnly(self, readOnly, automatic):

        if readOnly is False or self.name == 'id' or automatic is True:
            Qgs_editFormConfig = QgsEditFormConfig()
            Qgs_editFormConfig.setReadOnly(self.index)
            self.layer.setEditFormConfig(Qgs_editFormConfig)

        '''if readOnly is None or readOnly is True or readOnly == '':
            return

        Qgs_editFormConfig = QgsEditFormConfig()
        Qgs_editFormConfig.setReadOnly(self.index, False)
        self.layer.setEditFormConfig(Qgs_editFormConfig)'''

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
    def setFieldExpressionConstraintMinMaxValue(self, minValue, maxValue, vType, bNullable):

        if minValue is None and maxValue is None or minValue is '' and maxValue is '':
            return

        if vType == 'DateTime':
            minValue = minValue.replace(' ', 'T')
            maxValue = maxValue.replace(' ', 'T')

        expression = None

        if minValue is not None and maxValue is None or maxValue is '':
            expression = "\"{}\" >= {}".format(self.name, minValue)
        elif vType == 'Date' or vType == 'DateTime' or vType == 'YearMonth':
            expression = "\"{}\" >= '{}'".format(self.name, minValue)

        if minValue is None or minValue is '' and maxValue is not None:
            expression = "\"{}\" <= {}".format(self.name, maxValue)
        elif vType == 'Date' or vType == 'DateTime' or vType == 'YearMonth':
            expression = "\"{}\" <= '{}'".format(self.name, maxValue)

        if minValue is not None and maxValue is not None:
            expression = "\"{}\" >= {} and \"{}\" <= {}".format(self.name, minValue, self.name, maxValue)
        elif vType == 'Date' or vType == 'DateTime' or vType == 'YearMonth':
            expression = "\"{}\" >= '{}' and \"{}\" <= '{}'".format(self.name, minValue, self.name, maxValue)

        if vType == 'String' and bNullable is True:
            expression = "\"{}\" is null or {}".format(self.name, expression)

        self.layer.setConstraintExpression(self.index, expression)

    '''
    Contraintes > Expression (minLength/maxLength)
    
    Quand nullable = true, ce n'est apparemment pas suffisant pour les attributs de type String
    de juste laisser la case "Non nul" décochée. La valeur NULL n'est quand même pas acceptée.
    Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...
    '''
    def setFieldExpressionConstraintMinMaxLength(self, minLength, maxLength, vType, bNullable):

        if minLength is None and maxLength is None or minLength is '' and maxLength is '':
            return

        expression = None

        if minLength is not None and maxLength is None or maxLength is '':
            expression = "length(\"{}\") >= {}".format(self.name, minLength)

        if minLength is None or minLength is '' and maxLength is not None:
            expression = "length(\"{}\") <= {}".format(self.name, maxLength)

        if minLength is not None and maxLength is not None:
            expression = "length(\"{}\") >= {} AND length(\"{}\") <= {}".format(self.name, minLength, self.name,
                                                                                maxLength)

        if vType == 'String' and bNullable is True:
            expression = "\"{}\" is null or {}".format(self.name, expression)

        self.layer.setConstraintExpression(self.index, expression)

    '''
    Contraintes > Expression
    
    Quand nullable = true, ce n'est apparemment pas suffisant pour les attributs de type String
    de juste laisser la case "Non nul" décochée. La valeur NULL n'est quand même pas acceptée.
    Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...
    '''
    def setFieldExpressionConstraintPattern(self, pattern, vType, bNullable):

        if pattern is None or pattern is '':
            return

        newPattern = pattern.replace('\\', '\\\\')
        expression = "regexp_match(\"{}\", '{}') != 0".format(self.name, newPattern)

        if vType == 'String' and bNullable is True:
            expression = "\"{}\" is null or {}".format(self.name, expression)

        self.layer.setConstraintExpression(self.index, expression)

    '''
    Représentation du type d'outils : Edition de texte
    '''
    def setFieldString(self, defaultString):
        # Type: TextEdit
        QgsEWS_type = 'TextEdit'
        # Config: {'IsMultiline': False, 'UseHtml': False}
        QgsEWS_config = {'IsMultiline': False, 'UseHtml': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultString is None or defaultString is '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultString)))

    '''
    Représentation du type d'outils : Case à cocher
    '''
    def setFieldBoolean(self, defaultState):
        # Type: CheckBox
        QgsEWS_type = 'CheckBox'
        # Config: {'CheckedState': '1', 'UncheckedState': '0'}
        QgsEWS_config = {'CheckedState': '1', 'UncheckedState': '0'}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultState is None or defaultState is '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultState))

    '''
    Représentation du type d'outils : Plage
    '''
    def setFieldInteger(self, defaultInteger):
        # Type: Range
        QgsEWS_type = 'Range'
        # Config: {'AllowNull': True, 'Max': 2147483647, 'Min': -2147483648, 'Precision': 0, 'Step': 1,
        # 'Style': 'SpinBox'}
        if self.name == 'id':
            QgsEWS_config = {'AllowNull': False, 'Max': 2147483647, 'Min': -2147483648, 'Precision': 0,
                             'Step': 1, 'Style': 'SpinBox'}
        else:
            QgsEWS_config = {'AllowNull': True, 'Max': 2147483647, 'Min': -2147483648, 'Precision': 0,
                             'Step': 1, 'Style': 'SpinBox'}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultInteger is None or defaultInteger is '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultInteger))

    '''
    Représentation du type d'outils : Plage
    '''
    def setFieldDouble(self, defaultDouble):
        # Type: Range
        QgsEWS_type = 'Range'
        # Config: {'AllowNull': True, 'Max': 1.7976931348623157e+308, 'Min': -1.7976931348623157e+308,
        # 'Precision': 6, 'Step': 1.0, 'Style': 'SpinBox'}
        QgsEWS_config = {'AllowNull': True, 'Max': 1.7976931348623157e+308,
                         'Min': -1.7976931348623157e+308, 'Precision': 6, 'Step': 1.0,
                         'Style': 'SpinBox'}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDouble is None or defaultDouble is '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultDouble))

    '''
    Représentation du type d'outils : Date/Heure
    
    defaultDate peut prendre les valeurs : NULL, '2020-10-01', 'CURRENT_DATE' ou ''
    '''
    def setFieldDate(self, defaultDate):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd',
        # 'field_format': 'yyyy-MM-dd', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd',
                         'field_format': 'yyyy-MM-dd', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDate is None or defaultDate is '':
            return
        if defaultDate is 'CURRENT_DATE':
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue('to_date(now())'))
        else:
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultDate)))

    '''
    Représentation du type d'outils : Date/Heure
    
    defaultDateTime peut prendre les valeurs : NULL, '2020-10-01 00:00:00', 'CURRENT_DATE' ou ''
    '''
    def setFieldDateTime(self, defaultDateTime):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd HH:mm:ss',
        # 'field_format': 'yyyy-MM-dd HH:mm:ss', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': True,
                         'display_format': 'yyyy-MM-dd HH:mm:ss', 'field_format': 'yyyy-MM-dd HH:mm:ss',
                         'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDateTime is None or defaultDateTime is '':
            return
        if defaultDateTime is 'CURRENT_DATE':
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue('now()'))
        else:
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultDateTime)))

    '''
    Représentation du type d'outils : Date/Heure
    '''
    def setFieldYear(self, defaultYear):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy', 'field_format': 'yyyy',
        # 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy',
                         'field_format': 'yyyy', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultYear is None or defaultYear is '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultYear)))

    '''
    Représentation du type d'outils : Date/Heure
    
    ex defaultYearMonth : "2020-10"
    '''
    def setFieldYearMonth(self, defaultYearMonth):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy-MM',
        # 'field_format': 'yyyy-MM', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy-MM',
                         'field_format': 'yyyy-MM', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultYearMonth is None or defaultYearMonth is '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultYearMonth)))

    '''
    Représentation du type d'outils : Liste de valeurs
    
    - listOfValues : peut être de type
     - list ["LGV","Métro","Sans objet",null]
     - dict	{'A compléter': 'NR', 'Coupe rase': 'C', 'Peuplement sain': 'S'}
     - str "", chaine vide : on sort de la fonction
    
    - defaultListValue : une des valeurs de liste
    '''
    def setFieldListOfValues(self, listOfValues, defaultListValue):
        if listOfValues is None or listOfValues is '':
            return

        # Type: ValueMap
        QgsEWS_type = 'ValueMap'
        attribute_values = {}

        if type(listOfValues) is list:
            for value in listOfValues:
                attribute_values[value] = value

        if type(listOfValues) is dict:
            for attribute, value in listOfValues.items():
                attribute_values[attribute] = value

        # Config: {'map': {'A compléter': 'NR', 'Coupe rase': 'C', 'Peuplement sain': 'S'}}
        QgsEWS_config = {'map': attribute_values}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultListValue is None or defaultListValue is '':
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultListValue)))
