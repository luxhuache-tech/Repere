/* Repère hors ligne : l'appli et ses bibliothèques sont gardées sur l'iPad.
   La page est rechargée du réseau quand il y en a (pour les mises à jour), sinon depuis le cache. */
const V = "repere-v2";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png",
  "./lib/leaflet.min.css", "./lib/leaflet.min.js", "./lib/pdf.min.js", "./lib/pdf.worker.min.js",
  "./data/gares.json", "./data/lignes.json", "./data/declivite.json"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => {}))))); self.skipWaiting() });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(K => Promise.all(K.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())) });
self.addEventListener("fetch", e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET") return;
  const local = u.origin === location.origin, cdn = u.hostname === "cdnjs.cloudflare.com";
  if (!local && !cdn) return; // IGN, OpenStreetMap, tuiles de carte : directement au réseau
  if (local && (r.mode === "navigate" || /\/(index\.html)?$/.test(u.pathname))) {
    // page : réseau d'abord (4 s max), sinon cache
    e.respondWith(Promise.race([fetch(r), new Promise((_, no) => setTimeout(no, 4000))])
      .then(res => { const c = res.clone(); caches.open(V).then(k => k.put(r, c)); return res })
      .catch(() => caches.match(r, { ignoreSearch: true }).then(m => m || caches.match("./index.html"))));
    return;
  }
  // bibliothèques et données : cache d'abord, mis à jour en arrière-plan
  e.respondWith(caches.match(r).then(m => {
    const net = fetch(r).then(res => { if (res.ok) { const c = res.clone(); caches.open(V).then(k => k.put(r, c)) } return res }).catch(() => m);
    return m || net;
  }));
});
