/* Google Analytics 4 - ResQ Tyres & Recovery
   Measurement ID lives here only. Loaded on every page via:
     <script async src="https://www.googletagmanager.com/gtag/js?id=G-GVBR7Z973Z"></script>
     <script src="/js/analytics.js" defer></script>
*/
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-GVBR7Z973Z');

// Google Ads website call tracking. For visitors who arrive from an ad, Google
// swaps 07438 562633 for a forwarding number. Everyone else keeps seeing, and
// dialling, the real number.
gtag('config', 'AW-18374857509');
// Google's automatic swap changes the number where it is written out, but buttons
// that just say "Call now" would keep dialling the real number. The callback
// rewrites every tel: link and every written copy of the number whenever Google
// hands over a forwarding number.
function resqUseForwardingNumber(formatted, mobile) {
  if (!formatted) return;
  var dial = String(mobile || formatted).replace(/[^\d+]/g, '');
  var links = document.querySelectorAll('a[href^="tel:"]');
  for (var i = 0; i < links.length; i++) {
    if (links[i].getAttribute('href').replace(/\D/g, '').slice(-10) === '7438562633') {
      links[i].setAttribute('href', 'tel:' + dial);
    }
  }
  var re = /07438[\s\u00a0]?562633/g, walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), n;
  while ((n = walker.nextNode())) {
    if (re.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(re, formatted);
    re.lastIndex = 0;
  }
}
gtag('config', 'AW-18374857509/mR1vCN2bqPwcEKWm6LlE', {
  'phone_conversion_number': '07438 562633',
  'phone_conversion_callback': resqUseForwardingNumber
});

// Emergency trade = phone-driven. Taps on the number and on WhatsApp are the
// only conversions that matter, so they are sent as their own events and
// marked as key events in GA4 > Admin > Events.
document.addEventListener('click', function (e) {
  var a = e.target.closest && e.target.closest('a[href^="tel:"], a[href*="wa.me"]');
  if (!a) return;
  gtag('event', a.href.indexOf('tel:') === 0 ? 'call_click' : 'whatsapp_click',
       { link_url: a.href, link_text: (a.textContent || '').trim().slice(0, 60) });
}, true);
