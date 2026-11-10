/* Offline cache for the static HVAC Design Studio.
   Assets are cache-first; pages are served from cache instantly and quietly
   refreshed in the background so a new deploy arrives on the next visit. */
const CACHE = 'hvac-studio-v3';
const CORE = [
  './',
  './index.html',
  './icon.svg',
  './manifest.webmanifest',
  './web/app.css',
  './web/app.js',
  './web/engine.js',
  './web/r134a.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(CORE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      caches.open(CACHE).then((cache) =>
        cache.match('./index.html').then((cached) => {
          const network = fetch(request)
            .then((response) => {
              if (response && response.ok) cache.put('./index.html', response.clone());
              return response;
            })
            .catch(() => cached);
          return cached || network;
        })
      )
    );
    return;
  }

  event.respondWith(
    caches.open(CACHE).then((cache) =>
      cache.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (response && response.ok && response.type === 'basic') {
            cache.put(request, response.clone());
          }
          return response;
        });
      })
    )
  );
});
