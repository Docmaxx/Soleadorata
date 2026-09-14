# Framework scaling 0 → 30K$/jour (media buying)

Source : formation media buying, 4 phases chronologiques à ne pas sauter :
Testing → Scaling → Sécurisation (Bitcap/Costcap) → Industrialisation (ABO
testing). Principe directeur : pas d'émotion, décisions cartésiennes, ne jamais
laisser tourner un test mort par peur de couper.

## Phase 1 — Testing

**Structure** : 1 CBO, budget 100$/jour (50-75$ acceptable), 2 adsets (1
statiques, 1 vidéos), objectif achat, optimisation purchase.
**Volume créas** : ~15 statiques + ~10 vidéos (minimum 5-15 vidéos — en 2026 la
vidéo scale mieux que la statique).
**Pourquoi CBO et pas ABO en testing** : Meta arbitre mieux en CBO depuis
Andromeda ; juger au niveau de la campagne globale, jamais créa par créa (une
créa qui a beaucoup spend mais peu rentable peut quand même porter toute la
CBO — ne pas la couper isolément).

### Règles Go/No-Go

| Étape | Condition | Décision |
|---|---|---|
| J+1, 100$ dépensés | 0 ATC sur toute la CBO | Vérifier setup (ciblage, checkout, shipping, clarté de l'offre/prix/preuve sociale) d'abord. Si setup OK, laisser tourner encore une demi-journée puis couper si toujours nul. |
| J+3, 300$ cumulés | Rentable | Scale + itère (phase 2) |
| J+3, 300$ cumulés | Break-even | Continuer 1 semaine en itérant 80/20 (80% sur le concept qui marche, 20% nouveaux concepts) |
| J+3, 300$ cumulés | Mort (pas de vente/ATC) | Couper, passer à autre chose |
| Après 1 semaine | Marge >15% | Scale (phase 2) |
| Après 1 semaine | Toujours break-even | Forcer 1 semaine de plus en améliorant la page produit (heatmaps/session recording) |
| Après 2 semaines | Toujours pas rentable | Couper définitivement |

**Règle d'or** : personne n'a jamais scalé une marque dont les stats jour 1-2
étaient catastrophiques (CTR nul, CPC/CPM élevés, zéro ATC). Si c'est mort,
couper vite préserve la trésorerie plutôt que de s'acharner "au cas où".

## Phase 2 — Scaling

Même CBO, on alimente avec de nouveaux adsets (convention de nom : format +
angle + date) à chaque nouveau batch de créas.

**Règle de scaling** : +25% de budget tous les 2 jours tant qu'on reste
au-dessus de l'objectif de marge (15% mini). Ne jamais redescendre de palier
avant d'avoir laissé tourner 2 jours pleins au nouveau palier (Andromeda peut
avoir une mauvaise journée isolée).

**Soft scaling** (les bons jours, capitaliser dans la journée même, sans
attendre 2 jours) : si le ROAS tient, monter le budget plusieurs fois dans la
même journée (ex: 200→400→800$ entre 9h et 14h) pour franchir des paliers et
donner à l'algo le signal "je peux vendre plus en restant rentable" — le
lendemain, redémarrer directement sur un palier plus haut plutôt que de repartir
de la base.

**Alimentation créative — condition de survie** : sans nouvelles créas, une CBO
s'essouffle en 2-3 semaines. Volume recommandé : **25 à 100 créas/semaine**
(minimum absolu : 25). Beaucoup de statiques (faciles à produire) + vidéos en
volume via IA.

**Ratio itération** : 80% itération du concept gagnant / 20% nouveaux concepts
au début (jamais 100/0 — les concepts s'épuisent, il faut toujours semer de
nouvelles pistes). Ce ratio glisse vers 50/50 ou 60/40 une fois la première
vague de scaling passée (après ~1-1,5 mois, quand la redescente naturelle
arrive et qu'il faut retester plus large).

**5 méthodes d'itération directe** :
1. Hook swap — même body/angle/avatar qui marche, tester plein de hooks
   différents (spy concurrents/niche pour trouver des hooks qui marchent,
   reproduire avec des outils IA)
2. Réécriture complète du script sur le même angle/personnage (via IA)
3. Sur statiques : swap des titres
4. Sur statiques : swap des visuels
5. (Avatars multiples) : une fois plusieurs winners trouvés, explorer
   horizontalement — landing pages et pages produit dédiées par avatar

## Phase 3 — Sécurisation (Bitcap / Costcap)

Pour les comptes bloqués entre 3-5K$/jour qui n'arrivent pas à passer un
palier. Objectif : isoler les meilleures créas de la main CBO dans des
campagnes à enchère manuelle pour presser un maximum de marge dessus.

**Bid Cap (Bitcap)** : plafond de CPA **strict** — Meta ne dépense jamais
au-dessus. Protège la marge à fond, mais peut sous-dépenser si l'audience à ce
CPA est difficile à trouver.

**Cost Cap (Costcap)** : objectif de CPA **souple** — Meta peut dépasser
d'environ 20-25% pour trouver plus de volume. Pousse plus de spend, marge un
peu moins protégée mais souvent rentable quand même.

### Règle de répartition (à faire chaque lundi, sur l'analyse hebdo de la CBO)

| Marge de la créa | Destination |
|---|---|
| > 15% (idéalement 20%+) | Bitcap — "presser comme un citron" |
| 7,5% – 15% | Costcap — pousser le volume |
| 0% – 7,5% | Rester dans la main CBO, ne pas déplacer |

### Setup Bitcap
- Nouvelle campagne achat, stratégie d'enchère = limite d'enchère, CPA initial
  = celui qui garantit ~20% de marge
- Budget affiché 500-1000$/jour (ne sera quasiment jamais atteint au début)
- 1 CBO, 1 adset, toutes les meilleures créas dedans
- Laisser tourner 3 jours sans toucher
- Si $0 de spend : augmenter le CPA de 1$ par jour jusqu'à ce que ça commence à
  dépenser (le "sweet spot") — puis ne plus toucher, laisser stabiliser
- Quand le spend approche le budget plafond → doubler le budget (500→1000$)
- Alimentation hebdo : nouvel adset à chaque batch, même principe que la CBO

### Setup Costcap
Identique, mais CPA initial fixé pour ~15% de marge (plus souple que le
Bitcap), budget 500$/jour, même méthode d'ajustement par palier de 1$.

## Phase 4 — Industrialisation (ABO testing), seulement à partir de 20-30K$/jour

**Le problème à ce palier** : volume de créas trop important (100+ ads/semaine)
pour que la main CBO isole correctement la donnée par créa — beaucoup d'ads
avec peu de spend individuel, impossible d'analyser proprement ce qui marche
vraiment, alors qu'on paie une équipe créative pour produire ces concepts.

**Pourquoi pas avant** : tester en ABO trop tôt tue le budget de testing sans
matelas de profit pour l'absorber. À 20-30K$/jour, la marge quotidienne rend
le coût d'une ABO de test négligeable — et c'est là que ça devient nécessaire
pour ne pas perdre le fil du process créatif.

**Setup** : campagne ABO dédiée à l'analyse (jamais de Bitcap/Costcap dessus),
objectif achat, plusieurs adsets avec budget propre de 30-50$/adset/jour.

**Règles Go/No-Go** (mêmes principes que phase 1) :
- J+1 sans vente → couper, sauf signal fort (bon CTR, CPC faible, ATC élevé) →
  laisser 1 jour de plus puis couper si toujours mort
- Sur 1 semaine : rentable si marge ≥ 7,5% minimum (15-20-30% = très bien)

**Promotion vers le scaling** : après 7 jours, les créas gagnantes de l'ABO
partent dans un nouvel adset de la CBO de scaling (tri par hook/avatar/date).

**Point de vigilance — ne pas couper trop vite dans l'ABO** : quand une créa
passe en CBO, la laisser tourner en parallèle dans l'ABO tant qu'elle n'a pas
prouvé qu'elle spend bien en CBO (sinon on perd la donnée de comparaison). Une
fois qu'elle spend bien en CBO → la couper de l'ABO. Si elle ne spend pas en
CBO → continuer à la scaler dans l'ABO elle-même, et l'envoyer directement en
Bitcap/Costcap si elle atteint les seuils de marge.

## Les erreurs qui tuent le budget (à éviter absolument)

1. **S'acharner sur un test mort** — ne jamais laisser tourner 4 jours un
   testing éclaté au sol
2. **Scaler trop vite** — pas de doublement de budget jour 1-2, respecter la
   règle des 2 jours
3. **Mettre des créas pourries en Bitcap/Costcap et monter le CPA à l'aveugle**
   — garbage in, garbage out, ça finit par dépenser mais en perdant de l'argent
4. **Tester en ABO avant 20-30K$/jour** — brûle le budget de test avant d'avoir
   le matelas de profit pour l'absorber

## Récap chronologique

1. Testing : CBO, 2 adsets (vidéo/statique), 100$/j, 7 jours
2. Si rentable → Scaling : +25% tous les 2 jours, 25-100 créas/semaine, jusqu'à
   3-5K$/jour stable
3. À 3-5K$/jour stable → Bitcap (meilleures créas) + Costcap (créas correctes),
   alimentation hebdo (chaque lundi)
4. À 20-30K$/jour → ABO testing dédié pour retrouver une analyse créa par créa
   propre, réinjection des winners dans la CBO de scaling
