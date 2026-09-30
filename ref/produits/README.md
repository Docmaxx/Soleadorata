# ref/produits — photos produits (source de vérité)

Un sous-dossier par produit/SKU, en kebab-case :

```
ref/produits/
  gummies-bronzants-30j/
    packshot-face.png        # fond blanc/transparent, HD (≥ 2000 px)
    packshot-dos.png         # étiquette lisible (ingrédients, claims)
    gummy-macro.jpg          # le gummy seul, gros plan texture
    lifestyle-01.jpg         # en situation (main, plage, salle de bain)
    notes.md                 # nom exact, dosage, couleurs, claims autorisés
```

Règles :
- PNG détouré de préférence pour les packshots ; JPG pour le lifestyle.
- Nom de fichier = `type-angle-nn.ext` (packshot, macro, lifestyle, texture).
- Ne jamais modifier ces fichiers : les versions retouchées/générées vont dans `runs/`.
