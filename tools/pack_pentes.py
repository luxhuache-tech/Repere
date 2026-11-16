"""Déclivités par hectomètre, une ligne par fichier, depuis pks.csv (extras-opendata-sncf-reseau, ODbL).
Usage : python3 -I pack_pentes.py pks.csv lignes-tunnels.geojson sortie/
Format : {"c":code_ligne,"r":[[pk_début,[g0,g1,…]],…],"a":[[pk_début,[z0,z1,…]],…],"t":[[pk_début,pk_fin,nom],…]}
 r : déclivité en dixièmes de ‰, sens PK croissants, sur chaque 100 m ;
 a : altitude du terrain corrigée des tunnels (EU-DEM), en décimètres, tous les 100 m ;
 t : tunnels."""
import csv, json, os, sys, collections
src, tun, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
L = collections.defaultdict(dict); A = collections.defaultdict(dict); TU = collections.defaultdict(list)
for r in csv.DictReader(open(src)):
    c, h = r["code_ligne"].zfill(6), round(float(r["pk"]) * 10)
    if r["altitude_tunnels"] not in ("NULL", ""): A[c][h] = round(float(r["altitude_tunnels"]) * 10)
    z = r["altitude_declivites"]
    if z in ("NULL", ""): continue
    L[c][h] = float(z)
for f in json.load(open(tun))["features"]:
    p = f["properties"]
    if p.get("pkd") is None or not p.get("longueur"): continue
    TU[str(p["code_ligne"]).zfill(6)].append([round(p["pkd"], 3), round(p["pkd"] + p["longueur"] / 1000, 3), p.get("libelle") or ""])
def runs_of(Z):
    out, cur = [], None
    for h in sorted(Z):
        if cur and cur[2] == h: cur[1].append(Z[h]); cur[2] = h + 1
        else: cur = [h, [Z[h]], h + 1]; out.append(cur)
    return [[r[0] / 10, r[1]] for r in out if len(r[1]) >= 2]
tot = 0
for c in set(L) | set(A) | set(TU):
    Z = L.get(c, {})
    runs, cur = [], None
    for h in sorted(Z):
        if h + 1 not in Z: cur = None; continue
        g = round((Z[h + 1] - Z[h]) * 100)  # m sur 100 m -> dixièmes de ‰
        if abs(g) > 400: cur = None; continue  # saut aberrant (> 40 ‰)
        if cur and cur[2] == h: cur[1].append(g); cur[2] = h + 1
        else: cur = [h, [g], h + 1]; runs.append(cur)
    runs = [[r[0] / 10, r[1]] for r in runs if len(r[1]) >= 2]
    o = {"c": c, "r": runs}
    if c in A: o["a"] = runs_of(A[c])
    if c in TU: o["t"] = sorted(TU[c])
    if not runs and not o.get("a") and not o.get("t"): continue
    s = json.dumps(o, separators=(",", ":"), ensure_ascii=False)
    open(os.path.join(out, c + ".json"), "w", encoding="utf-8").write(s); tot += len(s)
print(len(os.listdir(out)), "lignes,", round(tot / 1e6, 1), "Mo")
