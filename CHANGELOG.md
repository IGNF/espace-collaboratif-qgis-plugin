# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [5.0.9] - 2026-05-28

### Modifié
- Modifications système d'authentification

## [5.0.8] - 2026-05-20

### Corrigé
- Correction de l'application des contraintes bloquantes lors de la création d'un nouvel objet
- Ajout de styles ponctuels supplémentaires (triangle, carré, etc.)
- Correction du menu déroulant dans l'interface de téléchargement des couches

## [5.0.7] - 2026-05-18

### Modifié
- Mise en conformité avec les exigences d'analyse statique du dépôt officiel QGIS

## [5.0.6] - 2026-05-18

### Modifié
- Vérification SSL activée systématiquement sur toutes les requêtes réseau
- Ajout de délais d'attente (timeout) sur les appels HTTP pour éviter les blocages indéfinis
- Organisation des paramètres de connexion au service d'authentification 

## [5.0.5] - 2026-05-07

### Modifié
- Mise à jour de fonctions XML dépréciées

## [5.0.4] - 2026-05-07

### Corrigé
- Thème du signalement précédent à nouveau pré-sélectionné à l'ouverture du formulaire de création (#173, régression 5.0.3)
- Nouveau signalement désormais affiché automatiquement sur la carte après envoi, sans nécessiter un re-téléchargement manuel
- "Créer un signalement unique" à nouveau sélectionné par défaut lors de la création avec plusieurs croquis (#172 /#175, régression 5.0.3)
- Téléchargement des signalements fonctionnel même si les couches Signalement/Croquis sont déjà présentes (projet issu d'une version antérieure) : reconnexion automatique des couches à la base SQLite courante (#176)

## [5.0.3] - 2026-04-13

### Modifié
- Compatibilité Qt5/Qt6

## [5.0.2]

### Ajouté
- Filtre spatial sur le guichet
- Option de téléchargement public

### Corrigé
- Bug lié aux attributs NULL

## [5.0.1]

### Ajouté
- Filtre spatial sur le guichet
- Option de téléchargement public

### Corrigé
- Bug lié aux attributs NULL

## [5.0.0]

- Première version majeure
