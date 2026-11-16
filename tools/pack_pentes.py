"""Déclivités par hectomètre, une ligne par fichier, depuis pks.csv (extras-opendata-sncf-reseau, ODbL).
Usage : python3 -I pack_pentes.py pks.csv sortie/
Format : {"c":code_ligne,"r":[[pk_début,[g0,g1,…]],…]} ; g en dixièmes de ‰, sens PK croissants, sur chaque 100 m."""
import csv, json, os, sys, collections
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
L = collections.defaultdict(dict)
for r in csv.DictReader(open(src)):
    z = r["altitude_declivites"]
    if z in ("NULL", ""): continue
    L[r["code_ligne"].zfill(6)][round(float(r["pk"]) * 10)] = float(z)
tot = 0
for c, Z in L.items():
    runs, cur = [], None
    for h in sorted(Z):
        if h + 1 not in Z: cur = None; continue
        g = round((Z[h + 1] - Z[h]) * 100)  # m sur 100 m -> dixièmes de ‰
        if abs(g) > 400: cur = None; continue  # saut aberrant (> 40 ‰)
        if cur and cur[2] == h: cur[1].append(g); cur[2] = h + 1
        else: cur = [h, [g], h + 1]; runs.append(cur)
    runs = [[r[0] / 10, r[1]] for r in runs if len(r[1]) >= 2]
    if not runs: continue
    s = json.dumps({"c": c, "r": runs}, separators=(",", ":"))
    open(os.path.join(out, c + ".json"), "w").write(s); tot += len(s)
print(len(os.listdir(out)), "lignes,", round(tot / 1e6, 1), "Mo")
