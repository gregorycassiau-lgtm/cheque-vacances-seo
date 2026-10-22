# Cheque-vacances.com — SEO Cockpit

Tableau de bord SEO statique (positions, statistiques, priorités, netlinking, maillage & technique) généré à partir des exports Semrush.

## Contenu
- `index.html` — interface (5 onglets)
- `data.json` — suivi de positions (57 mots-clés, relevé 2026-09-05)
- `netlinking.json` — Authority Score 42, 22 228 backlinks / 2 030 domaines référents, 0,4 % de toxiques (sain)
- `audit.json` — santé technique (score 70/100, 259 pages crawlées, snapshot 2026-09-04)
- `ChequeVacances-cockpit-standalone.html` — version autonome, s'ouvre sans serveur

## Mise à jour
1. Remplacer `data/semrush_export.csv` par un nouvel export Semrush (Position Tracking → Rankings overview)
2. `SEO_PROJECT="Cheque-vacances.com" python3 scripts/build_from_csv.py`
3. (optionnel) Rejouer le netlinking (target=cheque-vacances.com, target_type=root_domain) via le MCP Semrush puis `python3 scripts/build_netlinking.py`
4. (optionnel) Site Audit : projet Semrush 16068462

## Déploiement Netlify
Site : cheque-vacances-seo.netlify.app (créé le 2026-09-06)

## Points d'attention
- Netlinking sain (0,4 % de toxiques) — pas d'urgence de désaveu.
- 122 pages orphelines côté sitemap et 99 pages avec un seul lien interne — écart notable entre le nombre de pages du site et celles réellement maillées, à creuser (probablement les pages `af_faq-category/*` visibles dans les backlinks mais absentes du maillage).
