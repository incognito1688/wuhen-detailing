/* V7.0: journal motion tiles — silent autoplay only while visible. */
(function () {
  'use strict';
  function initialize() {
    var clips = Array.prototype.slice.call(document.querySelectorAll('video.journal-motion'));
    if (!clips.length) return;

    var visible = new Set();
    var reduceMotion = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;

    function ensureSource(video) {
      if (video.dataset.loaded === 'true') return;
      var source = video.querySelector('source[data-src]');
      if (source) {
        source.src = source.getAttribute('data-src');
        source.removeAttribute('data-src');
        video.load();
      }
      video.dataset.loaded = 'true';
    }

    function sync(video) {
      var shouldPlay = visible.has(video) && !document.hidden && !(reduceMotion && reduceMotion.matches);
      if (!shouldPlay) {
        video.pause();
        return;
      }
      ensureSource(video);
      video.defaultMuted = true;
      video.muted = true;
      if (video.paused) {
        var request = video.play();
        if (request && typeof request.catch === 'function') {
          request.catch(function () { /* Keep poster visible if autoplay is blocked. */ });
        }
      }
    }

    clips.forEach(function (video) {
      video.defaultMuted = true;
      video.muted = true;
      video.loop = true;
      video.controls = false;
      video.setAttribute('aria-hidden', 'true');
      video.addEventListener('error', function () { video.classList.add('media-unavailable'); });
      var source = video.querySelector('source');
      if (source) source.addEventListener('error', function () { video.classList.add('media-unavailable'); });
    });

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.25) visible.add(entry.target);
          else visible.delete(entry.target);
          sync(entry.target);
        });
      }, { threshold: [0, 0.25, 0.55, 0.85] });
      clips.forEach(function (video) { observer.observe(video); });
    } else {
      clips.forEach(function (video) { visible.add(video); sync(video); });
    }

    document.addEventListener('visibilitychange', function () { clips.forEach(sync); });
    if (reduceMotion) {
      if (typeof reduceMotion.addEventListener === 'function') reduceMotion.addEventListener('change', function () { clips.forEach(sync); });
      else if (typeof reduceMotion.addListener === 'function') reduceMotion.addListener(function () { clips.forEach(sync); });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
}());
