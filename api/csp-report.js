/* ===========================================================
   ResQ Tyres — Vercel serverless function: /api/csp-report
   -----------------------------------------------------------
   Collects Content-Security-Policy violation reports, so the
   report-only policy in vercel.json can be checked against what
   real browsers load before it is ever enforced.

   Browsers send two shapes:
     report-uri  (all browsers)  application/csp-report
                 { "csp-report": { "document-uri", "blocked-uri", ... } }
     report-to   (Chromium)      application/reports+json
                 [ { "type": "csp-violation", "body": { "documentURL", "blockedURL", ... } } ]

   Each report becomes one log line in the Vercel runtime logs,
   prefixed "csp-report". Only the fields needed to fix the policy
   are kept, and query strings and fragments are cut off every URL,
   so nothing a visitor typed or was sent in a link is logged.
   Nothing is stored anywhere else.
   =========================================================== */

const MAX_BYTES = 16 * 1024;
const MAX_REPORTS = 20;

/* scheme + host + path; drops ?query and #fragment. Keywords like
   "inline", "eval" or "data" pass through unchanged. */
function trimUrl(u) {
  const s = String(u || "").slice(0, 300);
  try {
    const x = new URL(s);
    return x.origin === "null" ? x.protocol : x.origin + x.pathname;
  } catch (e) {
    return s.split(/[?#]/)[0];
  }
}

function pick(r) {
  /* report-uri uses kebab-case keys, report-to uses camelCase */
  const g = (a, b) => (r[a] !== undefined ? r[a] : r[b]);
  return {
    page: trimUrl(g("document-uri", "documentURL")),
    blocked: trimUrl(g("blocked-uri", "blockedURL")),
    directive: String(g("effective-directive", "effectiveDirective") || g("violated-directive", "violatedDirective") || "").slice(0, 60),
    disposition: String(g("disposition", "disposition") || "").slice(0, 20),
    source: trimUrl(g("source-file", "sourceFile")),
    line: Number(g("line-number", "lineNumber")) || undefined,
    sample: String(g("script-sample", "sample") || "").slice(0, 40) || undefined
  };
}

function readBody(req) {
  return new Promise((resolve) => {
    let size = 0;
    const chunks = [];
    req.on("data", (c) => {
      size += c.length;
      if (size <= MAX_BYTES) chunks.push(c);
    });
    req.on("end", () => resolve(size > MAX_BYTES ? null : Buffer.concat(chunks).toString("utf8")));
    req.on("error", () => resolve(null));
  });
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    res.statusCode = 405;
    return res.end();
  }
  const raw = await readBody(req);
  let data = null;
  try { data = raw ? JSON.parse(raw) : null; } catch (e) { data = null; }

  let reports = [];
  if (data && data["csp-report"]) reports = [data["csp-report"]];
  else if (Array.isArray(data)) reports = data.filter((x) => x && x.type === "csp-violation" && x.body).map((x) => x.body);

  for (const r of reports.slice(0, MAX_REPORTS)) {
    console.log("csp-report " + JSON.stringify(pick(r)));
  }
  res.statusCode = 204;
  res.end();
};
