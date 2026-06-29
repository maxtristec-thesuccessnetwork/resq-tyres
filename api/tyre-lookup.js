/* ===========================================================
   ResQ Tyres — Vercel serverless function: /api/tyre-lookup
   -----------------------------------------------------------
   Looks up a vehicle's factory tyre size from its registration
   plate, via UK Vehicle Data (ukvehicledata.co.uk).

   The API KEY is read from an environment variable and is NEVER
   sent to the browser. Set it in Vercel:
     Project → Settings → Environment Variables
       UKVD_API_KEY   = <your key from panel.ukvehicledata.co.uk/APIKeys>
       UKVD_PACKAGE   = TyreData      (optional; default shown)

   Until a key is set, this returns sample ("mock") data so the
   whole flow can be demoed. Mock responses are clearly flagged
   with source:"mock".

   Request:  GET /api/tyre-lookup?vrm=AB12CDE
   Response: { ok, source, vrm, make, model, size:{label,width,profile,rim} }
   =========================================================== */

const UKVD_BASE = "https://uk1.ukvehicledata.co.uk/api/datapackage";

/* A few well-known fitments for the demo / fallback. Default covers
   anything not listed so the UI always has something to show. */
const MOCK = {
  _default: { make: "Vehicle", model: "Looked-up vehicle", size: "205/55R16" },
  "AB12CDE": { make: "Volkswagen", model: "Golf 1.6 TDI", size: "205/55R16" },
  "LA15XYZ": { make: "Ford", model: "Fiesta Zetec", size: "195/55R16" },
  "RA14POR": { make: "Volkswagen", model: "Sharan 2.0 TDi SEL", size: "225/50R17" },
  "BMW1A":   { make: "BMW", model: "320d M Sport", size: "225/45R18" }
};

function cleanVrm(v) {
  return String(v || "").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 8);
}

/* "225/50R17" -> {label, width, profile, rim} */
function parseSize(str) {
  const m = String(str || "").match(/(\d{3})\s*\/\s*(\d{2})\s*R?\s*(\d{2})/i);
  if (!m) return null;
  return {
    label: m[1] + "/" + m[2] + " R" + m[3],
    width: parseInt(m[1], 10),
    profile: parseInt(m[2], 10),
    rim: parseInt(m[3], 10)
  };
}

function sizeFromParts(width, profile, rim, fallback) {
  if (width && profile && rim) {
    return {
      label: width + "/" + profile + " R" + rim,
      width: parseInt(width, 10),
      profile: parseInt(profile, 10),
      rim: parseInt(rim, 10)
    };
  }
  return parseSize(fallback);
}

function sendMock(res, vrm) {
  const rec = MOCK[vrm] || MOCK._default;
  const size = parseSize(rec.size);
  return res.status(200).json({
    ok: true,
    source: "mock",
    vrm: vrm,
    make: rec.make,
    model: rec.model,
    size: size,
    note: "Sample data — set UKVD_API_KEY in Vercel for live lookups."
  });
}

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");

  const vrm = cleanVrm(req.query && req.query.vrm);
  if (!vrm || vrm.length < 2) {
    return res.status(400).json({ ok: false, error: "bad_vrm", message: "Please enter a valid registration." });
  }

  const apiKey = process.env.UKVD_API_KEY;
  const pkg = process.env.UKVD_PACKAGE || "TyreData";

  /* No key yet → demo mode */
  if (!apiKey) return sendMock(res, vrm);

  try {
    const url = UKVD_BASE + "/" + encodeURIComponent(pkg) +
      "?v=2&api_nullitems=1&auth_apikey=" + encodeURIComponent(apiKey) +
      "&user_tag=resqtyres&key_VRM=" + encodeURIComponent(vrm);

    const r = await fetch(url, { headers: { "Accept": "application/json" } });
    const data = await r.json();

    const ok = data && data.Response && data.Response.StatusCode === "Success";
    const items = ok ? data.Response.DataItems : null;
    if (!ok || !items) {
      const msg = (data && data.Response && data.Response.StatusMessage) || "No data for that registration.";
      return res.status(404).json({ ok: false, error: "not_found", message: msg, vrm: vrm });
    }

    const veh = items.VehicleDetails || {};
    const rec = items.TyreDetails && items.TyreDetails.RecordList && items.TyreDetails.RecordList[0];
    const front = rec && rec.Front && rec.Front.Tyre;

    let size = null;
    if (front) {
      size = sizeFromParts(front.SectionWidth, front.AspectRatio, front.RimDiameter, front.Size);
    }
    if (!size) {
      return res.status(404).json({ ok: false, error: "no_tyre", message: "We couldn't read a tyre size for that vehicle.", vrm: vrm });
    }

    return res.status(200).json({
      ok: true,
      source: "ukvd",
      vrm: vrm,
      make: veh.Make || "",
      model: veh.Model || (rec && rec.Vehicle && rec.Vehicle.ModelName) || "",
      size: size
    });
  } catch (e) {
    return res.status(502).json({ ok: false, error: "upstream", message: "Lookup service unavailable. Please enter your size manually." });
  }
};
