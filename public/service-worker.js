const CACHE_NAME = 'anchor-pos-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/offline.html',
  '/favicon.ico',
];

// Install SW and cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

// Intercept requests
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request).then(response =>
      response || caches.match('/offline.html')
    ))
  );
});

// Activate and cleanup
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) =>
      Promise.all(
        keyList.map((key) => key !== CACHE_NAME && caches.delete(key))
      )
    )
  );
});
