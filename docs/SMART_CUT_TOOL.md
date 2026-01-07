# Smart Cut Tool - Documentation

## Vue d'ensemble

Le **Smart Cut Tool** (Outil de Découpe Intelligente) est un nouvel outil QGIS qui permet de découper des polygones tout en gérant intelligemment les attributs uniques. Contrairement à l'outil de découpe standard de QGIS, cet outil garantit que les attributs uniques (comme `cleaabs`) restent uniquement sur le plus grand polygone résultant de la découpe.

## Fonctionnalités

- ✂️ **Découpe de polygones** : Tracez une ligne pour découper un polygone en plusieurs morceaux
- 📏 **Calcul automatique des surfaces** : Compare automatiquement les surfaces des polygones résultants
- 🔑 **Gestion des attributs uniques** : Conserve les attributs uniques uniquement sur le plus grand polygone
- ⚙️ **Configuration flexible** : Définissez quels attributs doivent être uniques
- 👁️ **Aperçu avant validation** : Visualisez les surfaces avant de confirmer la découpe

## Installation

Les fichiers suivants ont été créés :

```
espace-collaboratif-qgis-plugin/
├── core/
│   ├── MapToolSmartCut.py      # Outil principal de découpe
│   └── SmartCutHelper.py       # Fonctions utilitaires
├── FormSmartCutConfig.py       # Interface de configuration
├── PluginModule.py             # Intégration dans le plugin (modifié)
└── Contexte.py                 # Support du contexte (modifié)
```

## Utilisation

### 1. Configuration initiale

Avant d'utiliser l'outil pour la première fois :

1. Cliquez sur le bouton **"Configurer la découpe intelligente"** dans la barre d'outils
2. La fenêtre de configuration s'ouvre
3. Sélectionnez ou ajoutez les attributs qui doivent rester uniques (ex: `cleaabs`, `id`)
4. Cliquez sur **"🔍 Détecter automatiquement"** pour une détection automatique
5. Validez avec **OK**

### 2. Découper un polygone

1. **Sélectionnez une couche de polygones** dans QGIS
2. **Sélectionnez un polygone** sur la carte
3. Cliquez sur le bouton **"Découpe intelligente de polygone"** dans la barre d'outils
4. **Tracez une ligne** à travers le polygone :
   - Clic gauche pour ajouter des points
   - Clic droit pour terminer le tracé
5. Une fenêtre de confirmation s'affiche avec :
   - Les surfaces de chaque polygone résultant
   - Quel polygone conservera les attributs uniques
6. Cliquez sur **Oui** pour confirmer ou **Non** pour annuler

### 3. Résultat

- Le polygone est découpé en plusieurs morceaux
- Les attributs uniques (ex: `cleaabs`) sont conservés uniquement sur le **plus grand polygone**
- Les autres polygones ont ces attributs vidés (NULL ou chaîne vide)
- Tous les autres attributs sont copiés sur tous les polygones

## Configuration avancée

### Définir des attributs uniques

Plusieurs méthodes pour configurer les attributs uniques :

#### Méthode 1 : Depuis la couche active
1. Sélectionnez une couche de polygones
2. Ouvrez la configuration
3. Les champs de la couche s'affichent
4. Sélectionnez les champs et cliquez sur **"⬇ Ajouter sélection"**

#### Méthode 2 : Détection automatique
1. Ouvrez la configuration
2. Cliquez sur **"🔍 Détecter automatiquement"**
3. L'outil détecte automatiquement les champs avec des noms suggérant l'unicité :
   - `id`, `cleaabs`, `uid`, `uuid`, `identifier`
   - `code`, `numero`, `num`, `fid`, `objectid`

#### Méthode 3 : Ajout manuel
1. Tapez le nom de l'attribut dans le champ "Ajouter manuellement"
2. Cliquez sur **Ajouter**

### Validation des attributs

Lorsque vous activez l'outil, il vérifie si les attributs configurés existent dans la couche active :
- ✅ **Attributs valides** : Utilisés pour la découpe
- ⚠️ **Attributs invalides** : Message d'avertissement avec possibilité de continuer

## Exemples d'utilisation

### Exemple 1 : Découpe d'une parcelle avec cleaabs unique

```
Avant découpe :
┌─────────────────┐
│  Parcelle       │
│  cleaabs: 12345 │
│  surface: 1000m²│
└─────────────────┘

Après découpe avec ligne verticale :
┌────────┐┌────────┐
│ Part 1 ││ Part 2 │
│ 600m²  ││ 400m²  │
│ cleaabs││        │
│ 12345  ││ cleaabs│
│        ││ NULL   │
└────────┘└────────┘
```

Le plus grand morceau (600m²) conserve `cleaabs=12345`, le plus petit a `cleaabs=NULL`.

### Exemple 2 : Découpe en 3 morceaux

Si la ligne de découpe crée 3 polygones ou plus, seul le plus grand conserve les attributs uniques.

## Icône personnalisée

### TODO : Créer une icône

Pour le moment, l'outil utilise temporairement l'icône `config.png`. Pour créer une icône personnalisée :

1. Créez une image PNG 24x24 pixels représentant une découpe intelligente
2. Sauvegardez-la dans : `espace-collaboratif-qgis-plugin/images/smart_cut.png`
3. Mettez à jour le fichier `resources.qrc` :
```xml
<file>images/smart_cut.png</file>
```
4. Recompilez les ressources :
```bash
pyrcc5 resources.qrc -o resources.py
```
5. Modifiez `PluginModule.py` ligne ~578 et ~586 :
```python
# Remplacer
icon_path = ':/plugins/RipartPlugin/images/config.png'
# Par
icon_path = ':/plugins/RipartPlugin/images/smart_cut.png'
```

### Suggestion d'icône

L'icône pourrait représenter :
- ✂️ Des ciseaux avec un polygone
- 📐 Une règle coupant un polygone
- 🔢 Un polygone avec une flèche vers le plus grand morceau

## Architecture technique

### Classes principales

#### `MapToolSmartCut` (core/MapToolSmartCut.py)
- Hérite de `QgsMapToolCapture`
- Gère le tracé de la ligne de découpe
- Calcule les surfaces
- Applique la logique de gestion des attributs

#### `SmartCutHelper` (core/SmartCutHelper.py)
- Fonctions utilitaires
- Gestion de la configuration (lecture/écriture dans QgsSettings)
- Validation des attributs
- Détection automatique des champs uniques
- Formatage des surfaces

#### `FormSmartCutConfig` (FormSmartCutConfig.py)
- Interface de configuration
- Sélection des attributs uniques
- Intégration avec les couches QGIS

### Flux de travail technique

```
1. Activation de l'outil
   ↓
2. Validation de la couche et de la sélection
   ↓
3. Mode capture activé (tracé de ligne)
   ↓
4. Clic droit → Fin du tracé
   ↓
5. Appel à QgsGeometry.splitGeometry()
   ↓
6. Calcul des surfaces de chaque polygone
   ↓
7. Tri par surface (décroissant)
   ↓
8. Fenêtre de confirmation
   ↓
9. Application des changements :
   - Mise à jour de la géométrie originale
   - Création de nouvelles features
   - Gestion des attributs uniques
   ↓
10. Commit des modifications
```

## Stockage de la configuration

Les attributs uniques configurés sont stockés dans les paramètres QGIS :
- **Clé** : `espaceco/smartcut/unique_attributes`
- **Format** : Chaîne séparée par des virgules
- **Exemple** : `"cleaabs,id,code_parcelle"`

Cette configuration est persistante entre les sessions QGIS.

## Gestion des erreurs

L'outil gère les cas suivants :
- ❌ Pas de couche sélectionnée
- ❌ Couche non vectorielle
- ❌ Couche non polygonale
- ❌ Pas de polygone sélectionné
- ❌ Plusieurs polygones sélectionnés
- ❌ Ligne de découpe invalide (moins de 2 points)
- ❌ Découpe qui ne produit pas de nouveaux polygones
- ⚠️ Attributs configurés absents de la couche

## Limitations connues

1. **Un seul polygone à la fois** : L'outil ne supporte que la découpe d'un polygone à la fois
2. **Mode édition requis** : La couche doit être en mode édition (le plugin propose de l'activer automatiquement)
3. **Polygones simples** : Fonctionne mieux avec des polygones simples (sans trous complexes)

## Compatibilité

- ✅ QGIS 3.x
- ✅ Couches vectorielles (SpatiaLite, Shapefile, GeoPackage, etc.)
- ✅ Tous les types d'attributs (texte, numérique, etc.)

## Dépannage

### Problème : L'outil ne s'active pas
- ✓ Vérifiez qu'une couche de polygones est sélectionnée
- ✓ Vérifiez qu'un polygone est sélectionné sur la carte
- ✓ Consultez les logs du plugin

### Problème : Les attributs ne sont pas gérés correctement
- ✓ Vérifiez la configuration des attributs uniques
- ✓ Vérifiez que les attributs existent dans la couche
- ✓ Consultez la fenêtre de confirmation avant la découpe

### Problème : Erreur lors de la découpe
- ✓ Assurez-vous que la ligne de découpe traverse bien le polygone
- ✓ Vérifiez que la géométrie du polygone est valide
- ✓ Essayez une ligne de découpe plus simple

## Support et contribution

Pour les bugs, suggestions ou questions :
1. Vérifiez les logs : Menu Aide → Ouvrir le fichier de log
2. Consultez le code source dans `core/MapToolSmartCut.py`
3. Contactez l'équipe de développement

## Changelog

### Version 1.0 (Janvier 2026)
- ✨ Création initiale de l'outil Smart Cut
- ✨ Interface de configuration des attributs uniques
- ✨ Détection automatique des champs uniques
- ✨ Gestion intelligente des attributs après découpe
- ✨ Intégration dans le plugin Espace Collaboratif

## Licence

Ce plugin est distribué sous licence GNU GPL v2 (voir LICENSE.md)

---

**Note** : Cette documentation a été générée lors de la création du Smart Cut Tool. Pour toute mise à jour du plugin, pensez à mettre à jour cette documentation.
