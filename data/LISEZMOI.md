# Données de géométrie

`gares.json` et `lignes.json` sont tirés de l'open data de SNCF Réseau (jeux « Liste des gares » et « Lignes par type », ressources.data.sncf.com), compactés pour l'appli :

- gares : nom, code ligne, rang de tronçon, PK, longitude, latitude ;
- lignes : code ligne, rang de tronçon, libellé, PK début, PK fin, tracé simplifié (tolérance 1,5 m, coordonnées au 1/100 000e de degré).

Source : SNCF Réseau. Ces données ne sont pas destinées à la navigation en temps réel : le PK calculé par Repère est une aide, jamais une référence.

`declivite.json` vient du jeu « Caractéristique des voies et déclivité » (SNCF Réseau, état au 31/12/2021) : code ligne, rang de tronçon, voie, PK début, PK fin, déclivité en ‰ dans le sens des PK croissants (rampe positive, pente négative). Il ne couvre que les portions mesurées.

Le profil en long est complété par l'appli au moment de l'import : altitudes du terrain IGN (Géoplateforme, calcul altimétrique) et tunnels/ponts ferroviaires OpenStreetMap (© contributeurs OpenStreetMap, ODbL) via Overpass.

## pentes/
Un fichier par code ligne, tiré du dépôt [extras-opendata-sncf-reseau](https://github.com/nicolaswurtz/extras-opendata-sncf-reseau) de Nicolas Wurtz (licence ODbL 1.0), produit par `tools/pack_pentes.py` :

- `r` : déclivité par hectomètre (colonne `altitude_declivites` de `pks.csv` : déclivités SNCF Réseau ramenées à la ligne), en dixièmes de ‰ dans le sens des PK croissants ; sauts de plus de 40 ‰ écartés ;
- `a` : altitude du terrain corrigée des tunnels (EU-DEM, colonne `altitude_tunnels`), en décimètres, tous les 100 m ; sert quand l'IGN est injoignable ;
- `t` : tunnels (`lignes-tunnels.geojson`) : PK début, PK fin, nom.

Les « localités » du même dépôt ont été essayées comme points de calage et écartées : elles dégradaient la précision du PK.
