# -*- coding: utf-8 -*-
"""
Created on 23 oct. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""
from qgis.core import QgsEditorWidgetSetup, QgsFieldConstraints, QgsDefaultValue


class EditFormFieldFromAttributes(object):
    """
    Mise en forme des champs dans le formulaire d'attributs QGIS
    """

    '''
    Initialisation de la classe avec la couche active (layer) et les données récupérées (data)
    au format json
    '''

    def __init__(self, layer, data):
        # les données
        self.data = data
        # couche concernée
        self.layer = layer
        self.index = None
        self.name = None

    '''Lecture des clé/valeurs de l'item 'attributes', par exemple "commentaire_nom": {"crs": null, "default_value": 
    null, "id": 30180, "target_type": null, "name": "commentaire_nom", "short_name": "commentair", 
    "title": "commentaire_nom", "description": "Ceci est un commentaire à remplir par l'utilisateur.", "min_length": 
    null, "max_length": 255, "nullable": true, "unique": false, "srid": null, "position": 3, "listOfValues": "", 
    "min_value": null, "max_value": null, "pattern": null, "is3d": false, "readOnly": false, "condition": null, 
    "condition_field": null, "computed": false, "automatic": false, "formula": null, "queryable": false, "required": 
    false, "mime_types": null, "type": "String"} '''

    def readData(self):
        # Correspondance nom du champ/type du champ
        linkFieldType = {}
        for v in self.data:
            if v['name'] is None:
                continue
            self.name = v['name']
            self.index = self.layer.fields().indexOf(self.name)
            self.setFieldTitle(v['title'])
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
            # TODO voir Madeline pour le readOnly
            # self.setFieldReadOnly(v['readOnly'], v['computed'])
            self.setFieldReadOnly(v['computed'])
            linkFieldType[v['name']] = v['type']
        return linkFieldType

    def setFieldAllConstraints(self, constraints, bNullable):
        expressionAllConstraints = ''
        for c in constraints:
            if c == 'None':
                continue
            expressionAllConstraints += "({}) AND ".format(c)

        if expressionAllConstraints == '':
            return

        # Suppression du dernier AND inutile
        expressionAllConstraints = expressionAllConstraints[0:len(expressionAllConstraints) - 5]

        if bNullable:
            expressionAllConstraints = "\"{0}\" is null or \"{0}\" = 'null' or \"{0}\" = 'NULL' or ({1})".format(
                self.name, expressionAllConstraints)

        self.layer.setConstraintExpression(self.index, expressionAllConstraints)

    '''
    Formatage du champ en fonction du type collaboratif
    '''

    def setFieldSwitchType(self, vType, default_value):
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

        elif vType == 'String':
            self.setFieldString(default_value)

        elif vType == 'YearMonth':
            self.setFieldYearMonth(default_value)

        elif vType == 'Year':
            self.setFieldYear(default_value)

        elif vType == 'JsonValue':
            self.setJsonValue()

        else:
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
        if title is None or title == '':
            return
        self.layer.setFieldAlias(self.index, title)

    '''
    Contraintes > Non nul
    
    - Attention, c'est inversé entre les valeurs true/false de l'API et celles de la case à cocher QGIS :
    Nullable True --> case décochée
    Nullable False --> case cochée (ConstraintNotNull = 1)
    '''

    def setFieldConstraintNotNull(self, bNullable):
        if bNullable is None or bNullable is True or bNullable == '' or self.name == self.layer.idNameForDatabase:
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
      
      Contrairement à ce que dit l'aide de QGIS, setReadOnly doit être mis à True pour que le champ ne soit pas éditable
    '''

    # def setFieldReadOnly(self, readOnly, computed):
    def setFieldReadOnly(self, computed):
        # if self.name == self.layer.idNameForDatabase or readOnly or computed:
        if self.name == self.layer.idNameForDatabase or computed:
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

    def setFieldExpressionConstraintMinMaxValue(self, minValue, maxValue, vType, vName):
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

    '''
        Ajout d'une contrainte qui vérifie que pour la valeur d'un champ correspond
        un ou plusieurs valeurs d'un autre champ.
        Exemple si le champ "nature" est égal à 'Carrefour' alors le champ "nature_detaillee" doit être rempli
        par une des valeurs suivantes 'Echangeur', 'Rond-point', 'Echangeur complet', 'Echangeur partiel'
        La contrainte est de type
        CASE
            WHEN "nature" = 'Aérogare' THEN array_contains(array('NULL'),"nature_detaillee")
            WHEN "nature" = 'Aire de repos ou de service' THEN array_contains(array('Aire de repos','Aire de service'),
            "nature_detaillee")
            WHEN "nature" = 'Aire de triage' THEN ''
            WHEN "nature" = 'Carrefour' THEN array_contains(array('Echangeur','Rond-point','Echangeur complet',
            'Echangeur partiel'),"nature_detaillee")
            WHEN "nature" = 'Arrêt voyageurs' THEN array_contains(array('Arrêt touristique saisonnier',
            'Arrêt routier ferroviaire'),"nature_detaillee")
        END
    '''

    def setFieldExpressionConstraintMapping(self, constraintField, conditionField):
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

    '''
    Contraintes > Expression (minLength/maxLength)
    
    Quand nullable = true, ce n'est apparemment pas suffisant pour les attributs de type String
    de juste laisser la case "Non nul" décochée. La valeur NULL n'est quand même pas acceptée.
    Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...
    '''

    def setFieldExpressionConstraintMinMaxLength(self, minLength, maxLength, bNullable):

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

    '''
    Contraintes > Expression
    
    Quand nullable = true, ce n'est apparemment pas suffisant pour les attributs de type String
    de juste laisser la case "Non nul" décochée. La valeur NULL n'est quand même pas acceptée.
    Il semble qu'il faille rajouter dans la contrainte : xxxxx is null or ...
    '''

    def setFieldExpressionConstraintPattern(self, pattern, vType, bNullable):

        if pattern is None or pattern == '' or self.name == self.layer.idNameForDatabase:
            return 'None'

        newPattern = pattern.replace('\\', '\\\\')
        expression = "regexp_match(\"{}\", '{}') != 0".format(self.name, newPattern)

        if vType == 'String' and bNullable is True:
            expression = "\"{0}\" is null or \"{0}\" = 'null' or \"{0}\" = 'NULL' or {1}".format(self.name, expression)
        return expression

    '''
    Représentation du type d'outils : Edition de texte
    '''

    def setFieldString(self, defaultString):
        # Type: TextEdit
        QgsEWS_type = 'TextEdit'
        # Config: {'IsMultiline': False, 'UseHtml': False}
        QgsEWS_config = {'IsMultiline': False, 'UseHtml': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultString is None or defaultString == '':
            return

        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultString)))

    '''
    Représentation du type d'outils : Case à cocher
    '''

    def setFieldBoolean(self, defaultState):
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

    '''
    Représentation du type d'outils : Plage
    '''

    def setFieldInteger(self, defaultInteger):
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

    '''
    Représentation du type d'outils : Plage
    '''

    def setFieldDouble(self, defaultDouble):
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

        if defaultDate is None or defaultDate == '':
            return
        if defaultDate == 'CURRENT_DATE':
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
        QgsEWS_config = {'allow_null': True, 'calendar_popup': True, 'display_format': 'yyyy-MM-dd HH:mm:ss',
                         'field_format': 'yyyy-MM-dd HH:mm:ss', 'field_iso_format': False}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultDateTime is None or defaultDateTime == '':
            return
        if defaultDateTime == 'CURRENT_DATE':
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue('now()'))
        else:
            self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultDateTime)))

    '''Représentation du type Vue JSON'''

    def setJsonValue(self):
        # Type:JsonEdit
        QgsEWS_type = 'JsonEdit'
        # Config:{'DefaultView': 1, 'FormatJson': 0} arborescence/indenté
        QgsEWS_config = {'DefaultView': 1, 'FormatJson': 0}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

    '''
    Représentation du type d'outils : Date/Heure
    '''

    def setFieldYear(self, defaultYear):
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

        if defaultYearMonth is None or defaultYearMonth == '':
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
        if listOfValues is None or listOfValues == '':
            return

        # Type: ValueMap
        QgsEWS_type = 'ValueMap'
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

        # Config: {'map': {'A compléter': 'NR', 'Coupe rase': 'C', 'Peuplement sain': 'S'}}
        QgsEWS_config = {'map': attribute_values}
        self.setFormEditor(QgsEWS_type, QgsEWS_config)

        if defaultListValue is None or defaultListValue == '':
            defaultListValue = 'NULL'
        self.layer.setDefaultValueDefinition(self.index, QgsDefaultValue("'{}'".format(defaultListValue)))
