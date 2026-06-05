// Dart Game Pro - Basic PWA Service Worker (v3.1)
// Cache shell + offline support for scores view etc. Expand for prod.
const CACHE_NAME = 'dartpro-v3.1-cache-v1';
const ASSETS = [
  '/',
  '/static/manifest.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (k !== CACHE_NAME ? caches.delete(k) : null)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((resp) => resp || fetch(event.request).catch(() => caches.match('/')))
  );
});
