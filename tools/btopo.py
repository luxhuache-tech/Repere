"""Altitude des voies (BD TOPO IGN, tronçons de voie ferrée principale) le long de chaque ligne de data/lignes.json.
Sortie : data/btopo/<code_ligne>.json = {"c": code, "p": [[lon*1e5, lat*1e5, z*10], …]} un point tous les 100 m.
Source : IGN BD TOPO via le service WFS de la Géoplateforme (Licence Ouverte Etalab 2.0).
Usage : python3 tools/btopo.py [regex_codes]   (lancé par .github/workflows/btopo.yml)"""
import json, math, os, re, sys, time, urllib.request, urllib.parse, concurrent.futures as cf, statistics
WFS = "https://data.geopf.fr/wfs/ows"
L = json.load(open("data/lignes.json"))["lignes"]
pat = re.compile(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else None
os.makedirs("data/btopo", exist_ok=True)
M = 111320.0
def resample(part, step=100.0):
    out = [tuple(part[0])]; carry = 0.0
    for (x0, y0), (x1, y1) in zip(part, part[1:]):
        c = math.cos(math.radians(y0)); dx, dy = (x1 - x0) * c * M, (y1 - y0) * M; d = math.hypot(dx, dy); t = step - carry
        while t <= d: out.append((x0 + (x1 - x0) * t / d, y0 + (y1 - y0) * t / d)); t += step
        carry = (carry + d) % step if d else carry
    return out
lines = {}
for l in L:
    if pat and not pat.search(l[0]): continue
    for part in l[5]:
        if len(part) >= 2: lines.setdefault(l[0], []).extend(resample(part))
CW, CH = 0.04, 0.03
cell = lambda x, y: (math.floor(x / CW), math.floor(y / CH))
cells = sorted({cell(x, y) for P in lines.values() for x, y in P})
print(len(lines), "lignes,", sum(map(len, lines.values())), "points,", len(cells), "cases", flush=True)
def fetch(c):
    x0, y0 = c[0] * CW - .0005, c[1] * CH - .0005; bb = [x0, y0, x0 + CW + .001, y0 + CH + .001]
    q = urllib.parse.urlencode({"SERVICE": "WFS", "VERSION": "1.1.0", "REQUEST": "GetFeature", "TYPENAME": "BDTOPO_V3:troncon_de_voie_ferree",
        "MAXFEATURES": "10000", "OUTPUTFORMAT": "application/json", "BBOX": ",".join("%.5f" % v for v in bb) + ",EPSG:4326"})
    for a in range(5):
        try:
            with urllib.request.urlopen(WFS + "?" + q, timeout=90) as r: J = json.load(r); break
        except Exception as e: time.sleep(3 + 5 * a)
    else: return c, None
    segs = []
    for f in J.get("features", []):
        p, g = f.get("properties") or {}, f.get("geometry")
        if not g or (p.get("etat_de_l_objet") or "En service") != "En service": continue
        if not re.search(r"principale|LGV|grande vitesse", p.get("nature") or "", re.I): continue
        if (p.get("precision_altimetrique") or 0) > 3: continue
        for Lc in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            for A, B in zip(Lc, Lc[1:]):
                if len(A) > 2 and len(B) > 2 and A[2] > -500 and B[2] > -500: segs.append((A, B))
    return c, segs
SEG = {}; done = 0; t0 = time.time()
with cf.ThreadPoolExecutor(8) as ex:
    for c, s in ex.map(fetch, cells):
        SEG[c] = s; done += 1
        if done % 200 == 0: print(done, "/", len(cells), round(time.time() - t0), "s", flush=True)
def zat(x, y):
    cs = math.cos(math.radians(y)); zz = []
    for c in {cell(x + dx, y + dy) for dx in (-.0003, .0003) for dy in (-.0003, .0003)}:
        for A, B in SEG.get(c) or []:
            ax, ay, bx, by = (A[0] - x) * cs * M, (A[1] - y) * M, (B[0] - x) * cs * M, (B[1] - y) * M
            if min(ax, bx) > 15 or max(ax, bx) < -15 or min(ay, by) > 15 or max(ay, by) < -15: continue
            dx, dy = bx - ax, by - ay; l2 = dx * dx + dy * dy; t = max(0, min(1, -(ax * dx + ay * dy) / l2)) if l2 else 0
            if (ax + t * dx) ** 2 + (ay + t * dy) ** 2 <= 225: zz.append(A[2] + t * (B[2] - A[2]))
    return statistics.median(zz) if zz else None
tot = ok = 0
for code, P in lines.items():
    out = []
    for x, y in P:
        z = zat(x, y); tot += 1
        if z is not None: ok += 1; out.append([round(x * 1e5), round(y * 1e5), round(z * 10)])
    if out: json.dump({"c": code, "p": out}, open("data/btopo/%s.json" % code, "w"), separators=(",", ":"))
print("points avec altitude :", ok, "/", tot, "| cases sans réponse :", sum(1 for v in SEG.values() if v is None))
