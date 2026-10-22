#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère audit.json depuis data/audit/snapshot.json (réponse brute Semrush `snapshot`, clé "data")
et data/audit/errors_4xx.txt (une URL par ligne, issue_details issueid=2).
Usage : SEO_DOMAIN=exemple.com python3 scripts/build_audit.py"""
import os, json, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AD = os.path.join(ROOT, "data", "audit")
T = {2:"Pages en erreur 4xx",6:"Titles dupliqués",7:"Contenu dupliqué",8:"Liens internes cassés",9:"Pages non crawlées",
 13:"Images internes cassées",15:"Meta descriptions dupliquées",17:"Sitemap invalide",18:"Pages incorrectes dans le sitemap",
 32:"Canonical HTTP non redirigé (homepage)",45:"Données structurées avec erreurs",12:"Liens externes cassés",14:"Images externes cassées",
 31:"Liens externes en HTTP (site HTTPS)",102:"Title trop long",103:"H1 manquant",105:"H1 dupliqué (identique au title)",
 106:"Meta description manquante",109:"Redirections temporaires (302)",110:"Attributs ALT manquants",112:"Ratio texte/HTML faible",
 114:"Langue non déclarée",117:"Contenu trop léger (word count)",123:"Liens internes en nofollow",124:"Sitemap absent du robots.txt",
 129:"Pages non compressées",130:"Ressources internes non autorisées (robots.txt)",131:"Fichiers JS/CSS non compressés",
 134:"Trop de fichiers JS/CSS",135:"Fichiers JS/CSS non minifiés",104:"H1 multiples",137:"llms.txt absent",4:"Pages bloquées au crawl",
 202:"Liens externes en nofollow",205:"HSTS non géré",207:"Pages orphelines (sitemap)",212:"Profondeur de clic > 3",
 213:"Pages avec un seul lien interne",214:"Redirections permanentes (301)",215:"Ressources formatées en liens de page",
 216:"Liens sans texte d'ancre",217:"Liens à ancre non descriptive",218:"Liens externes en 403",219:"llms.txt mal formaté",
 223:"Contenu non optimisé",6720:""}
INTERNAL = [(213,"Pages avec un seul lien interne"),(212,"Profondeur de clic > 3"),(8,"Liens internes cassés"),
 (108,"Trop de liens sur la page"),(123,"Liens internes en nofollow"),(207,"Pages orphelines (sitemap)"),(206,"Pages orphelines (Analytics)")]
snap = json.load(open(os.path.join(AD, "snapshot.json"), encoding="utf-8"))
snap = snap.get("data", snap)
cnt = {}; sev = {}
for k, s in (("errors","error"),("warnings","warning"),("notices","notice")):
    for it in snap.get(k, []):
        cnt[it["id"]] = it["count"]; sev[it["id"]] = s
p = os.path.join(AD, "errors_4xx.txt")
errs = [l.strip() for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
date = datetime.datetime.fromtimestamp(snap["finish_date"]/1000, datetime.timezone.utc).strftime("%Y-%m-%d")
issues = [{"title": T[i], "count": c, "sev": sev[i]} for i, c in sorted(cnt.items(), key=lambda x: -x[1]) if c > 0 and i in T and T[i]
          and i not in (213,212,108,206,8,123,207)]
out = {"generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
 "domain": os.environ.get("SEO_DOMAIN",""), "audit_date": date,
 "score": snap["quality"]["value"], "pages_crawled": snap["pages_crawled"],
 "internal_checks": [{"id": i, "title": t, "count": cnt.get(i, 0)} for i, t in INTERNAL],
 "issues": issues, "errors_4xx": errs[:50]}
json.dump(out, open(os.path.join(ROOT, "audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("audit.json —", out["score"], "/100,", out["pages_crawled"], "pages,", len(issues), "problèmes, 4xx:", len(errs))
