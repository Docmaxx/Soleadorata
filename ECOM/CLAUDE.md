# Brain ECOM — instructions de comportement

Ce dossier est le "brain" de Maxime : un cerveau externe portable, indépendant
de l'outil IA utilisé (Claude, GPT, Codex, ...). Il n'y a pas de logiciel ni
de base de données — uniquement des fichiers `.md` organisés en dossiers.
Ce fichier est lu automatiquement par Claude Code à chaque session travaillant
dans `ECOM/`. Il définit comment se comporter avec ce brain.

## Structure

- `brain/core/` — identité, préférences, style, objectifs de Maxime.
- `brain/brands/` — marques, personas, produits, prix.
- `brain/knowledge/` — formations, formules, AB tests, résumés de contenus.
- `brain/memory/` — mémoire vive : lessons learned, logs de session, décisions.
- `brain/projects/` — état des projets en cours.
- `creative-lab/` — usine à créatives (systèmes de génération en masse).
- `tools/` — scripts et outils utilisés au quotidien.
- `resources/` — formations, PDFs, transcripts bruts. Volontairement hors de
  `brain/` : à lire seulement à la demande, pas systématiquement (pour ne pas
  gaspiller de contexte).

## Règles de comportement

1. **Au début d'une tâche liée à ECOM** : lire `brain/core/`, le dernier
   `brain/memory/session-log.md` et `brain/memory/lessons-learned.md` avant
   d'agir, pour ne jamais repartir de zéro.
2. **Ne jamais faire répéter Maxime.** Si une info importante (préférence,
   décision, correction, fait sur une marque/produit) apparaît dans la
   conversation, l'écrire dans le bon sous-dossier de `brain/` plutôt que de
   la garder seulement dans le contexte de chat.
3. **Lessons learned** : à chaque erreur identifiée et corrigée, l'ajouter
   dans `brain/memory/lessons-learned.md` (date, ce qui s'est passé, le fix,
   comment l'éviter la prochaine fois). Vérifier ce fichier avant de refaire
   une action similaire.
4. **Fin de session / point d'étape** : quand Maxime le demande (ou à la fin
   d'un gros morceau de travail), écrire un bref résumé dans
   `brain/memory/session-log.md` : ce qui a été fait, l'état actuel, les
   prochaines étapes. Ça permet de reprendre exactement où on en était, même
   dans une nouvelle conversation.
5. **"Retiens ça"** : quand Maxime dit explicitement de retenir une info,
   l'enregistrer immédiatement dans le fichier `brain/` le plus pertinent.
6. **Qualité > quantité** : ne stocker que des ressources et infos vraiment
   pertinentes dans `brain/`. Ne pas y mettre du bruit.
7. **Jamais de secrets** : aucun mot de passe, clé API ou token dans les
   fichiers `brain/`.
8. **Skills** : quand un process se répète et se stabilise (ex: un format de
   brief créatif validé plusieurs fois), le proposer à Maxime sous forme de
   skill Claude Code réutilisable plutôt que de le refaire manuellement à
   chaque fois.
