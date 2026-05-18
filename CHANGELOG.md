# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

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
