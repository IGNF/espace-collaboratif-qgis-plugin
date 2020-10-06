from qgis.core import QgsVectorLayer, QgsEditorWidgetSetup, QgsFieldConstraints, QgsDefaultValue, QgsEditFormConfig


class EditFormFieldFromAttributes(object):
    # Les items recherchés
    attributes = 'attributes'
    style = 'style'
    styles = 'styles'

    # les données
    data = None
    # couche concernée
    layer = None
    # nom du champ
    name = None
    # n° du champ dans la liste des champs de l'objet
    index = None


    '''
    '''
    def __init__(self, layer, data):
        self.data = data
        self.layer = layer


    '''
    '''
    def readData(self):
        for cle, valeurs in self.data.items():
            if cle != 'attributes':
                continue
            for c, v in valeurs.items():
                self.name = v['name']
                self.index = self.layer.fields().indexOf(self.name)
                self.setFieldSwitchType(v['type'], v['default_value'])
                self.setFieldExpressionConstraintMinMaxLength(v['min_length'], v['max_length'])
                self.setFieldExpressionConstraintMinMaxValue(v['min_value'], v['max_value'])
                self.setFieldExpressionConstraintPattern(v['pattern'])
                self.setFieldConstraintNotNull(v['nullable'])
                self.setFieldConstraintUnique(v['unique'])
                self.setFieldListOfValues(v['listOfValues'], v['default_value'])
                self.setFieldReadOnly(v['readOnly'])


    '''
    '''
    def setFieldSwitchType(self, vType, default_value):

        if vType == 'Boolean':
            self.setFieldFormBoolean(default_value)
            return

        if vType == 'DateTime':
            self.setFieldFormDateTime(default_value)
            return

        if vType == 'Date':
            self.setFieldFormDate(default_value)
            return

        if vType == 'Double':
            self.setFieldFormDouble(default_value)
            return

        if vType == 'Integer':
            self.setFieldFormInteger(default_value)
            return

        if vType == 'String':
            self.setFieldFormString(default_value)
            return

        if vType == 'YearMonth':
            self.setFieldYearMonth(default_value)
            return

        if vType == 'Year':
            self.setFieldFormYear(default_value)
            return


    '''
    '''
    def setFormEditor(self, QgsEWS_type, QgsEWS_config):
        setup = QgsEditorWidgetSetup(QgsEWS_type, QgsEWS_config)
        self.layer.setEditorWidgetSetup(self.index, setup)


    '''
    Contraintes > Non nul
    Attention, c'est inversé entre les valeurs true/false de l'API et celles de la case à cocher QGIS :
    Nullable true --> case décochée
    Nullable false --> case cochée (ConstraintNotNull = 1)
    '''
    def setFieldConstraintNotNull(self, bNullable):
        if bNullable is None or bNullable == 'True':
            return

        if bNullable == 'False':
            self.layer.setFieldConstraint(self.index, QgsFieldConstraints.Constraint.ConstraintNotNull)


    '''
    '''
    def setFieldConstraintUnique(self, bUnique):
        if bUnique is None or bUnique == 'False':
            return

        if bUnique == 'True':
            self.layer.setFieldConstraint(self.index, QgsFieldConstraints.Constraint.ConstraintUnique)


    '''
    If readOnly = False, the widget at the given index will be read-only. 
    '''
    def setFieldReadOnly(self, readOnly):
        if readOnly is None or readOnly == 'True':
            return

        Qgs_editFormConfig = QgsEditFormConfig ()
        if readOnly == 'False':
            Qgs_editFormConfig.setReadOnly(self.index, False)
            self.layer.setEditFormConfig(Qgs_editFormConfig)


    '''
    '''
    def setFieldExpressionConstraintMinMaxValue(self, minValue, maxValue):
        if minValue is None and maxValue is None:
            return

        expression = None
        if minValue is not None and maxValue is None:
            expression = "{} >= {}".format(self.name, minValue)
        if minValue is None and maxValue is not None:
            expression = "{} <= {}".format(self.name, maxValue)
        if minValue is not None and maxValue is not None:
            expression = "{} >= {} and {} <= {}".format(self.name, minValue, maxValue, self.name)

        self.layer.setConstraintExpression(self.index, expression)


    '''
    Contraintes > Expression
    length(  "texte_nom" )  >= 2 and  length(  "texte_nom" )  <= 10
    '''
    def setFieldExpressionConstraintMinMaxLength(self, minLength, maxLength):
        if minLength is None and maxLength is None:
            return

        expression = None
        if minLength is not None and maxLength is None:
            expression = "length({}) >= {}".format(self.name, minLength)
        if minLength is None and maxLength is not None:
            expression = "length({}) <= {}".format(self.name, maxLength)
        if minLength is not None and maxLength is not None:
            expression = "length({}) >= {} AND {} <= length({})".format(self.name, minLength, maxLength, self.name)

        self.layer.setConstraintExpression(self.index, expression)


    '''
    Contraintes > Expression
    regexp_match( "email", '^([a-z0-9_\\.-]+)@([\\da-z\\.-]+)\\.([a-z\\.]{2,6})$') != 0
    '''
    def setFieldExpressionConstraintPattern(self, pattern):
        if pattern is None:
            return
        expression = "regexp_match(\"{}\", '{}') != 0".format(self.name, pattern)
        self.layer.setConstraintExpression(self.index, expression)


    '''
    Représentation du type d'outils : Edition de texte
    ex defaultString : "titi"
    '''
    def setFieldFormString(self, defaultString):
        # Type: TextEdit
        QgsEWS_type = 'TextEdit'
        # Config: {'IsMultiline': False, 'UseHtml': False}
        QgsEWS_config = {'IsMultiline': False, 'UseHtml': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultString is None:
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultString))


    '''
    Représentation du type d'outils : Case à cocher
    defaultState : 'true' ou 'false'
    '''
    def setFieldFormBoolean(self, defaultState):
        # Type: CheckBox
        QgsEWS_type = 'CheckBox'
        # Config: {'CheckedState': '1', 'UncheckedState': '0'}
        QgsEWS_config = {'CheckedState': '1', 'UncheckedState': '0'}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultState is None:
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultState))


    '''
    Représentation du type d'outils : Plage
    ex defaultInteger : "12"
    '''
    def setFieldFormInteger(self, defaultInteger):
        # Type: Range
        QgsEWS_type = 'Range'
        # Config: {'AllowNull': True, 'Max': 2147483647, 'Min': -2147483648, 'Precision': 0, 'Step': 1, 'Style': 'SpinBox'}
        QgsEWS_config = {'AllowNull': True, 'Max': 2147483647, 'Min': -2147483648, 'Precision': 0,
                         'Step': 1, 'Style': 'SpinBox'}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultInteger is None:
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultInteger))


    '''
    Représentation du type d'outils : Plage
    ex defaultDouble : "18.4"
    '''
    def setFieldFormDouble(self, defaultDouble):
        # Type: Range
        QgsEWS_type = 'Range'
        # Config: {'AllowNull': True, 'Max': 1.7976931348623157e+308, 'Min': -1.7976931348623157e+308, 'Precision': 6, 'Step': 1.0, 'Style': 'SpinBox'}
        QgsEWS_config = {'AllowNull': True, 'Max': 1.7976931348623157e+308,
                         'Min': -1.7976931348623157e+308, 'Precision': 6, 'Step': 1.0,
                         'Style': 'SpinBox'}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDouble is None:
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultDouble))


    '''
    Représentation du type d'outils : Date/Heure
    defaultDate peut prendre les valeurs : NULL, '2020-10-01' ou 'CURRENT_DATE'
    '''
    def setFieldFormDate(self, defaultDate):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd', 'field_format': 'yyyy-MM-dd', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd',
                         'field_format': 'yyyy-MM-dd', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDate is None:
            return
        if defaultDate is 'CURRENT_DATE':
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue('to_date(now())'))
        else:
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultDate))


    '''
    Représentation du type d'outils : Date/Heure
    defaultDateTime peut prendre les valeurs : NULL, '2020-10-01 00:00:00' ou 'CURRENT_DATE'
    '''
    def setFieldFormDateTime(self, defaultDateTime):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd HH:mm:ss', 'field_format': 'yyyy-MM-dd HH:mm:ss', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': True,
                         'display_format': 'yyyy-MM-dd HH:mm:ss', 'field_format': 'yyyy-MM-dd HH:mm:ss',
                         'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDateTime is None:
            return
        if defaultDateTime is 'CURRENT_DATE':
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue('now()'))
        else:
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultDateTime))


    '''
    Représentation du type d'outils : Date/Heure
    ex defaultYear : "2000"
    '''
    def setFieldFormYear(self, defaultYear):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy', 'field_format': 'yyyy', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy',
                         'field_format': 'yyyy', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultYear is None:
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultYear))


    '''
    Représentation du type d'outils : Date/Heure
    ex defaultYearMonth : "2020-10"
    '''
    def setFieldYearMonth(self, defaultYearMonth):
        # Type: DateTime
        QgsEWS_type = 'DateTime'
        # Config: {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy-MM', 'field_format': 'yyyy-MM', 'field_iso_format': False}
        QgsEWS_config = {'allow_null': True, 'calendar_popup': False, 'display_format': 'yyyy-MM',
                         'field_format': 'yyyy-MM', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultYearMonth is None:
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultYearMonth))


    '''
    Représentation du type d'outils : Liste de valeurs
    listOfValues : peut être de type
     - list ["LGV","Métro","Sans objet",null]
     - dict	{'A compléter': 'NR', 'Coupe rase': 'C', 'Peuplement sain': 'S'}
     - str "", chaine vide : on sort de la fonction
    defaultListValue : une des valeurs de liste
    '''
    def setFieldListOfValues(self, listOfValues, defaultListValue):
        if listOfValues is None or listOfValues == '':
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

        if defaultListValue is None:
            return
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue(defaultListValue))
