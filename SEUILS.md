# SEUILS.md — Référentiel des seuils de qualité Yélé

Document de référence des seuils utilisés par le dashboard. Chaque borne est
justifiée par un repère externe ou une donnée terrain. **Toute modification
future doit être tracée en fin de document** (§5) : date, valeur avant/après,
motif, données qui l'ont motivée.

Code concerné : `js/quality.js` (objet `USAGES`), `js/map.js` (score global,
couverture). L'affichage ne mentionne jamais les justifications réglementaires
(règle : pas de jargon ARCEP/SDAN/THD à l'écran).

---

## 1. Débit descendant (mobile et fixe)

| Niveau | Libellé | Tranche |
|---|---|---|
| 1 | Lent | 0 – 5 Mbps |
| 2 | Moyen | 5 – 10 Mbps |
| 3 | Rapide | 10 – 30 Mbps |
| 4 | Très rapide | ≥ 30 Mbps |

Justification des bornes :

- **30 Mbps** — seuil du très haut débit (doctrine SDAN / repère international
  du THD). En fixe, il distingue une connexion « moderne » d'une connexion
  modeste.
- **5 Mbps** — plancher du streaming vidéo HD courant.
- **10 Mbps** — confort multi-usages (HD + navigation simultanée).

Validation externe : baromètre nPerf Burkina Faso 2026 — Orange fixe
62,88 ↓ / 10,94 ↑ Mb/s, Moov 22,42 ↑, CANAL+ 20,55 ↓. L'échelle classe ces
moyennes marché dans les deux niveaux supérieurs.

**Limite connue (à surveiller)** : les données terrain actuelles du dashboard
sont toutes WiFi à Ouagadougou. Le classement réel de la **4G mobile, et
encore plus en zone rurale**, n'est pas encore observé. Si les tests 4G réels
s'empilent dans « Lent » (0-5), la borne 5 Mbps sera à questionner — voir §5.

## 2. Débit montant

| Niveau | Libellé | Tranche |
|---|---|---|
| 1 | Lent | 0 – 1,5 Mbps |
| 2 | Moyen | 1,5 – 5 Mbps |
| 3 | Rapide | 5 – 10 Mbps |
| 4 | Très rapide | ≥ 10 Mbps |

L'upload est structurellement 3 à 10 fois plus faible que le download sur
réseau mobile ; appliquer l'échelle du descendant classifierait « lent » des
uploads corrects. Repères : 1,5 Mbps = visioconférence, 5 = partage de
connexion, 10 = envoi de fichiers lourds sans friction.

## 3. Latence

| Niveau | Libellé | Tranche |
|---|---|---|
| 4 | Réactivité excellente | < 30 ms |
| 3 | Réactivité bonne | 30 – 80 ms |
| 2 | Réactivité limitée | 80 – 200 ms |
| 1 | Réactivité faible | > 200 ms |

Échelle inversée (plus court = meilleur), comme la navigation web.
30 ms sépare le réseau sain du réseau chargé ; au-delà de 200 ms, visio et jeu
deviennent pénibles. La latence mobile réelle descend rarement sous ~20 ms.

## 4. Usages qualitatifs

- **Streaming** (score 0-100) : ≥ 80 fluide / 60-80 bon / 40-60 limité /
  < 40 difficile.
- **Navigation** (temps de chargement) : < 2 s très fluide / 2-5 s fluide /
  5-10 s lente / > 10 s très lente.
- **Score global** = moyenne des **niveaux** (1-4) de débit ↓ (référentiel
  selon mobile/fixe), débit ↑ et latence, mesures absentes ignorées. Les
  niveaux sont moyennés, pas les valeurs brutes : un excellent débit ne
  compense pas une latence pourrie, et un seul indicateur ne peut pas masquer
  les autres.

---

## 5. Journal des révisions et évolutions candidates

**Aucune révision à ce jour** (seuils posés en octobre 2026, à la création du
dashboard façon nPerf).

### Procédure de révision

1. Regrouper les données terrain : au moins 30 tests réels par segment
   concerné (ex. 4G mobile Ouaga, 3G rural).
2. Comparer la distribution aux tranches : si un quartile des mesures tombe
   dans le même niveau que le tiers supérieur d'une autre techno, la tranche
   ne sépare plus rien → réviser.
3. Noter ici : date, borne avant/après, motif, taille d'échantillon.
4. Mettre à jour `USAGES` dans `js/quality.js` ET ce document.

### Évolutions candidates (décisions en attente de données)

- **Score global « expérience »** (candidate) : deuxième mode combinant
  débit ↓ + ↑ + latence **+ streaming + navigation**, pour comparer l'expérience
  réelle (ce que l'utilisateur vit) au score réseau (ce que le lien débite).
  Questions à trancher avant d'implémenter : comment compter un test sans
  streaming (mesure absente → moyenne biaisée ?), et placement dans le panneau
  (déjà 7 types de carte). À décider après le test terrain 4G.
- **Filtre par quartier** (candidate) : le filtre Lieu est à la ville car
  Nominatim ne documente pas tous les quartiers. Le jour où Ouagadougou seule
  porte des centaines de tests, créer `quartiers-ouaga.json` (liste manuelle
  des ~30 quartiers principaux) et mapper les libellés géocodés dessus.
  Fichier test de référence : les 30 quartiers sont connus et stables.
- **État « partiel » visible** (candidate, mineure) : un test avec au moins
  une mesure mais pas toutes (ex. download OK, upload absent) est déjà traité
  correctement en interne (mesure absente ignorée, niveau 0 = gris) mais rien
  ne le nomme à l'écran. Ajouter la mention « mesures partielles » dans le
  popup si les cas apparaissent dans les données réelles.
- **Test mobile responsive** (à faire) : le panneau replié existe déjà
  (bouton `<`, 46px), mais le comportement à 375px de large (panneau ouvert
  260px) n'a pas été vérifié sur un vrai téléphone.
