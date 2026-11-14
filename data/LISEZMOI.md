# Données de géométrie

`gares.json` et `lignes.json` sont tirés de l'open data de SNCF Réseau (jeux « Liste des gares » et « Lignes par type », ressources.data.sncf.com), compactés pour l'appli :

- gares : nom, code ligne, rang de tronçon, PK, longitude, latitude ;
- lignes : code ligne, rang de tronçon, libellé, PK début, PK fin, tracé simplifié (tolérance 1,5 m, coordonnées au 1/100 000e de degré).

Source : SNCF Réseau. Ces données ne sont pas destinées à la navigation en temps réel : le PK calculé par Repère est une aide, jamais une référence.
