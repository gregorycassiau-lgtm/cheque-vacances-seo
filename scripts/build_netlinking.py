#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère netlinking.json à partir des exports Backlink Analytics Semrush placés dans
data/netlinking/ :
  overview.csv    domain;ascore;backlinks;refdomains;follow;nofollow   (1 ligne)
  historical.csv  date;backlinks_num;domains_num                       (timestamps Unix)
  refdomains.csv  domain;domain_score;backlinks_num;country
  anchors.csv     anchor;domains_num;backlinks_num
  pages.csv       source_url;backlinks_num;domains_num
Tous en séparateur ';'. Réutilisable pour n'importe quel domaine.
"""
import os, sys, csv, io, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ND = os.path.join(ROOT, "data", "netlinking"); OUT = os.path.join(ROOT, "netlinking.json")
TOXIC = ["telegram", "t.me", "seo backlinks", "black-links", "link indexing",
         "traffic boost", "@seo", "@bhs", "best seo links"]

def rd(name):
    p = os.path.join(ND, name)
    if not os.path.exists(p): return []
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter=";"))

def i(x):
    try: return int(str(x).strip())
    except: return 0

def main():
    ov = rd("overview.csv")
    if not ov: sys.exit("data/netlinking/overview.csv manquant.")
    o = ov[0]; domain = o["domain"].strip()
    overview = {domain: {"ascore": i(o["ascore"]), "backlinks": i(o["backlinks"]),
        "refdomains": i(o["refdomains"]), "follow": i(o["follow"]), "nofollow": i(o["nofollow"])}}
    hist = [{"date": datetime.datetime.utcfromtimestamp(i(r["date"])).strftime("%Y-%m"),
             "backlinks": i(r["backlinks_num"]), "refdomains": i(r["domains_num"])}
            for r in rd("historical.csv")][::-1]
    refd = [{"domain": r["domain"], "ascore": i(r["domain_score"]),
             "backlinks": i(r["backlinks_num"]), "country": r.get("country", "")}
            for r in rd("refdomains.csv")]
    anchors = []
    for r in rd("anchors.csv"):
        a = r["anchor"]; tox = any(m in a.lower() for m in TOXIC)
        anchors.append({"anchor": a, "domains": i(r["domains_num"]),
                        "backlinks": i(r["backlinks_num"]), "toxic": tox})
    pages = {}
    for r in rd("pages.csv"):
        u = r["source_url"].split("?")[0].rstrip("/"); bl = i(r["backlinks_num"])
        if u not in pages or bl > pages[u]["bl"]:
            pages[u] = {"bl": bl, "rd": i(r["domains_num"])}
    payload = {"generated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "domain": domain, "overview": overview, "historical": hist, "refdomains": refd,
        "anchors": anchors, "toxic_backlinks": sum(a["backlinks"] for a in anchors if a["toxic"]),
        "pages": pages}
    json.dump(payload, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("netlinking.json:", len(pages), "pages,", len(refd), "refdomains,", len(anchors),
          "ancres, toxiques:", payload["toxic_backlinks"])

if __name__ == "__main__": main()
