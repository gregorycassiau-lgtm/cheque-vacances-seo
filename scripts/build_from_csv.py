#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère data.json à partir d'un export Semrush « Position Tracking ».
Compatible avec l'export "Rankings overview" (une date) ET l'export "Rankings"
multi-dates : dernière date = position courante, date précédente = évolution.
Colonnes détectées par motif (nom = domaine + date), ordre indifférent.
Nom du projet via SEO_PROJECT.
"""
import os, sys, csv, glob, json, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); OUT = os.path.join(ROOT, "data.json")
INTENT = {"i": "Informationnel", "n": "Navigation", "c": "Commercial", "t": "Transactionnel"}
TYPE = {"organic": "Organique", "featured snippet": "Featured snippet",
        "site links": "Sitelinks", "local pack": "Local pack", "": ""}

def find_csv():
    if len(sys.argv) > 1: return sys.argv[1]
    c = glob.glob(os.path.join(DATA, "*.csv"))
    c = [x for x in c if re.search(r"position_tracking|rankings|semrush_export", os.path.basename(x), re.I)] or c
    if not c: sys.exit("Aucun CSV trouvé dans data/.")
    return max(c, key=os.path.getmtime)

def to_int(x):
    try: return int(float(str(x).strip()))
    except (ValueError, TypeError): return None

def to_float(x):
    try: return float(str(x).strip())
    except (ValueError, TypeError): return 0.0

def intent_txt(code):
    if not code: return ""
    return ", ".join(INTENT.get(c.strip(), "") for c in code.split("|") if INTENT.get(c.strip()))

def main():
    path = find_csv()
    lines = open(path, encoding="utf-8").read().splitlines()
    hi = next((i for i, l in enumerate(lines) if l.startswith("Keyword,")), 0)
    reader = list(csv.reader(lines[hi:])); hdr = reader[0]
    def byname(p):
        for i, h in enumerate(hdr):
            if re.search(p, h.strip(), re.I): return i
        return None
    c_kw = 0; c_tags = byname(r"^Tags$"); c_int = byname(r"^Intents$")
    c_cpc = byname(r"^CPC$"); c_vol = byname(r"^Search Volume$"); c_kd = byname(r"^Keyword Difficulty$")
    pos_col, type_col, land_col = {}, {}, {}
    for i, h in enumerate(hdr):
        h = h.strip()
        m = re.search(r"_(\d{8})$", h)
        if m and not h.endswith(("_type", "_landing", "_visibility")): pos_col[m.group(1)] = i
        mt = re.search(r"_(\d{8})_type$", h);      land = re.search(r"_(\d{8})_landing$", h)
        if mt: type_col[mt.group(1)] = i
        if land: land_col[land.group(1)] = i
    c_diff_precalc = None
    for i, h in enumerate(hdr):
        h2 = h.strip()
        if re.search(r"_difference$", h2, re.I) and "visibility" not in h2.lower():
            c_diff_precalc = i; break
    dates = sorted(pos_col.keys())
    if not dates: sys.exit("Aucune colonne de position (_AAAAMMJJ) détectée.")
    latest = dates[-1]; prev = dates[-2] if len(dates) > 1 else None
    rows, disp = [], []
    for r in reader[1:]:
        if len(r) <= c_kw or not r[c_kw].strip(): continue
        kw = r[c_kw].strip(); disp.append(kw)
        def cell(idx): return r[idx].strip() if (idx is not None and idx < len(r)) else ""
        pos = to_int(cell(pos_col[latest]))
        prevpos = to_int(cell(pos_col[prev])) if prev else None
        diff = (prevpos - pos) if (pos is not None and prevpos is not None) else None
        if diff is None and c_diff_precalc is not None and pos is not None:
            diff = to_int(cell(c_diff_precalc))
            if diff is not None: prevpos = pos + diff
        typ = cell(type_col.get(latest)); url = cell(land_col.get(latest)); cpc = cell(c_cpc)
        rows.append({"kw": kw, "vol": to_int(cell(c_vol)) or 0, "kd": to_int(cell(c_kd)),
            "intent": intent_txt(cell(c_int)), "cpc": 0.0 if cpc in ("", "n/a") else to_float(cpc),
            "pos": pos, "prev": prevpos if pos is not None else None,
            "diff": diff if pos is not None else None,
            "type": TYPE.get(typ.lower(), typ), "tags": cell(c_tags),
            "url": url if pos is not None else ""})
    ld = datetime.datetime.strptime(latest, "%Y%m%d").strftime("%Y-%m-%d")
    ranked = sum(1 for r in rows if r["pos"] is not None)
    payload = {"project": os.environ.get("SEO_PROJECT", ""),
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "Semrush Position Tracking (export)", "period": ld + " - " + ld,
        "compare_date": (datetime.datetime.strptime(prev, "%Y%m%d").strftime("%Y-%m-%d") if prev else ""),
        "count": len(rows), "ranked": ranked, "rows": rows}
    json.dump(payload, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(DATA, "keywords.txt"), "w", encoding="utf-8").write("\n".join(disp) + "\n")
    print("OK — %d mots-clés (%d positionnés) | relevé %s%s" % (len(rows), ranked, ld, (" vs " + prev) if prev else ""))

if __name__ == "__main__": main()
