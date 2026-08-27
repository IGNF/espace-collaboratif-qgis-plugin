# -*- coding: utf-8 -*-
"""
Registre partagé des relations ancêtre-enfant créées par les outils de découpe.

Ce module lit, dans l'espace de noms de l'interpréteur Python (``sys``),
un dictionnaire { (layer_id, new_fid): original_fid } alimenté par le plugin
de découpe (Outil_Decoupe_QGIS) lors d'une opération de découpe.

Le plugin Espace Collaboratif l'utilise, au moment de construire la transaction
POST, pour renseigner le champ ``ancestor`` d'une action ``Insert`` avec le
``cleabs`` de l'objet d'origine (retrouvé via SQLiteManager à partir du
``original_fid``).

Le dictionnaire est partagé entre les plugins chargés dans le même processus
Python via :
    getattr(sys, '_ign_cutting_ancestors', {})
"""
from __future__ import annotations

import sys

_REGISTRY_KEY = '_ign_cutting_ancestors'


def get(layer_id: str, new_fid: int):
    """
    Retourne la relation ancêtre pour un objet nouvellement créé, SANS la supprimer.

    La lecture est non-destructive afin que la relation survive à une éventuelle
    ré-tentative de transaction (la première tentative peut échouer côté serveur
    tout en conservant le buffer d'édition QGIS intact).

    L'entrée devient naturellement obsolète après le rechargement de la couche
    (``layer.reload()``) qui suit un commit réussi : QGIS réassigne alors de
    nouveaux FIDs positifs, de sorte que l'ancienne clé (layer_id, fid_négatif)
    ne sera plus jamais présentée.

    :param layer_id: Identifiant QGIS de la couche (QgsVectorLayer.id()).
    :param new_fid:  FID temporaire (négatif) du nouvel objet.
    :return: Le FID de l'objet d'origine (positif), ou None si aucune entrée
             n'est trouvée (l'objet inséré ne provient pas d'une découpe).
    """
    registry = getattr(sys, _REGISTRY_KEY, {})
    return registry.get((layer_id, new_fid), None)
