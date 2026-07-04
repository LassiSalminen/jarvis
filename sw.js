const CACHE = 'jarvis-v2';
const SHELL = ['./jarvis.html', './manifest.json', './icon.svg'];

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
        // Cachetetaan onnistuneet GET-pyynnöt offline-käyttöä varten
        if (e.request.method === 'GET' && r.ok) {
          const clone = r.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return r;
      })
      .catch(() => caches.match(e.request))
  );
});
