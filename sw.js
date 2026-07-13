const CACHE = 'jarvis-v3';
const SHELL = ['./jarvis.html', './manifest.json', './icon.svg', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  // Siivoa vanhat välimuistiversiot
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => clients.claim())
  );
});

// Network-first: hae aina tuorein palvelimelta (ohita selaimen HTTP-välimuisti),
// fallback cacheen kun offline
self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request, { cache: 'no-cache' })
      .then(r => {
        // Cachetetaan onnistuneet GET-pyynnöt offline-käyttöä varten.
        // Opaque = cross-origin (Google Fonts, pdf.js CDN) — status ei ole
        // luettavissa, mutta cachetetaan silti, jotta ulkoasu ja PDF-tuonti
        // toimivat reissulla ilman verkkoa.
        if (e.request.method === 'GET' && (r.ok || r.type === 'opaque')) {
          const clone = r.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return r;
      })
      .catch(() => caches.match(e.request))
  );
});
