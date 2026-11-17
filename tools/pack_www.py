"""Archive www.pack pour le projet Swift Playgrounds : index.html + lib/ + data/.
Format : 8 octets (taille de l'index, petit-boutiste) + index JSON {chemin: [début, longueur]} + fichiers."""
import json, os, struct, sys
root, out = sys.argv[1], sys.argv[2]
files = ["index.html"] + [os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
         for top in ("lib", "data") for d, _, fs in os.walk(os.path.join(root, top)) for f in sorted(fs) if not f.endswith(".md")]
idx, blobs, off = {}, [], 0
for f in files:
    b = open(os.path.join(root, f), "rb").read(); idx[f] = [off, len(b)]; blobs.append(b); off += len(b)
h = json.dumps(idx, separators=(",", ":"), ensure_ascii=False).encode()
with open(out, "wb") as o:
    o.write(struct.pack("<Q", len(h))); o.write(h)
    for b in blobs: o.write(b)
print(len(files), "fichiers,", round(os.path.getsize(out) / 1e6, 1), "Mo")
