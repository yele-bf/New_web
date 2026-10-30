# Preuves — IMP-15 (prévision de la qualité réseau)

Captures produites le **30/10/2026** par SANOU Zossoun Aristide Daouda
(`angedemon`), sur le code de la branche `imp/IMP-15-prevision-reseau`. Le
dashboard était servi en local et Chrome tournait sans interface, en 1440 × 900.

Le backend `mobiletest-j0c6` de `config.js` étant suspendu sur Render le jour des
captures, `API_BASE_URL` a été pointé **pour la capture seulement** vers une
instance du même backend contenant 748 mesures, dont 189 mesures mobiles à
Ouagadougou. Ce changement de `config.js` n'est pas dans la PR. La météo vient
d'Open-Meteo pour la date des captures.

| Fichier | Ce que la capture montre | Ce qu'elle ne montre pas |
|---|---|---|
| `IMP-15_01_carte-maintenant.png` | Onglet « Prévision » : 90 points de prévision sur Ouagadougou pour l'heure en cours (ven. 30/10, 00 h), colorés selon le débit descendant attendu ; panneau avec l'heure, la météo, la charge, les filtres et la légende ; « 81 points sur 90 au-dessus de 2 Mb/s » | la qualité de la prévision (aucune mesure faite après coup pour la comparer) |
| `IMP-15_02_infobulle-point.png` | Infobulle d'un carré de 14 mesures : 24,1 Mb/s attendus, envoi et latence, conformité au seuil ARCEP 4G (2 / 1 Mb/s), courbe des 48 h, détail du calcul : capacité 19,8 Mb/s × charge 1,22 (réseau peu chargé) × météo 1 (pas de pluie, 29 °C), fiabilité « Élevée · 16 mesures » | un cas de pluie ou d'orage (aucun annoncé à Ouagadougou ce jour-là) |
| `IMP-15_03_heure-de-pointe.png` | Même carte avec le curseur sur 20 h (heure de pointe) : « 75 points sur 90 au-dessus de 2 Mb/s » au lieu de 81, effet du facteur de charge | — |
| `IMP-15_04_filtre-orange-methode.png` | Filtre opérateur « Orange » (31 points) et méthode de calcul dépliée | les autres filtres (Moov Africa, Telecel, 4G / 3G / 2G), vérifiés en local mais pas capturés |

Les valeurs se recalculent depuis `js/forecast.js` :

- profil de charge `PRIOR_LOAD`, corrigé par les mesures puis lissé ;
- paliers de pluie `RAIN_STEPS` (tableau 20 de l'étude d'impact) ;
- facteurs orage `STORM_FACTOR = 0.85` et chaleur `HEAT_FACTOR = 0.95` ;
- seuil ARCEP 4G : 2 / 1 Mb/s.
