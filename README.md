# Présentation du plugin QGIS Espace collaboratif

## L'Espace collaboratif
L’Espace collaboratif de l’IGN (https://espacecollaboratif.ign.fr) propose deux services principaux :
* un service de signalement,
* un service d’hébergement et de contribution à des bases de données, métiers ou IGN.
#### Signalement
Le service de signalement de l’IGN (anciennement remontées d’information partagées RIPart) est un service offert par l’Institut national de l’information géographique et forestière (IGN) pour permettre à ses partenaires institutionnels de lui transmettre, de façon automatique et normalisée, des remarques concernant les données de l’Institut et qui nécessiteraient une correction ou une mise-à-jour. Ce service peut également être utilisé par les partenaires pour leurs propres besoins (mise à jour de données métiers, non destinées à l’IGN).
Chaque nouveau signalement sur une donnée IGN donne lieu à un traitement hiérarchisé au sein du service de l’IGN concerné par la remarque, qui y apportera des réponses officielles.
Un signalement contient :
* Une position géographique pour situer le signalement ;
* Un commentaire rédigé par l'auteur du signalement à l'adresse de l'IGN pour expliquer l’objet de son signalement ;
* Un statut pour situer le signalement dans la chaîne de traitement (reçu dans nos services, en cours de traitement, pris en compte…) ;
* Éventuellement un thème associé pour définir la thématique IGN et/ou la thématique métier concernées par le signalement. Il est à noter que les signalements sans thème auront le statut ‘en demande de qualification’ tant qu’ils n’auront pas un thème associé.
* Éventuellement un ou plusieurs attributs liés au thème ;
* Éventuellement des objets géométriques (ponctuels, linéaires, surfaciques) composant un croquis joint à ce signalement. Certains attributs de ce croquis peuvent aussi être joints au signalement ;
* Éventuellement de 1 à 4 fichiers joints de formats divers (pdf, doc, images…).
Chaque signalement, sauf s’il est lié à un groupe ne partageant pas ses signalements, est accessible en consultation à tous les utilisateurs sur l’Espace collaboratif. Il y possède une fiche où tous ces éléments sont visibles ainsi que les réponses apportées par l’IGN.

#### Contribution directe
L’IGN offre également à ses partenaires la possibilité d’héberger leurs données dans une base de données stockée sur l’Espace collaboratif. L’Espace collaboratif propose alors un ensemble d’outils de gestion de ces bases ainsi que des outils permettant d’entretenir et de mettre à jour les données qu’elles contiennent. On parle alors de fonctionnalités de contribution directe, accessibles depuis un « guichet » de l’Espace collaboratif.

## Rôle du plugin Espace collaboratif pour QGIS
Le plugin IGN_Espace_collaboratif est une extension pour le logiciel QGIS, qui permet depuis le SIG d'interagir directement avec le service Espace collaboratif (sans passer par le site web espacecollaboratif.ign.fr).
L'utilisateur peut ainsi depuis QGIS :
* Importer, dans sa carte courante, l'ensemble des signalements d'un lieu donné ;
* Consulter le contenu des signalements présents sur la carte ;
* Leur ajouter une réponse (s’il en a la permission) ;
* Créer de nouveaux signalements qui seront transmis au service concerné.
* Pour les utilisateurs appartenant à un groupe disposant de permissions d’écriture sur une base de données accessible sur l’Espace collaboratif via un guichet :
  * Afficher les couches paramétrées dans la carte de son groupe dans QGIS.
  * Editer les données et les enregistrer dans la base Espace collaboratif correspondante.
L'intégration du plugin dans le SIG se traduit visuellement par l’ajout d’une barre d'outils supplémentaire dédiée aux fonctionnalités du plugin, et par des couches ajoutées à la carte active et qui sont destinées à contenir les différents objets provenant de l’Espace collaboratif (ses signalements et croquis associés, couches du groupe).

## Utilisation
L'utilisation du plugin est décrite dans son [manuel utilisateur](https://github.com/IGNF/espace-collaboratif-qgis-plugin/blob/4.2.3/files/ENR_Espace_co_plugin_pour_qgis.pdf).
