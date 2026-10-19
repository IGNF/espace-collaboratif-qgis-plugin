# -*- coding: utf-8 -*-
"""
Lecture de l'information "ancestor" (cleabs de l'objet d'origine) portée directement par
la feature nouvellement insérée lors d'une découpe (plugin Outil_Decoupe_QGIS), via un
champ caché local ajouté au schéma de la couche (voir le module homonyme de ce plugin).

Remplace l'ancien registre partagé en mémoire (sys._ign_cutting_ancestors) : la valeur
voyage avec la feature elle-même, ce qui la rend indépendante du FID temporaire et
résistante à un reload/rollback survenant entre la découpe et l'envoi.
"""
from __future__ import annotations

# Doit rester identique à Outil_Decoupe_QGIS/traitement/ancestor_field.py
FIELD_NAME = "_ign_ancestor_cleabs"


def get_ancestor(feature):
    """
    Retourne le cleabs de l'objet d'origine porté par *feature*, ou None si absent
    (champ non présent sur la couche, ou objet non issu d'une découpe).
    """
    idx = feature.fields().indexOf(FIELD_NAME)
    if idx < 0:
        return None
    value = feature.attribute(idx)
    if value is None or str(value) in ("NULL", ""):
        return None
    return value
