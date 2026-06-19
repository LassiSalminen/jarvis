const CACHE = 'jarvis-v1';
const SHELL = ['./jarvis.html', './manifest.json', './icon.svg'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(clients.claim());
});

// Network-first: yritetään verkkoa, fallback cacheen
self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request)
      .then(r => {
        // Cachetetaan onnistuneet GET-pyynnöt
        if (e.request.method === 'GET' && r.ok) {
          const clone = r.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return r;
      })
      .catch(() => caches.match(e.request))
  );
});
