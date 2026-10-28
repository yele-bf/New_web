# Fiche d'impact — IMP-10 (Dashboard / Carte)

## Sous-ID V14
`IMP-10` — Dashboard / Carte — P3 (V5) — dépôt `New_web`

## Constat du classeur
Le dashboard ne propose que la couverture et la heatmap, pas de couche « carte de débit » ni de « carte 5G » dédiée, comme nPerf.

## Critère d'acceptation
Les couches débit et 5G sont sélectionnables et affichent les données correspondantes.

## Ce que fait cette PR
- Panneau « Carte (qualité) » sélectionnable : **Global / Download / Upload / Latence / Streaming / Navigation** — couleur de chaque zone selon l'indicateur choisi.
- Couche **5G** disponible via les filtres opérateur/technologie du panneau Réseau (technologie sortie du classeur : `5G`/`4G+`/`4G`/`3G`/`2G`), appliquée aux couches de qualité comme à la couverture.
- Carte de **couverture dédiée**, séparée des cartes de qualité (« où capte-t-on quoi ? » ≠ « c'est bien ou pas ? »).
- Popup de zone donnant le détail des mesures au clic, comme la vue tableau du dashboard.
- Tuiles plan/satellite nettoyées (repères anglais retirés, étiquettes FR du dashboard), seuils alignés sur le classeur (`SEUILS.md`), repli « position par IP » fusionné depuis la branche équipe.
- `demo_data.py` : données de démonstration réalistes pour apprécier les couches sans campagne terrain.

## Dépôts impactés
- [ ] `mobilefront`
- [ ] `mobiletest`
- [x] `New_web`
- [ ] `AI_yele`

## Validation (support imposé par le classeur)
Local (dashboard servi depuis `New_web`, backend docker-compose sur le port 8989) : bascule entre les couches de qualité et la couverture, vérification des couleurs et des seuils en thème clair et sombre, popup de zone, filtres opérateur/technologie (dont 5G), repli IP du bouton « Localisez-moi ».

## Agent et owner
- **Agent** : ZOUNGRANA Wendkuni Brice Yannick
- **Owner (colonne du classeur)** : SAWADOGO Wend-kuni Cédric / KOUNANGA Benoit / ZOUNGRANA Wendkuni Brice Yannick / OUEDRAOGO AZIZ
