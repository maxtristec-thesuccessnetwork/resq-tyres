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
// Google fetches the forwarding number only after both tags have loaded, so on a
// phone the swap lands a few seconds after the call button can be tapped, and a
// tap before it dials the real number uncounted. Opening the connections and
// fetching Google's call-tracking loader now brings the swap forward (about
// 5.2s to 4.5s on slow 4G, 2.6s to 2.1s on typical 4G). Every visitor loads
// these anyway, so nothing extra is downloaded.
[['preconnect', 'https://www.googleadservices.com'], ['preconnect', 'https://www.google.co.uk'],
 ['preload', 'https://www.gstatic.com/wcm/loader.js']].forEach(function (h) {
  var l = document.createElement('link');
  l.rel = h[0];
  l.href = h[1];
  if (h[0] === 'preload') l.as = 'script';
  document.head.appendChild(l);
});
// Google's automatic swap changes the number where it is written out, but buttons
// that just say "Call now" would keep dialling the real number. The callback
// rewrites every tel: link and every written copy of the number whenever Google
// hands over a forwarding number, and again for any added later (the postcode
// checker and the failed-send message write theirs after the page has loaded).
var resqForwarding = null;
function resqSwapNumbers(root) {
  if (!resqForwarding || !root.querySelectorAll) return;
  var links = root.querySelectorAll('a[href^="tel:"]');
  for (var i = 0; i < links.length; i++) {
    if (links[i].getAttribute('href').replace(/\D/g, '').slice(-10) === '7438562633') {
      links[i].setAttribute('href', 'tel:' + resqForwarding.dial);
    }
  }
  var re = /07438[\s\u00a0]?562633/g, walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), n;
  while ((n = walker.nextNode())) {
    if (re.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(re, resqForwarding.formatted);
    re.lastIndex = 0;
  }
}
function resqUseForwardingNumber(formatted, mobile) {
  if (!formatted) return;
  var watching = !!resqForwarding;
  resqForwarding = { formatted: formatted, dial: String(mobile || formatted).replace(/[^\d+]/g, '') };
  resqSwapNumbers(document.body);
  if (!watching && window.MutationObserver) {
    new MutationObserver(function (changes) {
      for (var i = 0; i < changes.length; i++) resqSwapNumbers(changes[i].target);
    }).observe(document.body, { childList: true, subtree: true });
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
