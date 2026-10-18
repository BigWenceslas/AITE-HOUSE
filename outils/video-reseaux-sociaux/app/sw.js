// Met l'appli en cache pour qu'elle s'ouvre sans réseau, et reçoit les
// vidéos partagées depuis Google Photos (share_target du manifeste).

const VERSION = 'pret-a-poster-v2';
const FICHIERS = [
  './index.html', './style.css', './app.js', './mediabunny.min.mjs',
  './manifest.webmanifest', './icone.svg', './icone-192.png', './icone-512.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    for (const cle of await caches.keys()) {
      if (cle !== VERSION && cle !== 'partage') await caches.delete(cle);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  if (e.request.method === 'POST' && url.pathname.endsWith('/partage')) {
    e.respondWith((async () => {
      const donnees = await e.request.formData();
      const video = donnees.get('video');
      if (video) {
        const cache = await caches.open('partage');
        await cache.put('fichier-partage', new Response(video, {
          headers: { 'Content-Type': video.type || 'video/mp4', 'X-Nom': encodeURIComponent(video.name || 'video.mp4') },
        }));
      }
      return Response.redirect(new URL('./index.html?partage=1', self.registration.scope).href, 303);
    })());
    return;
  }

  if (e.request.method !== 'GET') return;
  // Fichiers de l'appli : cache d'abord, réseau ensuite (polices comprises).
  e.respondWith(
    caches.match(e.request, { ignoreSearch: url.origin === location.origin })
      .then((r) => r || fetch(e.request).then((rep) => {
        if (rep.ok && (url.origin === location.origin || url.hostname.endsWith('gstatic.com') || url.hostname.endsWith('googleapis.com'))) {
          const copie = rep.clone();
          caches.open(VERSION).then((c) => c.put(e.request, copie));
        }
        return rep;
      })),
  );
});
