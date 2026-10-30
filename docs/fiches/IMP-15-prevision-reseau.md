# IMP-15 — Carte de prévision de la qualité réseau, point par point, à Ouagadougou

| Champ | Valeur |
|---|---|
| Dépôt | `New_web` |
| Issue | [#5](https://github.com/yele-bf/New_web/issues/5) |
| Priorité / vague | P1 / V6 Évolutions lourdes |
| Owner au classeur | SANOU Zossoun Aristide Daouda |
| Branche | `imp/IMP-15-prevision-reseau` |
| Validation imposée | Dashboard |

## Constat et impact

Le dashboard montrait seulement les mesures passées. Il ne disait rien de la
qualité à attendre dans les heures suivantes, alors que la qualité varie avec la
charge du réseau (population connectée), la météo (pluie, orages, chaleur), le
relief et les fréquences.

## Correction

Ajout d'un onglet **Prévision**. Pour chaque carré d'environ 275 m de
Ouagadougou où des tests mobiles Yélé existent, il affiche le débit descendant
attendu sur les 48 prochaines heures. Un curseur choisit l'heure, et des filtres
choisissent l'opérateur et la technologie. Un clic n'importe où sur la carte
donne la prévision à cet endroit.

Débit prévu = capacité du lieu × facteur de charge de l'heure × facteur météo.
Le modèle suit l'étude « Impact de la météo, du relief, de la fréquence et de la
population sur les réseaux mobiles » :

- **Capacité du lieu** : moyenne géométrique des tests mobiles voisins (2G à 5G,
  Wi-Fi exclu), pondérée par un noyau gaussien (σ = 400 m, portée 1,2 km).
  Chaque test est d'abord ramené à une heure « neutre » : on retire l'effet de
  l'heure où il a été fait. Le relief, les obstacles et la fréquence réellement
  servie sont ainsi pris en compte par la mesure elle-même.
- **Charge** : le débit par utilisateur vaut environ la capacité de la cellule
  divisée par le nombre d'utilisateurs actifs. On part d'un profil horaire a
  priori (pointes à midi et entre 18 h et 22 h), corrigé par les mesures avec un
  poids de 30 mesures virtuelles pour l'a priori, puis lissé sur 3 heures.
- **Météo** (Open-Meteo, sans clé) :
  - la pluie ne gêne pas les fréquences mobiles (< 6 GHz) mais dégrade les
    faisceaux hertziens de collecte, selon les paliers du tableau 20 de
    l'étude ; on suppose 50 % de sites collectés par faisceau et un pic d'averse
    égal à 3 fois le cumul horaire ;
  - un orage (codes 95–99) donne un facteur de 0,85 et une alerte de coupure
    de site ;
  - au-delà de 40 °C, facteur de 0,95 et alerte de surchauffe.
- **Fiabilité** :
  - Élevée : au moins 5 mesures à moins de 300 m ;
  - Moyenne : 2 à 4 mesures, ou au moins 5 dans le rayon ;
  - Faible sinon, avec un cercle en pointillés.

L'infobulle détaille chaque facteur, la conformité au seuil ARCEP 4G (2 / 1
Mb/s) et la courbe des 48 heures.

Fichiers :

- `js/forecast.js` (nouveau) ;
- `index.html` : bouton de navigation, section `view-forecast`, script ;
- `js/app.js` : appel de `Forecast.show()` ;
- `css/style.css` : styles `fc-*`, avec variables propres pour le thème sombre.

## Critère d'acceptation

Le critère du classeur parle de bilans de liaison conformes, d'un débit minimal
garanti sous forte charge et de continuité de service. Ce qui se vérifie dans le
dashboard :

- pour une heure et un lieu de Ouagadougou, le dashboard affiche le débit
  attendu ;
- l'infobulle dit si ce débit respecte le seuil ARCEP 4G sous la charge de
  l'heure ;
- elle signale les perturbations annoncées (orage, forte pluie, chaleur).

## Validation

- **Automatisée** : `node scripts/ci/web_check.js` passe en local (12 fichiers JS
  analysés, 14 ressources de `index.html` trouvées).
- **Support imposé par le classeur (Dashboard)** : fait le 2026-10-30 en local
  (Chrome) :
  - 189 tests mobiles chargés et 90 points de prévision affichés ;
  - météo reçue d'Open-Meteo ;
  - à 00 h, 81 points sur 90 sont au-dessus de 2 Mb/s ; à 20 h (heure de
    pointe), 75 sur 90 ;
  - filtre Orange : 31 points ;
  - thème sombre vérifié ;
  - aucune erreur JavaScript.
- **Preuve** : `docs/preuves/IMP-15/` (4 captures, légendées dans le README du
  dossier).

## Limites connues

- Les modèles de propagation de l'UIT-R (affaiblissement par le relief, portée
  par fréquence) ne sont pas calculés : leur effet n'entre que par les mesures
  voisines. Aucune prévision n'est donc possible là où il n'y a pas de test
  (au-delà de 1,2 km). Réserve actée en review de la PR #13 (approche A seule, sans item de suivi).
- Le modèle n'a pas été comparé à des mesures faites après coup : sa justesse
  reste à évaluer, idéalement avec une campagne terrain.
- La part de sites collectés par faisceau hertzien (50 %) et le rapport entre
  pic d'averse et cumul horaire (3) sont des hypothèses à confirmer auprès des
  opérateurs.
- Ville couverte : Ouagadougou seulement.
- Les captures ont été faites avec une autre instance du backend, celle de
  `config.js` étant suspendue (voir le README des preuves).
