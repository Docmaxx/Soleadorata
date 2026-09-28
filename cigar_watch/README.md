# Cigar Watch : alerte Telegram quand un cigare revient en stock

Surveille **Quai d'Orsay No. 54** sur 12 pages produit de boutiques suisses, toutes les ~5 min via GitHub Actions.
Envoie une alerte Telegram avec le prix et un lien direct dès qu'un stock réapparaît.

## Mise en route (10 min)

1. **Créer le bot** : sur Telegram, écrire à `@BotFather`, puis `/newbot`. Copier le **token**.
2. **Récupérer ton chat ID** : envoyer un message quelconque à ton bot, puis ouvrir
   `https://api.telegram.org/bot<TOKEN>/getUpdates` et relever `"chat":{"id": ...}`.
3. **Secrets GitHub** : dans le dépôt, aller dans *Settings → Secrets and variables → Actions → New repository secret* :
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. **Merger sur `main`** : GitHub n'exécute les tâches planifiées (cron) que sur la branche par défaut.
5. Dans *Actions → Cigar Watch → Run workflow* :
   - `test-telegram` : tu dois recevoir un message ;
   - `dry-run` : affiche l'état détecté pour chaque boutique (`in` / `out` / `unknown`) ;
   - ensuite le cron tourne seul.

## Fonctionnement

| Situation | Action |
|---|---|
| 1er passage | Un seul message récapitulatif (boutiques déjà en stock) |
| Rupture → en stock | 🚨 Alerte avec boutique, prix, lien |
| Toujours en stock | Rien (pas de spam) |
| Site injoignable ou illisible pendant ~1h | ⚠️ Alerte « surveillance aveugle » (une fois), puis ✅ quand ça revient |

L'état est conservé entre deux passages grâce au cache GitHub Actions ; aucun commit n'est ajouté au dépôt.

Détection, dans l'ordre : API Shopify (`/products/<handle>.js`), puis schema.org (JSON-LD, microdata, meta),
puis classes WooCommerce, puis mots-clés FR/DE/EN (« épuisé », « ausverkauft », « in den Warenkorb »…).

## Ajouter une boutique ou un autre cigare

Modifier `targets.json` :
- `url` : la page produit ;
- `strategy` : `"shopify"` si l'URL contient `/products/`, sinon ne rien mettre (détection automatique) ;
- `must_contain` : mots qui doivent figurer sur la page (protection contre les redirections vers une catégorie).

Pour un autre cigare, dupliquer le dossier ou adapter `product`, `must_contain` et les URLs.

## Tests

```
cd cigar_watch && python3 -m unittest -v
```
