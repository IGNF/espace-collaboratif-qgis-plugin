# -*- coding: utf-8 -*-
"""
Created on 15 jan. 2026

Gestionnaire de contraintes pour la vue tabulaire (attribute table).
Valide les contraintes lors de la sauvegarde des modifications.

@author: Plugin Team
"""
import re
from typing import Tuple, Optional, Dict, Any, List
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsVectorLayer, QgsFeature, Qgis
from qgis.utils import iface


class TableViewConstraints:
    """
    Gestionnaire de contraintes pour la vue tabulaire.
    Valide les contraintes des attributs avant la validation des modifications.
    """

    def __init__(self, layer: QgsVectorLayer, constraintsData: list) -> None:
        """
        Initialise le gestionnaire de contraintes.

        :param layer: La couche vectorielle QGIS
        :type layer: QgsVectorLayer
        :param constraintsData: Les données de contraintes provenant de l'espace collaboratif
        :type constraintsData: list
        """
        self.layer = layer
        self.constraintsData = constraintsData
        self.isConnected = False
        
        # Dictionnaire pour un accès rapide aux contraintes par nom de champ
        self.constraintsByField = {}
        self._buildConstraintsIndex()
        
        # Registre des validateurs de contraintes (mapping dynamique)
        self._constraintValidators = {
            'nullable': self._validateNotNull,
            'min_length': self._validateMinLength,
            'max_length': self._validateMaxLength,
            'min_value': self._validateMinValue,
            'max_value': self._validateMaxValue,
            'pattern': self._validatePattern,
            'unique': self._validateUnique,
            'enum': self._validateEnum
        }

    def _buildConstraintsIndex(self) -> None:
        """
        Construit un index des contraintes par nom de champ pour un accès rapide.
        """
        for fieldData in self.constraintsData:
            if fieldData.get('name'):
                self.constraintsByField[fieldData['name']] = fieldData

    def connectSignals(self) -> None:
        """
        Connecte les signaux nécessaires pour la validation des contraintes.
        """
        if not self.isConnected:
            # Connecte au signal d'édition démarré
            self.layer.editingStarted.connect(self.onEditingStarted)
            # Connecte au signal d'édition arrêté
            self.layer.editingStopped.connect(self.onEditingStopped)
            # Connecte au signal de modification d'attribut (temps réel)
            self.layer.attributeValueChanged.connect(self.onAttributeValueChanged)
            # Connecte au signal avant validation des changements
            self.layer.beforeCommitChanges.connect(self.validateBeforeCommit)
            self.isConnected = True

    def disconnectSignals(self) -> None:
        """
        Déconnecte les signaux.
        """
        if self.isConnected:
            try:
                self.layer.editingStarted.disconnect(self.onEditingStarted)
                self.layer.editingStopped.disconnect(self.onEditingStopped)
                self.layer.attributeValueChanged.disconnect(self.onAttributeValueChanged)
                self.layer.beforeCommitChanges.disconnect(self.validateBeforeCommit)
            except TypeError:
                # Les signaux n'étaient pas connectés
                pass
            self.isConnected = False

    def onEditingStarted(self) -> None:
        """
        Appelé quand l'édition démarre sur la couche.
        """
        if iface:
            iface.messageBar().pushMessage(
                "Mode édition",
                f"Édition activée sur '{self.layer.name()}'. Les contraintes seront validées lors de la sauvegarde.",
                level=Qgis.Info,
                duration=3
            )

    def onEditingStopped(self) -> None:
        """
        Appelé quand l'édition s'arrête sur la couche.
        """
        pass

    def onAttributeValueChanged(self, fid: int, fieldIndex: int, newValue: Any) -> None:
        """
        Appelé en temps réel quand une valeur d'attribut change dans la table.
        Permet de valider immédiatement la nouvelle valeur.
        
        :param fid: ID de l'entité modifiée
        :param fieldIndex: Index du champ modifié
        :param newValue: Nouvelle valeur saisie
        """
        fieldName = self.layer.fields()[fieldIndex].name()
        feature = self.layer.getFeature(fid)
        
        # Valider la nouvelle valeur
        isValid, errorMsg = self.validateFieldValue(fieldName, newValue, fid, feature)
        
        if not isValid:
            # Afficher un avertissement immédiat
            if iface:
                iface.messageBar().pushMessage(
                    "Attention - Contrainte non respectée",
                    f"Entité #{fid}, champ '{fieldName}': {errorMsg}",
                    level=Qgis.Warning,
                    duration=5
                )

    def validateBeforeCommit(self) -> None:
        """
        Valide toutes les modifications avant de les enregistrer.
        Empêche la sauvegarde si des contraintes ne sont pas respectées.
        """
        editBuffer = self.layer.editBuffer()
        if not editBuffer:
            return

        validationErrors = []

        # Valider les attributs modifiés
        changedAttributes = editBuffer.changedAttributeValues()
        for fid, attributes in changedAttributes.items():
            feature = self.layer.getFeature(fid)
            if not feature.isValid():
                continue
            
            errors = self._validateFeatureAttributes(fid, feature, attributes.items())
            validationErrors.extend(errors)

        # Valider les nouvelles entités ajoutées
        addedFeatures = editBuffer.addedFeatures()
        for fid, feature in addedFeatures.items():
            # Valider tous les champs de la nouvelle entité
            allFields = [(fieldIndex, feature.attribute(fieldIndex)) 
                         for fieldIndex in range(len(self.layer.fields()))]
            errors = self._validateFeatureAttributes(fid, feature, allFields)
            validationErrors.extend(errors)

        # Si des erreurs de validation existent, empêcher la sauvegarde
        if validationErrors:
            self.showValidationErrors(validationErrors)
            
            # Déconnecter temporairement ce signal pour éviter la récursion
            self.layer.beforeCommitChanges.disconnect(self.validateBeforeCommit)
            
            # Annuler les modifications en faisant un rollback
            self.layer.rollBack()
            
            # Remettre la couche en mode édition
            self.layer.startEditing()
            
            # Reconnecter le signal
            self.layer.beforeCommitChanges.connect(self.validateBeforeCommit)
            
            # Afficher un message d'erreur
            if iface:
                iface.messageBar().pushMessage(
                    "Erreur de validation",
                    "Sauvegarde annulée : des contraintes ne sont pas respectées. Corrigez les erreurs et sauvegardez à nouveau.",
                    level=Qgis.Critical,
                    duration=7
                )

    def _validateFeatureAttributes(self, fid: int, feature: QgsFeature, 
                                   fieldItems: List[Tuple[int, Any]]) -> List[Dict[str, Any]]:
        """
        Valide une liste d'attributs pour une entité donnée.
        Méthode helper pour éviter la duplication de code.

        :param fid: ID de l'entité
        :param feature: L'entité à valider
        :param fieldItems: Liste de tuples (fieldIndex, value) à valider
        :return: Liste des erreurs de validation
        """
        errors = []
        for fieldIndex, value in fieldItems:
            fieldName = self.layer.fields()[fieldIndex].name()
            isValid, errorMsg = self.validateFieldValue(
                fieldName, 
                value, 
                fid, 
                feature
            )
            
            if not isValid:
                errors.append({
                    'fid': fid,
                    'fieldName': fieldName,
                    'error': errorMsg,
                    'value': value
                })
        
        return errors

    def validateFieldValue(self, fieldName: str, value: Any, fid: int, feature: QgsFeature) -> Tuple[bool, str]:
        """
        Valide une valeur de champ selon les contraintes définies.
        Itère dynamiquement sur toutes les contraintes applicables.

        :param fieldName: Nom du champ
        :param value: Valeur à valider
        :param fid: ID de l'entité
        :param feature: L'entité complète (pour les contraintes contextuelles)
        :return: Tuple (isValid, errorMessage)
        """
        # Récupérer les contraintes pour ce champ
        constraint = self.constraintsByField.get(fieldName)
        
        if not constraint:
            # Pas de contrainte définie pour ce champ
            return True, ""

        # Itérer dynamiquement sur toutes les contraintes définies
        for constraintKey, validator in self._constraintValidators.items():
            if constraintKey in constraint:
                isValid, errorMsg = validator(fieldName, value, fid, constraint, feature)
                if not isValid:
                    return False, errorMsg
        
        return True, ""
    
    # === Validateurs individuels (peuvent être facilement étendus) ===
    
    def _validateNotNull(self, fieldName: str, value: Any, fid: int, 
                        constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide la contrainte NOT NULL"""
        if constraint.get('nullable') is False:
            if value is None or value == '' or value == 'NULL':
                return False, f"Le champ '{fieldName}' ne peut pas être vide (contrainte NOT NULL)"
        return True, ""
    
    def _validateMinLength(self, fieldName: str, value: Any, fid: int, 
                          constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide la longueur minimale"""
        minLength = constraint.get('min_length')
        if minLength is not None and value is not None:
            if len(str(value)) < minLength:
                return False, f"Le champ '{fieldName}' doit contenir au moins {minLength} caractères"
        return True, ""
    
    def _validateMaxLength(self, fieldName: str, value: Any, fid: int, 
                          constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide la longueur maximale"""
        maxLength = constraint.get('max_length')
        if maxLength is not None and value is not None:
            if len(str(value)) > maxLength:
                return False, f"Le champ '{fieldName}' ne peut pas dépasser {maxLength} caractères"
        return True, ""
    
    def _validateMinValue(self, fieldName: str, value: Any, fid: int, 
                         constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide la valeur minimale"""
        minValue = constraint.get('min_value')
        if minValue is not None and value is not None:
            try:
                numValue = float(value)
                if numValue < float(minValue):
                    return False, f"Le champ '{fieldName}' doit être supérieur ou égal à {minValue}"
            except (ValueError, TypeError):
                pass
        return True, ""
    
    def _validateMaxValue(self, fieldName: str, value: Any, fid: int, 
                         constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide la valeur maximale"""
        maxValue = constraint.get('max_value')
        if maxValue is not None and value is not None:
            try:
                numValue = float(value)
                if numValue > float(maxValue):
                    return False, f"Le champ '{fieldName}' doit être inférieur ou égal à {maxValue}"
            except (ValueError, TypeError):
                pass
        return True, ""
    
    def _validatePattern(self, fieldName: str, value: Any, fid: int, 
                        constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide le pattern (expression régulière)"""
        pattern = constraint.get('pattern')
        if pattern is not None and value is not None:
            if not re.match(pattern, str(value)):
                return False, f"Le champ '{fieldName}' ne correspond pas au format attendu"
        return True, ""
    
    def _validateUnique(self, fieldName: str, value: Any, fid: int, 
                       constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide l'unicité"""
        if constraint.get('unique') is True and value is not None:
            for existingFeature in self.layer.getFeatures():
                if existingFeature.id() != fid:
                    existingValue = existingFeature.attribute(fieldName)
                    if existingValue == value:
                        return False, f"Le champ '{fieldName}' doit être unique. La valeur '{value}' existe déjà"
        return True, ""
    
    def _validateEnum(self, fieldName: str, value: Any, fid: int, 
                     constraint: dict, feature: QgsFeature) -> Tuple[bool, str]:
        """Valide les valeurs énumérées"""
        enumValues = constraint.get('enum')
        if enumValues is not None and value is not None:
            # enumValues peut être une liste ou un dictionnaire
            validValues = []
            if isinstance(enumValues, list):
                validValues = enumValues
            elif isinstance(enumValues, dict):
                validValues = list(enumValues.keys())
            
            if value not in validValues and str(value) not in [str(v) for v in validValues]:
                return False, f"Le champ '{fieldName}' doit avoir une des valeurs prédéfinies"
        return True, ""

    def showValidationErrors(self, errors: List[Dict[str, Any]]) -> None:
        """
        Affiche les erreurs de validation à l'utilisateur.

        :param errors: Liste des erreurs de validation
        """
        if not errors:
            return

        # Construire le message d'erreur
        errorMessage = "Les contraintes suivantes ne sont pas respectées :\n\n"
        
        # Grouper les erreurs par entité
        errorsByFeature = {}
        for error in errors:
            fid = error['fid']
            if fid not in errorsByFeature:
                errorsByFeature[fid] = []
            errorsByFeature[fid].append(error)

        # Limiter l'affichage aux 10 premières erreurs pour ne pas surcharger
        errorCount = 0
        maxErrors = 10
        
        for fid, featureErrors in errorsByFeature.items():
            if errorCount >= maxErrors:
                remaining = len(errors) - errorCount
                errorMessage += f"\n... et {remaining} autres erreur(s)"
                break
            
            errorMessage += f"Entité #{fid} :\n"
            for error in featureErrors:
                errorMessage += f"  • {error['error']}\n"
                errorCount += 1
                if errorCount >= maxErrors:
                    break
            errorMessage += "\n"

        errorMessage += "\nVeuillez corriger ces erreurs avant de sauvegarder."

        # Afficher le message d'erreur
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle("Erreurs de validation des contraintes")
        msgBox.setText("Impossible de sauvegarder les modifications")
        msgBox.setInformativeText(errorMessage)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def getConstraintForField(self, fieldName: str) -> Optional[Dict[str, Any]]:
        """
        Récupère la définition de contrainte pour un champ.

        :param fieldName: Nom du champ
        :return: Dictionnaire de contraintes ou None
        """
        return self.constraintsByField.get(fieldName)