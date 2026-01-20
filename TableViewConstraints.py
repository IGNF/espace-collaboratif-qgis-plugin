# -*- coding: utf-8 -*-
"""
Created on 15 jan. 2026

Gestionnaire de contraintes pour la vue tabulaire (attribute table).
Valide les contraintes lors de la sauvegarde des modifications.
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
        
        # Configuration des validateurs 
        self._validatorConfig = {
            'nullable': {
                'check': lambda c, v: c.get('nullable') is False and (v is None or v == '' or v == 'NULL'),
                'message': lambda f, c, v: f"Le champ '{f}' ne peut pas être vide (contrainte NOT NULL)"
            },
            'min_length': {
                'check': lambda c, v: c.get('min_length') is not None and v is not None and len(str(v)) < c['min_length'],
                'message': lambda f, c, v: f"Le champ '{f}' doit contenir au moins {c['min_length']} caractères"
            },
            'max_length': {
                'check': lambda c, v: c.get('max_length') is not None and v is not None and len(str(v)) > c['max_length'],
                'message': lambda f, c, v: f"Le champ '{f}' ne peut pas dépasser {c['max_length']} caractères"
            },
            'min_value': {
                'check': lambda c, v: c.get('min_value') is not None and v is not None and self._tryFloat(v, c['min_value'], lambda nv, mv: nv < mv),
                'message': lambda f, c, v: f"Le champ '{f}' doit être supérieur ou égal à {c['min_value']}"
            },
            'max_value': {
                'check': lambda c, v: c.get('max_value') is not None and v is not None and self._tryFloat(v, c['max_value'], lambda nv, mv: nv > mv),
                'message': lambda f, c, v: f"Le champ '{f}' doit être inférieur ou égal à {c['max_value']}"
            },
            'pattern': {
                'check': lambda c, v: c.get('pattern') is not None and v is not None and not re.match(c['pattern'], str(v)),
                'message': lambda f, c, v: f"Le champ '{f}' ne correspond pas au format attendu"
            },
            'enum': {
                'check': lambda c, v: c.get('enum') is not None and v is not None and not self._isInEnum(v, c['enum']),
                'message': lambda f, c, v: f"Le champ '{f}' doit avoir une des valeurs prédéfinies"
            }
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
        Utilise une configuration data-driven pour valider dynamiquement.

        :param fieldName: Nom du champ
        :param value: Valeur à valider
        :param fid: ID de l'entité
        :param feature: L'entité complète (pour les contraintes contextuelles)
        :return: Tuple (isValid, errorMessage)
        """
        constraint = self.constraintsByField.get(fieldName)
        if not constraint:
            return True, ""

        # Validation de l'unicité (nécessite une logique spéciale avec fid)
        if constraint.get('unique') is True and value is not None:
            if self._checkUnique(fieldName, value, fid):
                return False, f"Le champ '{fieldName}' doit être unique. La valeur '{value}' existe déjà"

        # Itérer sur tous les validateurs configurés
        for validatorKey, config in self._validatorConfig.items():
            try:
                if config['check'](constraint, value):
                    return False, config['message'](fieldName, constraint, value)
            except Exception:
                # Si le validateur échoue (ex: conversion impossible), on continue
                continue
        
        return True, ""
    
    # === Méthodes helper pour les validations complexes ===
    
    def _tryFloat(self, value: Any, constraintValue: Any, comparator) -> bool:
        """Tente une comparaison numérique, retourne False si impossible"""
        try:
            return comparator(float(value), float(constraintValue))
        except (ValueError, TypeError):
            return False
    
    def _isInEnum(self, value: Any, enumValues: Any) -> bool:
        """Vérifie si une valeur est dans l'énumération"""
        validValues = enumValues if isinstance(enumValues, list) else list(enumValues.keys()) if isinstance(enumValues, dict) else []
        return value in validValues or str(value) in [str(v) for v in validValues]
    
    def _checkUnique(self, fieldName: str, value: Any, fid: int) -> bool:
        """Vérifie si la valeur est unique dans la couche"""
        for existingFeature in self.layer.getFeatures():
            if existingFeature.id() != fid:
                if existingFeature.attribute(fieldName) == value:
                    return True  # Duplicate trouvé
        return False  # Unique

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