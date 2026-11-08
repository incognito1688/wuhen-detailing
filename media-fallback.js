/* V6.4: Keep the reserved image frame on missing-file errors. No external network API. */
(function () {
  function markMissing(img) {
    if (img instanceof HTMLImageElement && img.hasAttribute('data-media-slot')) {
      img.classList.add('media-unavailable');
    }
  }
  document.addEventListener('error', function (ev) { markMissing(ev.target); }, true);
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('img[data-media-slot]').forEach(function (img) {
      if (img.complete && img.naturalWidth === 0) markMissing(img);
    });
  });
}());
