# Données de géométrie

`gares.json` et `lignes.json` sont tirés de l'open data de SNCF Réseau (jeux « Liste des gares » et « Lignes par type », ressources.data.sncf.com), compactés pour l'appli :

- gares : nom, code ligne, rang de tronçon, PK, longitude, latitude ;
- lignes : code ligne, rang de tronçon, libellé, PK début, PK fin, tracé simplifié (tolérance 1,5 m, coordonnées au 1/100 000e de degré).

Source : SNCF Réseau. Ces données ne sont pas destinées à la navigation en temps réel : le PK calculé par Repère est une aide, jamais une référence.

`declivite.json` vient du jeu « Caractéristique des voies et déclivité » (SNCF Réseau, état au 31/12/2021) : code ligne, rang de tronçon, voie, PK début, PK fin, déclivité en ‰ dans le sens des PK croissants (rampe positive, pente négative). Il ne couvre que les portions mesurées.

Le profil en long est complété par l'appli au moment de l'import : altitudes du terrain IGN (Géoplateforme, calcul altimétrique) et tunnels/ponts ferroviaires OpenStreetMap (© contributeurs OpenStreetMap, ODbL) via Overpass.

## pentes/
Déclivité par hectomètre, un fichier par code ligne (`{"c": code, "r": [[pk_début, [g, …]], …]}`, g en dixièmes de ‰ dans le sens des PK croissants, sur chaque tronçon de 100 m). Tirée de la colonne `altitude_declivites` de `pks.csv` du dépôt [extras-opendata-sncf-reseau](https://github.com/nicolaswurtz/extras-opendata-sncf-reseau) de Nicolas Wurtz : déclivités SNCF Réseau (open data) ramenées à la ligne. Licence ODbL 1.0. Sauts de plus de 40 ‰ écartés. Produit par `tools/pack_pentes.py`.
