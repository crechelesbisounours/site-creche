// Crèche Les Bisounours — animations et petits comportements du site
(function () {
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  var hasIO = 'IntersectionObserver' in window;

  // Menu sur téléphone
  var burger = document.querySelector('.burger');
  var nav = document.getElementById('menu-principal');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        burger.setAttribute('aria-expanded', 'false');
        burger.focus();
      }
    });
  }

  // Apparition des sections au défilement
  var els = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if (!reduce && hasIO && els.length) {
    document.documentElement.classList.add('reveal-on');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  // Compteur animé
  var box = document.getElementById('compteur');
  if (box) {
    var out = box.querySelector('.value');
    var target = parseInt(box.getAttribute('data-target'), 10) || 0;
    var fmt = function (n) { return n.toLocaleString('fr-FR') + ' €'; };
    if (reduce || !hasIO) {
      out.textContent = fmt(target);
    } else {
      out.textContent = fmt(0);
      var running = false;
      var run = function () {
        running = true;
        var start = null, duration = 2000;
        var step = function (now) {
          if (start === null) start = now;
          var p = Math.min(1, (now - start) / duration);
          out.textContent = fmt(Math.round(target * (1 - Math.pow(1 - p, 3))));
          if (p < 1) requestAnimationFrame(step); else running = false;
        };
        requestAnimationFrame(step);
      };
      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting && !running) run(); });
      }, { threshold: 0.6 }).observe(box);
    }
  }

  // Carte Google Maps : chargée seulement à la demande du visiteur
  var mapBtn = document.getElementById('charger-carte');
  if (mapBtn) {
    mapBtn.addEventListener('click', function () {
      var map = mapBtn.closest('.map');
      var frame = document.createElement('iframe');
      frame.title = 'Carte : ' + map.getAttribute('data-label');
      frame.src = 'https://www.google.com/maps?q=' + encodeURIComponent(map.getAttribute('data-query')) + '&output=embed';
      frame.loading = 'lazy';
      frame.referrerPolicy = 'no-referrer-when-downgrade';
      frame.allowFullscreen = true;
      map.innerHTML = '';
      map.appendChild(frame);
    });
  }
})();
