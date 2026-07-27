/* Google Analytics 4 - ResQ Tyres & Recovery
   Property: ResQ Tyres & Recovery, under the Helium Studio Analytics account.
   Measurement ID lives here only. Loaded on every page via:
     <script async src="https://www.googletagmanager.com/gtag/js?id=G-GVBR7Z973Z"></script>
     <script src="/js/analytics.js" defer></script>
*/
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-GVBR7Z973Z');

// Emergency trade = phone-driven. Taps on the number and on WhatsApp are the
// only conversions that matter, so they are sent as their own events and
// marked as key events in GA4 > Admin > Events.
document.addEventListener('click', function (e) {
  var a = e.target.closest && e.target.closest('a[href^="tel:"], a[href*="wa.me"]');
  if (!a) return;
  gtag('event', a.href.indexOf('tel:') === 0 ? 'call_click' : 'whatsapp_click',
       { link_url: a.href, link_text: (a.textContent || '').trim().slice(0, 60) });
}, true);
