# CLAUDE.md — Studio Soleadorata

Studio de production créative pour **Soleadorata** (gummies bronzants) : advertorials, statiques et vidéos ads (Meta, TikTok).

## Arborescence

| Dossier | Rôle | Règle |
|---|---|---|
| `ref/produits/<sku>/` | Photos produits originales (packshots, macro, lifestyle) + `notes.md` | **Lecture seule.** Source de vérité visuelle. |
| `ref/marque/` | Logo, palette, typos, tone of voice, claims autorisés | Lecture seule. |
| `ref/inspiration/` | Ads concurrentes, moodboards, hooks qui performent | Libre. |
| `script/` | Scripts vidéo, advertorials, copies d'ads, hooks | Un fichier par asset : `AAAA-MM-JJ_format_angle.md` |
| `skills/` | Process réutilisables (prompts, frameworks, checklists) | Un dossier par skill avec `SKILL.md`. |
| `runs/` | Sorties de production (images/vidéos générées, itérations) | Un dossier par run : `runs/AAAA-MM-JJ_nom-du-run/` |

## Règles de production

1. **Fidélité produit** : toute génération image/vidéo part d'une photo de `ref/produits/`. Packaging, couleurs et texte d'étiquette ne doivent jamais être inventés.
2. **Claims** : n'utiliser que les allégations listées dans `ref/marque/` (compléments alimentaires = règlement UE 1924/2006 ; pas de promesse médicale, pas de « remplace la crème solaire »).
3. **Traçabilité** : chaque run contient un `brief.md` (objectif, angle, cible, refs utilisées, prompts/modèles, résultat retenu).
4. **Ne jamais écraser** : on versionne (`v1`, `v2`…) plutôt que de remplacer.
5. **Langue** : FR par défaut ; réponses courtes, structurées, orientées décision.

## Workflow type

`ref/` (inputs) → `script/` (angle + copy) → `runs/` (génération + sélection) → export final dans `runs/<run>/final/`.
