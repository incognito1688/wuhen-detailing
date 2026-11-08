/* V6.7: PR-1 through PR-5 are silent, non-interactive motion illustrations. */
(function () {
  'use strict';
  function initialize() {
    var clips = Array.prototype.slice.call(document.querySelectorAll('video.pr-motion'));
    if (!clips.length) return;

    var visible = new Set();
    var reduceMotion = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;

    function sync(video) {
      var shouldPlay = visible.has(video) && !document.hidden && !(reduceMotion && reduceMotion.matches);
      if (!shouldPlay) {
        video.pause();
        return;
      }
      // The MP4 files contain no audio stream. Muted is an additional autoplay safeguard.
      video.defaultMuted = true;
      video.muted = true;
      if (video.preload === 'none') video.preload = 'auto';
      if (video.paused) {
        var request = video.play();
        if (request && typeof request.catch === 'function') {
          request.catch(function () { /* Keep the poster if autoplay is blocked. */ });
        }
      }
    }

    clips.forEach(function (video) {
      video.defaultMuted = true;
      video.muted = true;
      video.controls = false;
      video.addEventListener('error', function () { video.classList.add('media-unavailable'); });
      var source = video.querySelector('source');
      if (source) source.addEventListener('error', function () { video.classList.add('media-unavailable'); });
    });

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.15) visible.add(entry.target);
          else visible.delete(entry.target);
          sync(entry.target);
        });
      }, { threshold: [0, 0.15, 0.4, 0.8] });
      clips.forEach(function (video) { observer.observe(video); });
    } else {
      // Graceful fallback: play when browser does not support viewport observation.
      clips.forEach(function (video) { visible.add(video); sync(video); });
    }

    document.addEventListener('visibilitychange', function () { clips.forEach(sync); });
    if (reduceMotion) {
      if (typeof reduceMotion.addEventListener === 'function') {
        reduceMotion.addEventListener('change', function () { clips.forEach(sync); });
      } else if (typeof reduceMotion.addListener === 'function') {
        reduceMotion.addListener(function () { clips.forEach(sync); });
      }
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
}());
