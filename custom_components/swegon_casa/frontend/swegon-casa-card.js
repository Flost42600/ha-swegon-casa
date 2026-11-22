/*!
 * Swegon CASA card: animated Lovelace card for Swegon CASA air handling units.
 * Shipped with the swegon_casa integration (loaded automatically), version below.
 *
 *   type: custom:swegon-casa-card        (or custom:swegon-casa-mini-card)
 *   title: Ventilation                   optional, defaults to the device name
 *   device_id: <id>                      optional, when several units are configured
 *   exchanger: plate | rotor             optional, detected from the entities
 *   show_header / show_controls / show_stats: true
 *   entities:                            optional overrides, e.g. for a YAML modbus setup
 *     fresh: sensor.casa_air_neuf
 *
 * Entities are found by themselves (platform swegon_casa + translation key).
 */

const DOMAIN = "swegon_casa";
const CARD_VERSION = "0.2.1";

/* ------------------------------------------------------------------------------------------ */
/*  Entities: card key -> [domain, translation keys by preference]                            */
/* ------------------------------------------------------------------------------------------ */
const DISCOVERY = {
  fan: ["fan", null],
  mode: ["select", ["operating_mode"]],
  ventilation: ["sensor", ["ventilation_state"]],
  unit_state: ["sensor", ["unit_state"]],
  fresh: ["sensor", ["fresh_air_temperature"]],
  supply: ["sensor", ["supply_air_temperature"]],
  supply_pre: ["sensor", ["supply_before_heater_temperature"]],
  extract: ["sensor", ["extract_air_temperature"]],
  exhaust: ["sensor", ["exhaust_air_temperature"]],
  room: ["sensor", ["room_temperature"]],
  preheater_temp: ["sensor", ["preheater_temperature"]],
  efficiency: ["sensor", ["heat_recovery_efficiency"]],
  supply_fan: ["sensor", ["supply_fan_control"]],
  exhaust_fan: ["sensor", ["exhaust_fan_control"]],
  supply_rpm: ["sensor", ["supply_fan_rpm"]],
  exhaust_rpm: ["sensor", ["exhaust_fan_rpm"]],
  supply_flow: ["sensor", ["supply_airflow"]],
  exhaust_flow: ["sensor", ["exhaust_airflow"]],
  bypass: ["sensor", ["bypass_position"]],
  bypass_manual: ["sensor", ["manual_bypass"]],
  preheater_power: ["sensor", ["preheater_power", "nordic_preheater_power"]],
  preheater_active: ["binary_sensor", ["preheater_active"]],
  heater_power: ["sensor", ["supply_control_power"]],
  heater_setpoint: ["sensor", ["temperature_setpoint_active"]],
  cooling: ["binary_sensor", ["cooling_active"]],
  defrost: ["binary_sensor", ["defrost"]],
  night_cooling: ["binary_sensor", ["summer_cooling_active"]],
  rotor: ["binary_sensor", ["rotor_active"]],
  rotor_rpm: ["sensor", ["rotor_rpm"]],
  co2: ["sensor", ["co2"]],
  humidity: ["sensor", ["humidity"]],
  abs_humidity: ["sensor", ["absolute_humidity"]],
  voc: ["sensor", ["voc"]],
  boost_left: ["sensor", ["boost_time_left"]],
  week_timer: ["binary_sensor", ["week_timer_active"]],
  alarm: ["binary_sensor", ["alarm"]],
  filter: ["binary_sensor", ["filter_info"]],
  service: ["binary_sensor", ["service_info"]],
  hours_service: ["sensor", ["hours_to_service"]],
  fireplace: ["switch", ["fireplace"]],
  confirm_filter: ["button", ["confirm_filter"]],
  confirm_service: ["button", ["confirm_service"]],
};

const MODE_KEYS = ["stopped", "away", "home", "boost", "travelling"];
const MODES = {
  stopped: { color: "#7d8794", icon: "mdi:power" },
  away: { color: "#8ea4bd", icon: "mdi:home-export-outline" },
  home: { color: "#6fdc8c", icon: "mdi:home" },
  boost: { color: "#ff8a3d", icon: "mdi:fan-plus" },
  travelling: { color: "#b39ddb", icon: "mdi:airplane" },
};

const T = {
  fr: {
    outside: "Extérieur", house: "Maison",
    fresh: "Air neuf", supply: "Soufflé", extract: "Extrait", exhaust: "Rejeté",
    modes: { stopped: "Arrêt", away: "Absent", home: "Maison", boost: "Boost", travelling: "Voyage" },
    states: { external_stop: "Arrêt externe", user_stopped: "Arrêtée", starting: "Démarrage", normal: "En marche", commissioning: "Mise en service" },
    unreachable: "Injoignable", filter: "Filtre", filterDue: "Filtre à remplacer", serviceDue: "Entretien à prévoir", confirm: "Acquitter",
    preheater: "Préchauffe", postheater: "Post-chauffe", cooling: "Froid", bypass: "By-pass", closed: "fermé",
    efficiency: "Rendement", recovery: "récupération", airflow: "Débit", fans: "Ventilateurs", supplyShort: "Soufflage", extractShort: "Extr.",
    co2: "CO₂", humidity: "Humidité", voc: "COV", service: "Entretien", inDays: (d) => `dans ${d} j`,
    fireplace: "Cheminée", nightCooling: "Rafraîchissement nocturne", defrost: "Dégivrage", alarm: "Alarme", weekTimer: "Programme horaire",
    rpm: "tr/min", rotor: "Roue", plates: "Échangeur à plaques", left: (m) => `encore ${m} min`, room: "Ambiance", setpoint: "consigne",
    short: { out: "Ext.", supply: "Soufflé", eff: "Rend." },
    notFound: "Aucune centrale Swegon CASA trouvée. Indiquez les entités avec la clé entities:.",
    alarms: {
      reheater_failure: "Défaut post-chauffage", preheater_failure: "Défaut préchauffage", external_preheater_failure: "Défaut préchauffage externe",
      freezing_danger: "Risque de gel", supply_fan_failure: "Défaut ventilateur soufflage", exhaust_fan_failure: "Défaut ventilateur extraction",
      temperature_sensor_failure: "Défaut sonde", emergency_stop: "Arrêt d'urgence", filter_guard: "Filtre", service: "Entretien",
      internal_temperature: "Température interne", supply_temperature_low: "Soufflage trop froid", supply_temperature_high: "Soufflage trop chaud",
      preheater_temperature_high: "Préchauffage trop chaud", rotor: "Défaut roue", fan_control: "Régulation ventilateurs",
    },
  },
  en: {
    outside: "Outside", house: "House",
    fresh: "Fresh air", supply: "Supply", extract: "Extract", exhaust: "Exhaust",
    modes: { stopped: "Stop", away: "Away", home: "Home", boost: "Boost", travelling: "Travel" },
    states: { external_stop: "External stop", user_stopped: "Stopped", starting: "Starting", normal: "Running", commissioning: "Commissioning" },
    unreachable: "Unreachable", filter: "Filter", filterDue: "Replace the filter", serviceDue: "Service due", confirm: "Confirm",
    preheater: "Preheater", postheater: "Re-heater", cooling: "Cooling", bypass: "Bypass", closed: "closed",
    efficiency: "Efficiency", recovery: "heat recovery", airflow: "Airflow", fans: "Fans", supplyShort: "Supply", extractShort: "Extr.",
    co2: "CO₂", humidity: "Humidity", voc: "VOC", service: "Service", inDays: (d) => `in ${d} d`,
    fireplace: "Fireplace", nightCooling: "Night cooling", defrost: "Defrost", alarm: "Alarm", weekTimer: "Week timer",
    rpm: "rpm", rotor: "Rotor", plates: "Plate exchanger", left: (m) => `${m} min left`, room: "Room", setpoint: "setpoint",
    short: { out: "Out", supply: "Supply", eff: "Eff." },
    notFound: "No Swegon CASA unit found. Set the entities with the entities: key.",
    alarms: {
      reheater_failure: "Re-heater failure", preheater_failure: "Preheater failure", external_preheater_failure: "External preheater failure",
      freezing_danger: "Freezing danger", supply_fan_failure: "Supply fan failure", exhaust_fan_failure: "Exhaust fan failure",
      temperature_sensor_failure: "Sensor failure", emergency_stop: "Emergency stop", filter_guard: "Filter", service: "Service",
      internal_temperature: "Internal temperature", supply_temperature_low: "Supply air too cold", supply_temperature_high: "Supply air too warm",
      preheater_temperature_high: "Preheater too hot", rotor: "Rotor failure", fan_control: "Fan control",
    },
  },
};

/* ------------------------------------------------------------------------------------------ */
/*  Helpers                                                                                    */
/* ------------------------------------------------------------------------------------------ */
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

const pipe = (id, d, cls = "") =>
  `<g class="pipe ${cls}" id="${id}"><path class="pb" d="${d}"/><path class="pg" d="${d}"/><path class="pc" d="${d}"/><path class="pf" d="${d}"/></g>`;

function lerpColor(a, b, t) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const ch = (s) => Math.round(((pa >> s) & 255) + (((pb >> s) & 255) - ((pa >> s) & 255)) * t);
  return "#" + ((1 << 24) | (ch(16) << 16) | (ch(8) << 8) | ch(0)).toString(16).slice(1);
}

// Air temperature -> colour: deep blue when freezing, mint around 15 °C, orange when warm.
const AIR_STOPS = [[-15, "#3d6bff"], [-3, "#4f8dff"], [5, "#64b5f6"], [11, "#6fd3e8"], [15, "#9be3c0"], [18, "#ffd27a"], [22, "#ffa36b"], [27, "#ff7a45"], [35, "#ff4b2b"]];
function airColor(t) {
  if (t == null || isNaN(t)) return "#8a96a3";
  if (t <= AIR_STOPS[0][0]) return AIR_STOPS[0][1];
  for (let i = 1; i < AIR_STOPS.length; i++) {
    if (t <= AIR_STOPS[i][0]) {
      const [t0, c0] = AIR_STOPS[i - 1], [t1, c1] = AIR_STOPS[i];
      return lerpColor(c0, c1, (t - t0) / (t1 - t0));
    }
  }
  return AIR_STOPS[AIR_STOPS.length - 1][1];
}

function flake(x, y, s = 1) {
  const l = 7 * s;
  let p = "";
  for (let a = 0; a < 180; a += 60) {
    const r = (a * Math.PI) / 180, dx = Math.cos(r) * l, dy = Math.sin(r) * l;
    p += `M${(x - dx).toFixed(1)} ${(y - dy).toFixed(1)}L${(x + dx).toFixed(1)} ${(y + dy).toFixed(1)}`;
  }
  return p;
}

const fanBlades = (scale = 1) => {
  let b = "";
  for (let i = 0; i < 5; i++) {
    b += `<path transform="rotate(${i * 72}) scale(${scale})" d="M0 -6 C10 -14 22 -40 8 -52 C-6 -58 -14 -34 -6 -10 Z"/>`;
  }
  return b;
};

function esc(v) {
  return String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

/* ------------------------------------------------------------------------------------------ */
/*  Static SVG                                                                                 */
/*  Fresh air enters top left and leaves as supply air bottom right; extract air enters top   */
/*  right and leaves as exhaust bottom left. Both streams cross in the plate exchanger.       */
/* ------------------------------------------------------------------------------------------ */
const CX = 620, CY = 330, HS = 92; // exchanger centre, half side of the plate stack (local frame)

/*
 * Cross-flow plate exchanger, drawn in a frame rotated by 45 degrees: local +x runs from the
 * top-left face to the bottom-right face (fresh -> supply), local +y from the top-right face to
 * the bottom-left face (extract -> exhaust). A brushed-metal plate stack carries two soft
 * light ribbons, one per air stream, coloured from inlet to outlet temperature; they cross in
 * the middle, where a glow breathes while heat is exchanged. Flared collars join the ducts.
 */
function exchanger(o) {
  const { hs, band, lanes, flare, hc, hb, frost = "", bolts = true } = o;
  const b = band / 2, f = flare;
  let plates = "";
  for (let c = -2 * hs + 12, i = 0; c < 2 * hs; c += 12, i++) {
    plates += `<path class="${i % 2 ? "pl2" : "pl1"}" d="M${c + hs} ${-hs} L${c - hs} ${hs}"/>`;
  }
  // Light streaks sliding along each ribbon (CSS translate runs in the rotated frame, i.e. along the diagonal).
  const sl = Math.max(8, band * 0.3), lanesY = lanes.length > 1 ? lanes : [0];
  const streaks = lanesY.flatMap((y, li) => [0, 1].map((k) =>
    `<path d="M${-sl} ${y} H0" style="--i:${(li * 0.37 + k * 0.5) % 1}"/>`)).join("");
  const dotsF = streaks;
  const dotsE = `<g transform="rotate(90)">${streaks}</g>`;
  const lip = (w) => `M${-hs - f} ${-w} C${-hs - f * 0.45} ${-w} ${-hs - f * 0.35} ${-b - (w - hc)} ${-hs} ${-b - (w - hc)} V${b + (w - hc)} C${-hs - f * 0.35} ${b + (w - hc)} ${-hs - f * 0.45} ${w} ${-hs - f} ${w} Z`;
  const collar = (id, rot, n) => `<g transform="rotate(${rot})"><path class="clb" d="${lip(hb)}"/><path id="${id}" class="cl" d="${lip(hc)}" fill="url(#gCl${n})"/></g>`;
  const boltXY = hs - 9;
  return {
    defs: `
    <linearGradient id="gFresh" gradientUnits="userSpaceOnUse" x1="${-hs}" y1="0" x2="${hs}" y2="0"><stop id="gf0" offset="0" stop-color="#64b5f6"/><stop id="gf1" offset="1" stop-color="#ffa36b"/></linearGradient>
    <linearGradient id="gExt" gradientUnits="userSpaceOnUse" x1="0" y1="${-hs}" x2="0" y2="${hs}"><stop id="ge0" offset="0" stop-color="#ffa36b"/><stop id="ge1" offset="1" stop-color="#64b5f6"/></linearGradient>
    <linearGradient id="gFthY" gradientUnits="userSpaceOnUse" x1="0" y1="${-b}" x2="0" y2="${b}"><stop offset="0" stop-color="#000"/><stop offset=".16" stop-color="#fff"/><stop offset=".84" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
    <linearGradient id="gFthX" gradientUnits="userSpaceOnUse" x1="${-b}" y1="0" x2="${b}" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".16" stop-color="#fff"/><stop offset=".84" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
    <mask id="mRibF" maskUnits="userSpaceOnUse" x="${-hs}" y="${-hs}" width="${hs * 2}" height="${hs * 2}"><rect x="${-hs}" y="${-b}" width="${hs * 2}" height="${band}" fill="url(#gFthY)"/></mask>
    <mask id="mRibE" maskUnits="userSpaceOnUse" x="${-hs}" y="${-hs}" width="${hs * 2}" height="${hs * 2}"><rect x="${-b}" y="${-hs}" width="${band}" height="${hs * 2}" fill="url(#gFthX)"/></mask>
    <linearGradient id="gBevel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e3e8ee"/><stop offset=".5" stop-color="#8a96a3"/><stop offset="1" stop-color="#4b5462"/></linearGradient>
    <linearGradient id="gMetal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a424d"/><stop offset=".5" stop-color="#252b33"/><stop offset="1" stop-color="#1b2027"/></linearGradient>
    <radialGradient id="gGlow"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".45" style="stop-color:var(--glow,#fff)" stop-opacity=".45"/><stop offset="1" style="stop-color:var(--glow,#fff)" stop-opacity="0"/></radialGradient>
    <linearGradient id="gStreak" gradientUnits="userSpaceOnUse" x1="${-sl}" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".95"/></linearGradient>
    <clipPath id="cHx"><rect x="${-hs}" y="${-hs}" width="${hs * 2}" height="${hs * 2}" rx="${hs * 0.08}"/></clipPath>
    <linearGradient id="gCl0" gradientUnits="userSpaceOnUse" x1="${-hs - f}" y1="0" x2="${-hs}" y2="0"><stop offset="0" stop-opacity="1"/><stop offset=".55" stop-opacity=".95"/><stop offset="1" stop-opacity=".6"/></linearGradient>
    <linearGradient id="gCl1" gradientUnits="userSpaceOnUse" x1="${-hs - f}" y1="0" x2="${-hs}" y2="0"><stop offset="0" stop-opacity="1"/><stop offset=".55" stop-opacity=".95"/><stop offset="1" stop-opacity=".6"/></linearGradient>
    <linearGradient id="gCl2" gradientUnits="userSpaceOnUse" x1="${-hs - f}" y1="0" x2="${-hs}" y2="0"><stop offset="0" stop-opacity="1"/><stop offset=".55" stop-opacity=".95"/><stop offset="1" stop-opacity=".6"/></linearGradient>
    <linearGradient id="gCl3" gradientUnits="userSpaceOnUse" x1="${-hs - f}" y1="0" x2="${-hs}" y2="0"><stop offset="0" stop-opacity="1"/><stop offset=".55" stop-opacity=".95"/><stop offset="1" stop-opacity=".6"/></linearGradient>`,
    body: `
      ${collar("cl_f", 0, 0)}${collar("cl_s", 180, 1)}${collar("cl_e", 90, 2)}${collar("cl_x", 270, 3)}
      <g id="plates">
        <rect class="hxbody" x="${-hs}" y="${-hs}" width="${hs * 2}" height="${hs * 2}" rx="${hs * 0.08}"/>
        <g clip-path="url(#cHx)">
          <g class="rib" id="rib_e"><rect mask="url(#mRibE)" x="${-b}" y="${-hs}" width="${band}" height="${hs * 2}" fill="url(#gExt)"/></g>
          <g class="rib" id="rib_f"><rect mask="url(#mRibF)" x="${-hs}" y="${-b}" width="${hs * 2}" height="${band}" fill="url(#gFresh)"/></g>
          <circle class="hglow" r="${b * 0.8}" fill="url(#gGlow)"/>
          <g class="stack">${plates}</g>
          <g class="dots" id="dots_e" style="--d:calc(var(--spde,1.3s) * 3.2);--L:${hs}px">${dotsE}</g>
          <g class="dots" id="dots_f" style="--d:calc(var(--spd,1.3s) * 3.2);--L:${hs}px">${dotsF}</g>
          <rect id="hxfrost" x="${-hs}" y="${-hs}" width="${hs * 2}" height="${hs * 2}" fill="#dff1ff"/>
          <g id="hxice">${frost}</g>
        </g>
        <rect class="hxframe" x="${-hs}" y="${-hs}" width="${hs * 2}" height="${hs * 2}" rx="${hs * 0.08}" stroke="url(#gBevel)"/>
        <rect class="hxinner" x="${-hs + 5}" y="${-hs + 5}" width="${hs * 2 - 10}" height="${hs * 2 - 10}" rx="${hs * 0.05}"/>
        ${bolts ? [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([x, y]) => `<circle class="bolt" cx="${x * boltXY}" cy="${y * boltXY}" r="3"/>`).join("") : ""}
      </g>`,
  };
}

function buildSVG() {
  const frost = [[-60, -55, 1], [40, -66, 0.8], [-20, 10, 0.9], [62, 30, 1.1], [-66, 52, 0.7], [18, 64, 0.8]]
    .map(([x, y, s], i) => `<path class="ice" style="animation-delay:${i * 0.35}s" d="${flake(x, y, s)}"/>`).join("");
  let spokes = "";
  for (let i = 0; i < 24; i++) spokes += `<path transform="rotate(${i * 15})" d="M0 -28 V-118"/>`;
  const hxp = exchanger({ hs: HS, band: 84, lanes: [-22, 0, 22], flare: 54, hc: 10, hb: 15, frost });
  let pleats = "";
  for (let y = 166; y <= 214; y += 6) pleats += `M-11 ${y - 190} L11 ${y - 187}`;

  return `
<svg viewBox="0 52 1240 522" xmlns="http://www.w3.org/2000/svg" id="svg" role="img" aria-label="Swegon CASA">
  <defs>
    <linearGradient id="gCase" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3039"/><stop offset="1" stop-color="#1c2027"/></linearGradient>
    <linearGradient id="gHx" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1d2228"/><stop offset="1" stop-color="#262c34"/></linearGradient>
    <radialGradient id="gFan" cx="0.5" cy="0.5" r="0.5"><stop offset="0.55" stop-color="#14171c"/><stop offset="1" stop-color="#232830"/></radialGradient>
    ${hxp.defs}
  </defs>

  <!-- ===== Outside / house ===== -->
  <g id="outside" class="clickable" data-e="fresh">
    <circle cx="96" cy="300" r="15" class="sun"/>
    <path class="cloud" d="M76 344 h66 a17 17 0 0 0 -4 -33 a24 24 0 0 0 -45 6 a14 14 0 0 0 -17 27z"/>
    <text id="l_out" class="sub" x="110" y="378" text-anchor="middle"></text>
  </g>
  <g id="house" class="clickable" data-e="room">
    <path class="housep" d="M1074 330 L1125 288 L1176 330 M1084 322 V378 H1166 V322"/>
    <text id="t_room" class="lbl" x="1125" y="352" text-anchor="middle"></text>
    <text id="l_house" class="sub" x="1125" y="404" text-anchor="middle"></text>
  </g>

  <!-- ===== Casing ===== -->
  <rect x="230" y="70" width="780" height="490" rx="26" fill="url(#gCase)" stroke="#4b5462" stroke-width="2.5"/>
  <rect x="244" y="76" width="752" height="6" rx="3" fill="#fff" opacity=".05"/>

  <!-- ===== Air ducts (bypass first: the extract duct passes over it) ===== -->
  ${pipe("a_byp", "M440 190 V112 H790 V470", "duct byp")}
  ${pipe("a_fresh", "M30 190 H375", "duct")}
  ${pipe("a_pre", "M375 190 H480 L555 265", "duct")}
  ${pipe("a_ext", "M1210 190 H760 L685 265", "duct")}
  ${pipe("a_exh", "M555 395 L480 470 H30", "duct")}
  ${pipe("a_sup1", "M685 395 L760 470 H830", "duct")}
  ${pipe("a_sup2", "M830 470 H1210", "duct")}

  <!-- ===== By-pass damper ===== -->
  <g id="byp" class="clickable" data-e="bypass">
    <circle cx="615" cy="112" r="22" class="dhouse"/>
    <g transform="translate(615 112)"><g id="damper"><circle r="20" fill="transparent"/><path d="M-17 0 H17"/><circle r="3.5"/></g></g>
    <text id="t_byp" class="sub" x="615" y="160" text-anchor="middle"></text>
  </g>

  <!-- ===== Filters ===== -->
  <g id="flt_f" class="filter clickable" data-e="filter"><g transform="translate(290 190)">
    <rect x="-13" y="-30" width="26" height="60" rx="4"/><path class="pleat" d="${pleats}"/></g>
    <text class="sub" x="290" y="146" text-anchor="middle" id="l_flt_f"></text>
  </g>
  <g id="flt_e" class="filter clickable" data-e="filter"><g transform="translate(905 190)">
    <rect x="-13" y="-30" width="26" height="60" rx="4"/><path class="pleat" d="${pleats}"/></g>
    <text class="sub" x="905" y="146" text-anchor="middle" id="l_flt_e"></text>
  </g>

  <!-- ===== Heating coils ===== -->
  <g id="pre" class="coilbox clickable" data-e="preheater_power">
    <rect x="355" y="160" width="40" height="60" rx="7"/>
    <path class="zz" d="M375 164 l9 6 l-18 7 l18 7 l-18 7 l18 7 l-18 7 l18 7 l-9 4"/>
    <text id="t_pre" class="sub" x="375" y="244" text-anchor="middle"></text>
  </g>
  <g id="post" class="coilbox clickable" data-e="heater_power">
    <rect x="810" y="440" width="40" height="60" rx="7"/>
    <path class="zz" d="M830 444 l9 6 l-18 7 l18 7 l-18 7 l18 7 l-18 7 l18 7 l-9 4"/>
    <text id="t_post" class="sub" x="830" y="524" text-anchor="middle"></text>
  </g>

  <!-- ===== Fans ===== -->
  <g id="fan_e" class="fanbox clickable" data-e="exhaust_fan">
    <circle cx="360" cy="470" r="38" fill="url(#gFan)" stroke="#5d6775" stroke-width="2"/>
    <circle class="ring" cx="360" cy="470" r="38" fill="none" stroke-width="3"/>
    <g transform="translate(360 470)"><g class="fan" id="fe"><circle r="34" fill="transparent"/>${fanBlades(0.62)}<circle r="7" class="hub"/></g></g>
    <text id="t_fe" class="lbl" x="360" y="534" text-anchor="middle"></text><text id="r_fe" class="sub" x="360" y="554" text-anchor="middle"></text>
  </g>
  <g id="fan_s" class="fanbox clickable" data-e="supply_fan">
    <circle cx="935" cy="470" r="38" fill="url(#gFan)" stroke="#5d6775" stroke-width="2"/>
    <circle class="ring" cx="935" cy="470" r="38" fill="none" stroke-width="3"/>
    <g transform="translate(935 470)"><g class="fan" id="fs"><circle r="34" fill="transparent"/>${fanBlades(0.62)}<circle r="7" class="hub"/></g></g>
    <text id="t_fs" class="lbl" x="935" y="534" text-anchor="middle"></text><text id="r_fs" class="sub" x="935" y="554" text-anchor="middle"></text>
  </g>

  <!-- ===== Cross-flow plate exchanger ===== -->
  <g id="hx" class="clickable" data-e="efficiency">
    <g transform="translate(${CX} ${CY}) rotate(45)">
      ${hxp.body}
    </g>
    <g id="rotorg">
      <circle cx="${CX}" cy="${CY}" r="124" class="rotorbg"/>
      ${pipe("x_f", "M555 265 L685 395", "duct inner")}
      ${pipe("x_e", "M685 265 L555 395", "duct inner")}
      <g transform="translate(${CX} ${CY})"><g id="wheel" class="fan"><circle r="122" fill="transparent"/>
        <circle r="120" class="rim"/><circle r="90" class="rim thin"/><circle r="58" class="rim thin"/><g class="spokes">${spokes}</g><circle r="26" class="hubr"/></g></g>
    </g>
  </g>
  <text id="t_eff" class="big clickable" data-e="efficiency" x="${CX}" y="506" text-anchor="middle"></text>
  <text id="l_eff" class="sub" x="${CX}" y="530" text-anchor="middle"></text>

  <!-- ===== Temperatures ===== -->
  <g class="clickable" data-e="fresh"><text id="l_fresh" class="sub" x="34" y="132"></text><text id="t_fresh" class="big" x="34" y="162"></text></g>
  <g class="clickable" data-e="exhaust"><text id="t_exh" class="big" x="34" y="524"></text><text id="l_exh" class="sub" x="34" y="548"></text></g>
  <g class="clickable" data-e="extract"><text id="l_ext" class="sub" x="1206" y="132" text-anchor="end"></text><text id="t_ext" class="big" x="1206" y="162" text-anchor="end"></text></g>
  <g class="clickable" data-e="supply"><text id="t_sup" class="big" x="1206" y="524" text-anchor="end"></text><text id="l_sup" class="sub" x="1206" y="548" text-anchor="end"></text></g>
</svg>`;
}

/* ------------------------------------------------------------------------------------------ */
/*  Styles                                                                                     */
/* ------------------------------------------------------------------------------------------ */
const CSS = `
:host{display:block}
ha-card{display:block;overflow:hidden;background:var(--sw-bg,radial-gradient(120% 90% at 30% 0%,#1f232a 0%,#15181c 60%,#121417 100%));
  color:#e6e9ee;border-radius:var(--ha-card-border-radius,16px);border:1px solid rgba(255,255,255,.06);
  font-family:var(--ha-font-family-body,var(--paper-font-body1_-_font-family,Roboto,system-ui,sans-serif))}
.hdr{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 18px 4px;flex-wrap:wrap}
.name{font-size:17px;font-weight:600;letter-spacing:.2px}
.subt{font-size:12.5px;color:#9aa3ad;margin-top:2px}
.chips{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:8px;padding:6px 12px 6px 10px;border-radius:999px;font-size:13px;font-weight:600;
  background:color-mix(in srgb,var(--mc,#7d8794) 16%,transparent);color:var(--mc,#7d8794);border:1px solid color-mix(in srgb,var(--mc,#7d8794) 35%,transparent);transition:all .5s}
.pill .dot{width:8px;height:8px;border-radius:50%;background:var(--mc,#7d8794)}
.pill.live .dot{animation:ping 1.8s ease-out infinite}
@keyframes ping{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--mc) 70%,transparent)}100%{box-shadow:0 0 0 9px transparent}}
.badge{font-size:11.5px;font-weight:600;padding:4px 9px;border-radius:999px;background:rgba(255,255,255,.06);color:#c9d1da;border:1px solid rgba(255,255,255,.08);display:none;cursor:pointer}
.badge.show{display:inline-block}
.badge.warn{color:#ffcf70;border-color:rgba(255,207,112,.3);background:rgba(255,207,112,.08)}
.badge.err{color:#ff8a80;border-color:rgba(255,110,100,.35);background:rgba(255,110,100,.1)}
.badge.ice{color:#bfe3ff;border-color:rgba(191,227,255,.3);background:rgba(191,227,255,.08)}
.badge.hot{color:#ff9f80;border-color:rgba(255,120,90,.3);background:rgba(255,120,90,.08)}
.wrap{padding:0 6px}
svg{width:100%;height:auto;display:block}
.lbl{fill:#e6e9ee;font-size:19px;font-weight:500}
.big{fill:#fff;font-size:26px;font-weight:600}
.sub{fill:#9aa3ad;font-size:14.5px}
text{paint-order:stroke;stroke:#16191d;stroke-width:4px;stroke-linejoin:round;font-variant-numeric:tabular-nums}
.clickable{cursor:pointer}
.clickable:hover{filter:brightness(1.18)}
.hide{display:none}

/* narrow layout: same drawing, larger text, secondary labels hidden */
.narrow .lbl{font-size:calc(10.5px * var(--k,2))}.narrow .big{font-size:calc(12px * var(--k,2))}.narrow .sub{font-size:calc(9.5px * var(--k,2))}
.narrow text{stroke-width:calc(1.6px * var(--k,2))}
.narrow #l_flt_f,.narrow #l_flt_e,.narrow #t_pre,.narrow #t_post,.narrow #l_eff,.narrow #t_fe,.narrow #t_fs,.narrow #l_out,.narrow #l_house,
.narrow #outside,.narrow #r_fe,.narrow #r_fs,.narrow #house .housep,.narrow #l_fresh,.narrow #l_exh,.narrow #l_ext,.narrow #l_sup{visibility:hidden}
.narrow #t_fresh{transform:translateY(-14px)}.narrow #t_ext{transform:translateY(-14px)}
.narrow #t_exh{transform:translateY(30px)}.narrow #t_sup{transform:translateY(30px)}
.narrow #t_eff{transform:translateY(14px)}.narrow #t_byp{transform:translateY(8px)}
.narrow #t_room{transform:translate(-4px,-6px)}

/* ducts (same layered pipes as the Vitocal card, air sized) */
.pipe path{fill:none;stroke-linecap:round;stroke-linejoin:round}
.pipe .pb{stroke:#0f1215;stroke-width:13}
.pipe .pg{stroke:var(--c,transparent);stroke-width:15;opacity:0;transition:opacity .6s,stroke .6s}
.pipe .pc{stroke:#4a525d;stroke-width:7;transition:stroke .6s}
.pipe .pf{stroke:rgba(255,255,255,.9);stroke-width:3;stroke-dasharray:2 18;opacity:0}
.pipe.on .pc{stroke:var(--c)}
.pipe.on .pg{opacity:.22}
.pipe.on .pf{opacity:1;animation:flow var(--spd,1.3s) linear infinite}
.duct .pb{stroke-width:30;stroke-linecap:butt}.duct .pg{stroke-width:36;stroke-linecap:butt}.duct .pc{stroke-width:20;stroke-linecap:butt}
.duct .pf{stroke-width:4;stroke-dasharray:3 21}
.duct.on .pf{animation-name:flowd}
.duct.byp{opacity:var(--bo,1);transition:opacity .8s}
.duct.byp .pb{stroke-width:22}.duct.byp .pg{stroke-width:26}.duct.byp .pc{stroke-width:13}.duct.byp .pf{stroke-width:3}
.duct.inner .pb{stroke-width:18}.duct.inner .pc{stroke-width:11}.duct.inner .pg{stroke-width:22}
@keyframes flow{to{stroke-dashoffset:-20}}
@keyframes flowd{to{stroke-dashoffset:-24}}
@keyframes flowc{to{stroke-dashoffset:-16}}


/* outside / house */
.sun{fill:#ffd27a;opacity:.85}
.cloud{fill:#3a414b;stroke:#68727f;stroke-width:1.6}
.housep{fill:none;stroke:#9aa3ad;stroke-width:2.4;stroke-linejoin:round;stroke-linecap:round}

/* by-pass damper */
.dhouse{fill:#1d2228;stroke:#68727f;stroke-width:2.2;transition:stroke .6s}
#damper{transform-box:fill-box;transform-origin:center;transition:transform .9s cubic-bezier(.4,1.4,.6,1)}
#damper path{stroke:#c9d1da;stroke-width:4.5;stroke-linecap:round}
#damper circle:last-child{fill:#c9d1da}
#byp.open .dhouse{stroke:var(--c,#9be3c0)}
#byp.open #damper path{stroke:var(--c,#9be3c0)}

/* filters */
.filter rect{fill:#2b313a;stroke:#7d8794;stroke-width:1.8;transition:stroke .6s,filter .6s}
.filter .pleat{fill:none;stroke:#7d8794;stroke-width:1.3}
.filter.due rect{stroke:#ffcf70;filter:drop-shadow(0 0 6px rgba(255,207,112,.6))}
.filter.due .pleat{stroke:#ffcf70}
.filter.due .sub{fill:#ffcf70}

/* heating coils */
.coilbox rect{fill:#1d2228;stroke:#68727f;stroke-width:2;transition:stroke .6s,filter .6s}
.coilbox .zz{fill:none;stroke:#68727f;stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round;transition:stroke .6s}
.coilbox.on rect{stroke:var(--hc);filter:drop-shadow(0 0 calc(4px + var(--hp,0) * 10px) var(--hc))}
.coilbox.on .zz{stroke:var(--hc);animation:glow 1.6s ease-in-out infinite}
@keyframes glow{0%,100%{opacity:.65}50%{opacity:1}}

/* fans */
.fan{transform-box:fill-box;transform-origin:center}
.fanbox .fan path{fill:#59636f;transition:fill .6s}
.fanbox .hub{fill:#7b8693}
.fanbox .ring{stroke:var(--fc,transparent);opacity:0;transition:opacity .6s}
.fanbox.on .fan{animation:spin var(--fspd,1.4s) linear infinite}
.fanbox.on .fan path{fill:var(--fc)}
.fanbox.on .hub{fill:#eef6ff}
.fanbox.on .ring{opacity:.55}
.fanbox.fault .ring{stroke:#ff6e64;opacity:.9}
@keyframes spin{to{transform:rotate(360deg)}}

/* plate exchanger */
.hxbody{fill:url(#gMetal)}
.stack path{fill:none;stroke-linecap:butt}
.stack .pl1{stroke:rgba(255,255,255,.12);stroke-width:1.2}
.stack .pl2{stroke:rgba(0,0,0,.5);stroke-width:2.2}
.hxframe{fill:none;stroke-width:4.5}
.hxinner{fill:none;stroke:rgba(255,255,255,.07);stroke-width:1.5}
.bolt{fill:#59636f;stroke:#16191d;stroke-width:1}
#plates{transition:filter .8s}
#hx.on #plates{filter:drop-shadow(0 0 16px color-mix(in srgb,var(--glow,#9be3c0) 35%,transparent))}
.rib{mix-blend-mode:screen;opacity:calc(var(--co,1) * .85);transition:opacity .8s}
.rib.off{opacity:.18}
.hglow{opacity:0;transition:opacity .8s}
#hx.on .hglow{animation:breathe 3.2s ease-in-out infinite}
@keyframes breathe{0%,100%{opacity:.05}50%{opacity:.22}}
.dots path{fill:none;stroke:url(#gStreak);stroke-width:3.2;stroke-linecap:round;opacity:0}
#hx.on .dots path{animation:slide var(--d,4s) linear infinite;animation-delay:calc(var(--d,4s) * var(--i) * -1)}
#dots_f{opacity:var(--co,1)}
.dots.off path{animation:none!important;opacity:0!important}
@keyframes slide{0%{transform:translateX(calc(var(--L) * -1));opacity:0}18%,82%{opacity:.85}100%{transform:translateX(var(--L));opacity:0}}
.clb{fill:#0f1215}
.cl{transition:fill .6s}
#gCl0 stop,#gCl1 stop,#gCl2 stop,#gCl3 stop{stop-color:#4a525d;transition:stop-color .6s}
#hxfrost,#hxice{opacity:0;transition:opacity .8s}
#hx.defrost #hxfrost{opacity:.22}
#hx.defrost #hxice{opacity:1}
.ice{fill:none;stroke:#e8f6ff;stroke-width:2.4;stroke-linecap:round}
#hx.defrost .ice{animation:twinkle 2.4s ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:.35}50%{opacity:1}}

/* rotary exchanger (R series) */
#rotorg{display:none}
#hx.rotor #rotorg{display:inline}
#hx.rotor #plates,#hx.rotor .cl,#hx.rotor .clb{display:none}
.rotorbg{fill:#1d2228;stroke:#76808d;stroke-width:3}
.rim{fill:none;stroke:#8a96a3;stroke-width:3}.rim.thin{stroke-width:1.4;opacity:.6}
.spokes path{stroke:#68727f;stroke-width:1.6}
.hubr{fill:#2b313a;stroke:#9aa5b1;stroke-width:2}
#wheel{opacity:.85}
#hx.rotor.spin #wheel{animation:spin var(--rspd,4s) linear infinite}

/* controls */
.ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;padding:2px 14px 10px}
.seg{display:flex;gap:4px;padding:4px;border-radius:14px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.06);flex-wrap:wrap}
.mb{display:inline-flex;align-items:center;gap:6px;border:0;border-radius:10px;padding:7px 11px;font:inherit;font-size:13px;font-weight:600;
  color:#9aa3ad;background:transparent;cursor:pointer;transition:background .25s,color .25s}
.mb ha-icon{--mdc-icon-size:18px}
.mb:hover{background:rgba(255,255,255,.06);color:#e6e9ee}
.mb.act{color:var(--mc);background:color-mix(in srgb,var(--mc) 18%,transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--mc) 40%,transparent)}
.mb.busy{opacity:.55;pointer-events:none}
.mb.fire.act{--mc:#ff8a3d}
.alerts{display:flex;flex-wrap:wrap;gap:8px;padding:0 14px 10px}
.alert{display:flex;align-items:center;gap:10px;font-size:13px;padding:8px 10px 8px 12px;border-radius:12px;flex:1 1 220px;
  background:rgba(255,207,112,.08);border:1px solid rgba(255,207,112,.25);color:#ffcf70}
.alert.err{background:rgba(255,110,100,.1);border-color:rgba(255,110,100,.3);color:#ff8a80}
.alert span{flex:1}
.alert button{border:0;border-radius:8px;padding:5px 10px;font:inherit;font-size:12.5px;font-weight:600;cursor:pointer;color:inherit;background:currentColor}
.alert button:disabled{opacity:.5}
.alert button b{color:#16191d}

/* tiles */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:8px;padding:4px 14px 14px}
.tile{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:10px 12px;cursor:pointer;transition:background .2s;min-width:0}
.tile:hover{background:rgba(255,255,255,.07)}
.tl{font-size:11.5px;color:#9aa3ad;text-transform:uppercase;letter-spacing:.6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tv{font-size:21px;font-weight:600;margin-top:3px;font-variant-numeric:tabular-nums;white-space:nowrap}
.tv small{font-size:12.5px;font-weight:500;color:#9aa3ad;margin-left:2px}
.ts{font-size:11.5px;color:#7f8994;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar{height:4px;border-radius:2px;background:rgba(255,255,255,.08);margin-top:6px;overflow:hidden}
.bar i{display:block;height:100%;width:0;border-radius:2px;background:var(--bc,linear-gradient(90deg,#ff6b3d,#ffd54f,#6fdc8c));transition:width .8s}
.narrow .tiles{grid-template-columns:repeat(3,1fr);padding:4px 10px 12px}.narrow .tv{font-size:18px}.narrow .tile{padding:8px 10px}
.vnarrow .tiles{grid-template-columns:repeat(2,1fr)}
.narrow .mb span{display:none}.narrow .mb{padding:8px 10px}
.empty{padding:16px 18px;color:#9aa3ad}
@media (prefers-reduced-motion: reduce){*{animation-duration:0s!important;animation-iteration-count:1!important}}
`;

/* ------------------------------------------------------------------------------------------ */
/*  Card                                                                                       */
/* ------------------------------------------------------------------------------------------ */
class SwegonCasaCard extends HTMLElement {
  static getStubConfig() { return {}; }

  setConfig(config) {
    this._config = Object.assign({ show_header: true, show_controls: true, show_stats: true, entities: {} }, config || {});
    this._map = null;
    if (this.shadowRoot) this._applyLayout();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (!this.shadowRoot) this._build();
    if (first || hass.entities !== this._entsRef) { this._map = null; this._entsRef = hass.entities; }
    this._update();
  }

  getCardSize() { return 9; }
  getGridOptions() { return { columns: 12, min_columns: 6 }; }

  _t() {
    const lang = ((this._hass && ((this._hass.locale && this._hass.locale.language) || this._hass.language)) || "fr").slice(0, 2);
    return T[lang] || T.en;
  }

  /* ---------- build ---------- */
  _build() {
    const root = this.attachShadow({ mode: "open" });
    const t = this._t();
    const modeBtns = MODE_KEYS.map((m) =>
      `<button class="mb" data-mode="${m}" style="--mc:${MODES[m].color}" title="${esc(t.modes[m])}"><ha-icon icon="${MODES[m].icon}"></ha-icon><span>${esc(t.modes[m])}</span></button>`).join("");
    root.innerHTML = `
      <style>${CSS}</style>
      <ha-card>
        <div class="hdr" id="hdr">
          <div><div class="name" id="h_name"></div><div class="subt" id="h_sub"></div></div>
          <div class="chips">
            <span class="badge err" id="b_alarm" data-e="alarm"></span>
            <span class="badge warn" id="b_filter" data-e="filter"></span>
            <span class="badge warn" id="b_service" data-e="service"></span>
            <span class="badge hot" id="b_fire" data-e="fireplace"></span>
            <span class="badge ice" id="b_night" data-e="night_cooling"></span>
            <span class="badge ice" id="b_defrost" data-e="defrost"></span>
            <span class="pill" id="h_mode" data-e="ventilation"><span class="dot"></span><span id="h_mode_t">—</span></span>
          </div>
        </div>
        <div class="empty hide" id="empty"></div>
        <div class="wrap" id="diagram">${buildSVG()}</div>
        <div class="ctl" id="ctl">
          <div class="seg" id="seg">${modeBtns}</div>
          <div class="seg" id="seg2"><button class="mb fire" id="btn_fire"><ha-icon icon="mdi:fireplace"></ha-icon><span>${esc(t.fireplace)}</span></button></div>
        </div>
        <div class="alerts" id="alerts"></div>
        <div class="tiles" id="tiles">
          <div class="tile" data-e="efficiency" id="k_eff_w"><div class="tl">${esc(t.efficiency)}</div><div class="tv" id="k_eff">—</div><div class="bar"><i id="k_eff_b"></i></div></div>
          <div class="tile" data-e="supply_flow" id="k_flow_w"><div class="tl">${esc(t.airflow)}</div><div class="tv" id="k_flow">—</div><div class="ts" id="k_flow_s"></div></div>
          <div class="tile" data-e="supply_fan" id="k_fans_w"><div class="tl">${esc(t.fans)}</div><div class="tv" id="k_fans">—</div><div class="ts" id="k_fans_s"></div></div>
          <div class="tile" data-e="co2" id="k_co2_w"><div class="tl">${esc(t.co2)}</div><div class="tv" id="k_co2">—</div><div class="bar"><i id="k_co2_b"></i></div></div>
          <div class="tile" data-e="humidity" id="k_hum_w"><div class="tl">${esc(t.humidity)}</div><div class="tv" id="k_hum">—</div><div class="ts" id="k_hum_s"></div></div>
          <div class="tile" data-e="voc" id="k_voc_w"><div class="tl">${esc(t.voc)}</div><div class="tv" id="k_voc">—</div><div class="ts" id="k_voc_s"></div></div>
          <div class="tile" data-e="hours_service" id="k_srv_w"><div class="tl">${esc(t.service)}</div><div class="tv" id="k_srv">—</div><div class="ts" id="k_srv_s"></div></div>
        </div>
      </ha-card>`;

    root.addEventListener("click", (ev) => {
      const path = ev.composedPath();
      const btn = path.find((n) => n.dataset && (n.dataset.mode || n.dataset.press));
      if (btn) { btn.dataset.mode ? this._setMode(btn.dataset.mode) : this._press(btn.dataset.press); return; }
      if (path.some((n) => n.id === "btn_fire")) { this._toggleFireplace(); return; }
      const el = path.find((n) => n.dataset && n.dataset.e);
      if (!el) return;
      const id = this._eid(el.dataset.e) || (el.dataset.e === "ventilation" ? this._eid("mode") : null);
      if (id) this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: id }, bubbles: true, composed: true }));
    });
    this._applyLayout();
    const card = root.querySelector("ha-card");
    if (window.ResizeObserver) {
      this._ro = new ResizeObserver((ent) => {
        const w = ent[0].contentRect.width;
        const narrow = w > 0 && w < 640;
        card.classList.toggle("narrow", narrow);
        card.classList.toggle("vnarrow", w > 0 && w < 360);
        card.style.setProperty("--k", (1240 / Math.max(w - 12, 200)).toFixed(3));
        if (narrow !== this._narrow) { this._narrow = narrow; this._update(); }
      });
      this._ro.observe(card);
    }
  }

  _applyLayout() {
    const r = this.shadowRoot;
    if (!r) return;
    const show = (id, on) => { const el = r.getElementById(id); if (el) el.style.display = on ? "" : "none"; };
    show("hdr", this._config.show_header !== false);
    show("ctl", this._config.show_controls !== false);
    show("tiles", this._config.show_stats !== false);
  }

  /* ---------- entity resolution ---------- */
  _resolveAll() {
    const hass = this._hass, cfg = this._config.entities || {}, map = {};
    const disc = {};
    let deviceId = this._config.device_id;
    if (hass.entities) {
      const mine = Object.values(hass.entities).filter((e) => e.platform === DOMAIN);
      if (!deviceId) deviceId = (mine.find((e) => e.translation_key === "fresh_air_temperature") || mine[0] || {}).device_id;
      for (const e of mine) {
        if (deviceId && e.device_id !== deviceId) continue;
        const dom = e.entity_id.split(".")[0];
        const k = e.translation_key ? `${dom}:${e.translation_key}` : dom;
        (disc[k] = disc[k] || []).push(e.entity_id);
      }
    }
    this._deviceId = deviceId;
    const exists = (id) => id && hass.states[id] !== undefined;
    for (const k of new Set([...Object.keys(DISCOVERY), ...Object.keys(cfg)])) {
      if (k in cfg) { map[k] = cfg[k] || null; continue; } // explicit override; null / false hides it
      const d = DISCOVERY[k];
      let found = null;
      if (d && !d[1]) found = (disc[d[0]] || []).find(exists);
      else if (d) for (const tk of d[1]) { found = (disc[`${d[0]}:${tk}`] || []).find(exists); if (found) break; }
      map[k] = found || null;
    }
    this._map = map;
  }
  _eid(k) { if (!this._map) this._resolveAll(); return this._map[k] || null; }
  _st(k) { const id = this._eid(k); return id ? this._hass.states[id] : undefined; }
  _has(k) { return !!this._st(k); }
  _s(k) { const s = this._st(k); return s && s.state !== "unavailable" && s.state !== "unknown" ? s.state : null; }
  _n(k) { const v = parseFloat(this._s(k)); return isNaN(v) ? null : v; }
  _on(k) { const s = this._s(k); return s === "on" || s === "open" || s === "true"; }
  _unit(k) { const s = this._st(k); return (s && s.attributes.unit_of_measurement) || ""; }

  _f(v, d = 1) {
    if (v == null || isNaN(v)) return null;
    const lang = (this._hass.locale && this._hass.locale.language) || this._hass.language || "fr";
    this._fmts = this._fmts || {};
    const key = lang + d;
    if (!this._fmts[key]) this._fmts[key] = new Intl.NumberFormat(lang, { minimumFractionDigits: d, maximumFractionDigits: d });
    return this._fmts[key].format(v);
  }
  _deg() { return this._narrow ? "°" : " °C"; }
  _T(k) { const v = this._n(k); return v == null ? null : `${this._f(v, 1)}${this._deg()}`; }

  /* ---------- DOM helpers ---------- */
  _$(id) { return this.shadowRoot.getElementById(id); }
  _txt(id, t) { const el = this._$(id); if (!el) return; if (t == null || t === "") el.style.display = "none"; else { el.style.display = ""; if (el.textContent !== t) el.textContent = t; } }
  _html(id, h) { const el = this._$(id); if (el && el.innerHTML !== h) el.innerHTML = h; }
  _cls(id, cls, on) { const el = this._$(id); if (el) el.classList.toggle(cls, !!on); }
  _var(id, name, val) { const el = this._$(id); if (el) el.style.setProperty(name, val); }
  _show(id, on) { const el = this._$(id); if (el) el.style.display = on ? "" : "none"; }
  _pipe(id, on, color, spd) {
    const el = this._$(id); if (!el) return;
    el.classList.toggle("on", !!on);
    if (color) el.style.setProperty("--c", color);
    if (spd) el.style.setProperty("--spd", spd);
  }

  /* ---------- computed state (shared with the mini card) ---------- */
  _mode() {
    // Accept the integration's option keys and raw numbers (YAML modbus: 0 = stopped ... 4 = travelling).
    for (const k of ["ventilation", "mode"]) {
      const v = this._s(k);
      if (v == null) continue;
      if (MODES[v]) return v;
      if (/^\d+$/.test(v) && MODE_KEYS[+v]) return MODE_KEYS[+v];
    }
    const fan = this._st("fan");
    if (fan) return fan.state === "off" ? "stopped" : MODES[fan.attributes.preset_mode] ? fan.attributes.preset_mode : "home";
    return null;
  }

  _computeState() {
    const mode = this._mode();
    const unitState = this._s("unit_state");
    const sf = this._n("supply_fan"), ef = this._n("exhaust_fan");
    const sr = this._n("supply_rpm"), er = this._n("exhaust_rpm");
    const avail = ["fresh", "supply", "extract", "exhaust"].some((k) => this._s(k) != null);
    let running;
    if (sf != null || ef != null) running = (sf || 0) > 0 || (ef || 0) > 0;
    else if (sr != null || er != null) running = (sr || 0) > 0 || (er || 0) > 0;
    else running = mode != null && mode !== "stopped" && !["external_stop", "user_stopped"].includes(unitState);
    const sOn = running && (sf == null ? (sr == null || sr > 0) : sf > 0);
    const eOn = running && (ef == null ? (er == null || er > 0) : ef > 0);
    const spd = (pct) => `${clamp(2.3 - (pct == null ? 50 : pct) * 0.018, 0.55, 2.3).toFixed(2)}s`;

    let bypass = this._n("bypass");
    if (bypass == null && this._s("bypass_manual") != null) {
      const v = this._s("bypass_manual");
      bypass = v === "open" || v === "on" || v === "1" ? 100 : 0;
    }
    const fresh = this._n("fresh"), supply = this._n("supply"), extract = this._n("extract"), exhaust = this._n("exhaust");
    const preT = this._n("preheater_temp");
    const supPre = this._n("supply_pre");
    let eff = this._n("efficiency");
    if (eff == null && running && fresh != null && supply != null && extract != null && Math.abs(extract - fresh) >= 2) {
      eff = clamp(((supply - fresh) / (extract - fresh)) * 100, 0, 100);
    }
    const rotor = this._config.exchanger ? this._config.exchanger === "rotor" : this._has("rotor") || this._has("rotor_rpm");
    return { mode, unitState, avail, running, sOn, eOn, sf, ef, sr, er, spd, bypass, fresh, supply, extract, exhaust, preT, supPre, eff, rotor };
  }

  /* ---------- update ---------- */
  _update() {
    if (!this._hass || !this.shadowRoot) return;
    if (!this._map) this._resolveAll();
    const t = this._t();
    const S = this._computeState();
    const found = Object.values(this._map).some(Boolean);
    this._show("empty", !found);
    this._txt("empty", found ? null : t.notFound);
    this._show("diagram", found);
    if (!found) return;

    this._updateHeader(t, S);
    this._updateDiagram(t, S);
    if (this._config.show_controls !== false) this._updateControls(t, S);
    if (this._config.show_stats !== false) this._updateTiles(t, S);
  }

  _deviceName() {
    const dev = this._deviceId && this._hass.devices && this._hass.devices[this._deviceId];
    return (dev && (dev.name_by_user || dev.name)) || "Swegon CASA";
  }

  _updateHeader(t, S) {
    const { mode, unitState, avail } = S;
    this._txt("h_name", this._config.title || this._deviceName());
    const pill = this._$("h_mode");
    let label, color, live;
    if (!avail) { label = t.unreachable; color = "#ff8a80"; live = false; }
    else if (unitState && unitState !== "normal" && t.states[unitState]) {
      label = t.states[unitState]; color = unitState === "starting" ? "#ffd27a" : "#7d8794"; live = unitState === "starting";
    } else {
      label = mode ? t.modes[mode] : "—"; color = mode ? MODES[mode].color : "#7d8794"; live = mode && mode !== "stopped";
      const left = this._n("boost_left");
      if (mode === "boost" && left) label += ` · ${this._f(left, 0)} min`;
    }
    pill.style.setProperty("--mc", color);
    pill.classList.toggle("live", !!live);
    this._txt("h_mode_t", label);

    const sub = [];
    if (unitState && t.states[unitState] && unitState === "normal") sub.push(t.states[unitState]);
    if (this._on("week_timer")) sub.push(t.weekTimer);
    sub.push(S.rotor ? t.rotor : t.plates);
    this._txt("h_sub", sub.join(" · "));

    const alarms = this._alarms();
    const b = (id, on, txt) => { this._cls(id, "show", on); if (on) this._txt(id, txt); };
    b("b_alarm", alarms.length > 0, alarms.length === 1 ? (t.alarms[alarms[0]] || alarms[0]) : `${t.alarm} · ${alarms.length}`);
    b("b_filter", this._on("filter"), t.filterDue);
    b("b_service", this._on("service"), t.serviceDue);
    b("b_fire", this._on("fireplace"), t.fireplace);
    b("b_night", this._on("night_cooling"), t.nightCooling);
    b("b_defrost", this._on("defrost"), t.defrost);
  }

  _alarms() {
    const st = this._st("alarm");
    if (!st || st.state !== "on") return [];
    const list = (st.attributes.alarms || []).filter((a) => a !== "filter_guard" && a !== "service");
    return list.length || (st.attributes.alarms || []).length ? list : ["alarm"];
  }

  _updateDiagram(t, S) {
    const { running, sOn, eOn, sf, ef, spd, bypass, fresh, supply, extract, exhaust, preT, supPre, rotor } = S;
    const bp = bypass == null ? 0 : clamp(bypass, 0, 100) / 100;

    // --- colours along the two air streams ---
    const preActive = this._on("preheater_active") || (this._n("preheater_power") || 0) > 0;
    const afterPre = preT != null ? preT : fresh;
    const exOut = supPre != null ? supPre : supply;
    const cFresh = airColor(fresh), cPre = airColor(afterPre), cSup1 = airColor(exOut), cSup = airColor(supply);
    const cExt = airColor(extract), cExh = airColor(exhaust);
    const sSpd = spd(sf), eSpd = spd(ef);

    this._pipe("a_fresh", sOn, cFresh, sSpd);
    this._pipe("a_pre", sOn, cPre, sSpd);
    this._pipe("a_sup1", sOn, cSup1, sSpd);
    this._pipe("a_sup2", sOn, cSup, sSpd);
    this._pipe("a_ext", eOn, cExt, eSpd);
    this._pipe("a_exh", eOn, cExh, eSpd);
    this._pipe("a_byp", sOn && bp > 0, cPre, sSpd);
    this._var("a_byp", "--bo", bp > 0 ? (0.55 + 0.45 * bp).toFixed(2) : "1");
    this._pipe("x_f", sOn, cPre, sSpd);
    this._pipe("x_e", eOn, cExt, eSpd);


    // --- exchanger ---
    const hx = this._$("hx");
    hx.classList.toggle("on", running);
    hx.classList.toggle("rotor", rotor);
    hx.classList.toggle("defrost", this._on("defrost"));
    this._$("gf0").setAttribute("stop-color", cPre);
    this._$("gf1").setAttribute("stop-color", cSup1);
    this._$("ge0").setAttribute("stop-color", cExt);
    this._$("ge1").setAttribute("stop-color", cExh);
    hx.style.setProperty("--spd", sSpd);
    hx.style.setProperty("--spde", eSpd);
    this._exchanger(sOn, eOn, bp, cPre, cSup1, cExt, cExh);
    const rpm = this._n("rotor_rpm");
    hx.classList.toggle("spin", rotor && running && (rpm == null ? this._on("rotor") || !this._has("rotor") : rpm > 0));
    if (rpm) hx.style.setProperty("--rspd", `${clamp(30 / rpm, 2, 12).toFixed(1)}s`);

    // --- bypass damper ---
    const byp = this._$("byp");
    byp.style.display = bypass == null ? "none" : "";
    this._$("a_byp").style.display = bypass == null ? "none" : "";
    byp.classList.toggle("open", bp > 0);
    byp.style.setProperty("--c", cPre);
    this._$("damper").style.transform = `rotate(${(90 - 90 * bp).toFixed(0)}deg)`;
    this._txt("t_byp", bypass == null ? null : `${t.bypass} ${bp > 0 ? `${this._f(bypass, 0)} %` : t.closed}`);

    // --- efficiency ---
    this._txt("t_eff", S.eff != null ? `${this._f(S.eff, 0)} %` : null);
    const rpmTxt = rotor && rpm != null ? ` · ${t.rotor} ${this._f(rpm, 1)} ${t.rpm}` : "";
    this._txt("l_eff", S.eff != null || rpmTxt ? `${t.efficiency}${rpmTxt}` : null);

    // --- filters ---
    const due = this._on("filter");
    this._cls("flt_f", "due", due); this._cls("flt_e", "due", due);
    this._txt("l_flt_f", t.filter); this._txt("l_flt_e", t.filter);

    // --- heating coils ---
    const coil = (gid, tid, has, on, pct, color, label) => {
      this._show(gid, has);
      if (!has) return;
      const g = this._$(gid);
      g.classList.toggle("on", on);
      g.style.setProperty("--hc", color);
      g.style.setProperty("--hp", on && pct != null ? clamp(pct / 100, 0, 1).toFixed(2) : "0");
      this._txt(tid, pct != null && pct > 0 ? `${label} ${this._f(pct, 0)} %` : label);
    };
    const preP = this._n("preheater_power");
    coil("pre", "t_pre", this._has("preheater_power") || this._has("preheater_active"), preActive && running, preP, "#ff8a3d", t.preheater);
    const heatP = this._n("heater_power");
    const cooling = this._on("cooling");
    coil("post", "t_post", this._has("heater_power") || this._has("cooling"), running && (cooling || (heatP || 0) > 0), heatP,
      cooling ? "#3ddcff" : "#ff6b3d", cooling ? t.cooling : t.postheater);

    // --- fans ---
    const fan = (gid, rid, tid, on, pct, rpmv, faultKey, c) => {
      this._txt(`r_${rid}`, rpmv != null ? `${this._f(rpmv, 0)} ${t.rpm}` : null);
      const g = this._$(gid);
      g.classList.toggle("on", on);
      g.style.setProperty("--fc", c);
      this._var(rid, "--fspd", `${clamp(2.0 - (pct == null ? 50 : pct) * 0.016, 0.35, 2).toFixed(2)}s`);
      g.classList.toggle("fault", this._alarms().includes(faultKey));
      this._txt(tid, pct != null ? `${this._f(pct, 0)} %` : null);
    };
    fan("fan_e", "fe", "t_fe", eOn, ef, S.er, "exhaust_fan_failure", lerpColor(cExh, "#ffffff", 0.15));
    fan("fan_s", "fs", "t_fs", sOn, sf, S.sr, "supply_fan_failure", lerpColor(cSup, "#ffffff", 0.15));

    // --- temperatures ---
    this._txt("l_fresh", t.fresh); this._txt("t_fresh", this._T("fresh") || "—");
    this._txt("l_exh", t.exhaust); this._txt("t_exh", this._T("exhaust") || "—");
    this._txt("l_ext", t.extract); this._txt("t_ext", this._T("extract") || "—");
    this._txt("l_sup", t.supply); this._txt("t_sup", this._T("supply") || "—");
    this._$("t_fresh").style.fill = cFresh; this._$("t_exh").style.fill = cExh;
    this._$("t_ext").style.fill = cExt; this._$("t_sup").style.fill = cSup;
    this._txt("l_out", t.outside);
    this._txt("l_house", t.house);
    this._txt("t_room", this._T("room"));
    this._show("house", true);
  }

  _exchanger(sOn, eOn, bp, cIn, cOut, cExt, cExh) {
    this._var("hx", "--co", (1 - 0.75 * bp).toFixed(2));
    const card = this.shadowRoot.querySelector("ha-card");
    if (card) card.style.setProperty("--glow", lerpColor(cExt, cIn, 0.5));
    this._cls("rib_f", "off", !sOn); this._cls("dots_f", "off", !sOn);
    this._cls("rib_e", "off", !eOn); this._cls("dots_e", "off", !eOn);
    const collar = (gid, c, on) => this.shadowRoot.querySelectorAll(`#${gid} stop`).forEach((st) => { st.style.stopColor = on ? c : ""; });
    collar("gCl0", cIn, sOn); collar("gCl1", cOut, sOn); collar("gCl2", cExt, eOn); collar("gCl3", cExh, eOn);
  }

  _updateControls(t, S) {
    const hasMode = this._has("mode") || this._has("fan");
    this._show("seg", hasMode);
    this.shadowRoot.querySelectorAll(".mb[data-mode]").forEach((b) => {
      b.classList.toggle("act", b.dataset.mode === S.mode);
      b.classList.toggle("busy", this._busy === "mode");
    });
    const hasFire = this._has("fireplace");
    this._show("seg2", hasFire);
    this._cls("btn_fire", "act", this._on("fireplace"));
    this._cls("btn_fire", "busy", this._busy === "fireplace");

    const items = [];
    for (const a of this._alarms()) items.push(`<div class="alert err"><span>${esc(t.alarms[a] || t.alarm)}</span></div>`);
    if (this._on("filter")) {
      items.push(`<div class="alert"><span>${esc(t.filterDue)}</span>${this._has("confirm_filter") ? `<button data-press="confirm_filter"${this._busy === "confirm_filter" ? " disabled" : ""}><b>${esc(t.confirm)}</b></button>` : ""}</div>`);
    }
    if (this._on("service")) {
      items.push(`<div class="alert"><span>${esc(t.serviceDue)}</span>${this._has("confirm_service") ? `<button data-press="confirm_service"${this._busy === "confirm_service" ? " disabled" : ""}><b>${esc(t.confirm)}</b></button>` : ""}</div>`);
    }
    this._html("alerts", items.join(""));
    this._show("alerts", items.length > 0);
  }

  _updateTiles(t, S) {
    const tile = (id, has) => this._show(`${id}_w`, has);

    tile("k_eff", S.eff != null || this._has("efficiency"));
    this._html("k_eff", S.eff != null ? `${this._f(S.eff, 0)}<small>%</small>` : "—");
    this._$("k_eff_b").style.width = `${S.eff != null ? clamp(S.eff, 0, 100) : 0}%`;

    const flow = (k) => {
      const v = this._n(k);
      if (v == null) return null;
      const u = this._unit(k).toLowerCase();
      return u.includes("m³") || u.includes("m3") ? v : v * 3.6;
    };
    const fs = flow("supply_flow"), fe = flow("exhaust_flow");
    tile("k_flow", this._has("supply_flow") || this._has("exhaust_flow"));
    this._html("k_flow", fs != null ? `${this._f(fs, 0)}<small>m³/h</small>` : "—");
    this._txt("k_flow_s", fe != null ? `${t.extractShort} ${this._f(fe, 0)} m³/h` : "");

    tile("k_fans", this._has("supply_fan") || this._has("exhaust_fan"));
    this._html("k_fans", S.sf != null ? `${this._f(S.sf, 0)}<small>%</small>` : "—");
    this._txt("k_fans_s", S.ef != null ? `${t.extractShort} ${this._f(S.ef, 0)} %` : "");

    const co2 = this._n("co2");
    tile("k_co2", this._has("co2"));
    this._html("k_co2", co2 != null ? `${this._f(co2, 0)}<small>ppm</small>` : "—");
    const co2c = co2 == null ? "#4a525d" : co2 < 800 ? "#6fdc8c" : co2 < 1000 ? "#ffd54f" : co2 < 1400 ? "#ff9f43" : "#ff6e64";
    const b = this._$("k_co2_b");
    b.style.width = `${co2 != null ? clamp((co2 - 400) / 16, 4, 100) : 0}%`;
    b.style.setProperty("--bc", co2c);

    const hum = this._n("humidity"), ah = this._n("abs_humidity");
    tile("k_hum", this._has("humidity"));
    this._html("k_hum", hum != null ? `${this._f(hum, 0)}<small>%</small>` : "—");
    this._txt("k_hum_s", ah != null ? `${this._f(ah, 1)} g/m³` : "");

    const voc = this._n("voc");
    tile("k_voc", this._has("voc"));
    this._html("k_voc", voc != null ? `${this._f(voc, 0)}<small>ppm</small>` : "—");
    this._txt("k_voc_s", "");

    const h = this._n("hours_service");
    tile("k_srv", this._has("hours_service"));
    this._html("k_srv", h != null ? `${this._f(h, 0)}<small>h</small>` : "—");
    this._txt("k_srv_s", h != null ? t.inDays(this._f(h / 24, 0)) : "");
  }

  /* ---------- actions ---------- */
  async _run(key, fn) {
    this._busy = key;
    this._update();
    try { await fn(); } catch (err) {
      this.dispatchEvent(new CustomEvent("hass-notification", { detail: { message: String((err && err.message) || err) }, bubbles: true, composed: true }));
    } finally { this._busy = null; this._update(); }
  }

  _setMode(mode) {
    const sel = this._st("mode");
    if (sel && (sel.attributes.options || []).includes(mode)) {
      this._run("mode", () => this._hass.callService("select", "select_option", { entity_id: sel.entity_id, option: mode }));
      return;
    }
    const fan = this._eid("fan");
    if (!fan) return;
    this._run("mode", () => (mode === "stopped"
      ? this._hass.callService("fan", "turn_off", { entity_id: fan })
      : this._hass.callService("fan", "set_preset_mode", { entity_id: fan, preset_mode: mode === "travelling" ? "travelling" : mode })));
  }

  _toggleFireplace() {
    const id = this._eid("fireplace");
    if (id) this._run("fireplace", () => this._hass.callService("switch", this._on("fireplace") ? "turn_off" : "turn_on", { entity_id: id }));
  }

  _press(key) {
    const id = this._eid(key);
    if (id) this._run(key, () => this._hass.callService("button", "press", { entity_id: id }));
  }
}

/* ------------------------------------------------------------------------------------------ */
/*  Mini card                                                                                  */
/* ------------------------------------------------------------------------------------------ */
const MINI_CSS = `
.mwrap{container-type:inline-size}
.mini{display:grid;grid-template-columns:minmax(110px,150px) 1fr;gap:6px 14px;align-items:center;padding:12px 14px 12px 10px}
.mini svg{width:100%;height:auto;display:block}
.mini .duct .pb{stroke-width:11}.mini .duct .pg{stroke-width:13}.mini .duct .pc{stroke-width:6}
.mini .duct .pf{stroke-width:1.8;stroke-dasharray:1.5 9}.mini .duct.on .pf{animation-name:flowm}
.mini .dots path{stroke-width:1.6}
.mini .stack .pl1,.mini .stack .pl2{stroke-width:.8}.mini .hxframe{stroke-width:1.6}.mini .hxinner{display:none}
@keyframes flowm{to{stroke-dashoffset:-10.5}}
@keyframes flowm2{to{stroke-dashoffset:-9.1}}
.mtop{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;min-width:0}
.mname{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mini .pill{padding:4px 10px 4px 8px;font-size:12px}
.mstats{display:grid;grid-template-columns:repeat(auto-fit,minmax(46px,1fr));gap:4px 8px;margin-top:8px}
.ms{cursor:pointer;min-width:0}
.ms .l{font-size:10.5px;color:#9aa3ad;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
.ms .v{font-size:16px;font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.ms .v small{font-size:11px;color:#9aa3ad;font-weight:500;margin-left:1px}
.ms.hide{display:none}
.mclick{cursor:pointer}
@container (max-width:400px){.mini{grid-template-columns:92px 1fr;gap:4px 10px;padding:10px 12px 10px 8px}.mname{display:none}
  .mtop{justify-content:flex-start}.ms .v{font-size:15px}.mstats{grid-template-columns:repeat(auto-fit,minmax(42px,1fr));gap:3px 6px}}
@container (max-width:260px){.mini{grid-template-columns:1fr}.mini svg{max-width:160px;margin:0 auto}}
`;

function buildMiniSVG() {
  const hx = exchanger({ hs: 26, band: 26, lanes: [0], flare: 12, hc: 3, hb: 5.5, bolts: false });
  return `
<svg viewBox="0 0 200 122" xmlns="http://www.w3.org/2000/svg">
  <defs>${hx.defs}</defs>
  ${pipe("mp_fresh", "M4 22 H58 L82 42", "duct")}
  ${pipe("mp_ext", "M196 22 H142 L118 42", "duct")}
  ${pipe("mp_exh", "M82 80 L58 100 H4", "duct")}
  ${pipe("mp_sup", "M118 80 L142 100 H196", "duct")}
  <g id="hx" class="mclick" data-e="efficiency">
    <g transform="translate(100 61) rotate(45)">${hx.body}</g>
  </g>
</svg>`;
}

class SwegonCasaMiniCard extends SwegonCasaCard {
  getCardSize() { return 2; }
  getGridOptions() { return { columns: 6, min_columns: 4, rows: 2 }; }

  _build() {
    const root = this.attachShadow({ mode: "open" });
    const t = this._t();
    root.innerHTML = `
      <style>${CSS}${MINI_CSS}</style>
      <ha-card class="mwrap">
        <div class="mini">
          <div class="mclick" id="msvg">${buildMiniSVG()}</div>
          <div style="min-width:0">
            <div class="mtop">
              <div class="mname" id="m_name"></div>
              <span class="pill" id="h_mode" data-e="ventilation"><span class="dot"></span><span id="h_mode_t">—</span></span>
            </div>
            <div class="mstats">
              <div class="ms" data-e="fresh"><div class="l">${esc(t.short.out)}</div><div class="v" id="m_out">—</div></div>
              <div class="ms" data-e="supply"><div class="l">${esc(t.short.supply)}</div><div class="v" id="m_sup">—</div></div>
              <div class="ms" data-e="efficiency"><div class="l">${esc(t.short.eff)}</div><div class="v" id="m_eff">—</div></div>
              <div class="ms" data-e="co2" id="m_co2_w"><div class="l">${esc(t.co2)}</div><div class="v" id="m_co2">—</div></div>
            </div>
          </div>
        </div>
      </ha-card>`;
    root.addEventListener("click", (ev) => {
      const path = ev.composedPath();
      const nav = this._config.navigation_path;
      if (nav && path.some((n) => n.id === "msvg")) {
        history.pushState(null, "", nav);
        window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
        return;
      }
      const el = path.find((n) => n.dataset && n.dataset.e);
      const id = el ? this._eid(el.dataset.e) || this._eid("mode") : this._eid("fan") || this._eid("mode");
      if (id) this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: id }, bubbles: true, composed: true }));
    });
  }

  _applyLayout() {}

  _update() {
    if (!this._hass || !this.shadowRoot) return;
    if (!this._map) this._resolveAll();
    const t = this._t();
    const S = this._computeState();
    this._txt("m_name", this._config.title || this._deviceName());
    this._updateHeader(t, S);

    const cFresh = airColor(S.fresh), cSup = airColor(S.supply), cExt = airColor(S.extract), cExh = airColor(S.exhaust);
    const sSpd = S.spd(S.sf), eSpd = S.spd(S.ef);
    this._pipe("mp_fresh", S.sOn, cFresh, sSpd);
    this._pipe("mp_sup", S.sOn, cSup, sSpd);
    this._pipe("mp_ext", S.eOn, cExt, eSpd);
    this._pipe("mp_exh", S.eOn, cExh, eSpd);
    const hx = this._$("hx");
    hx.classList.toggle("on", S.running);
    hx.style.setProperty("--spd", sSpd);
    hx.style.setProperty("--spde", eSpd);
    this._$("gf0").setAttribute("stop-color", cFresh);
    this._$("gf1").setAttribute("stop-color", cSup);
    this._$("ge0").setAttribute("stop-color", cExt);
    this._$("ge1").setAttribute("stop-color", cExh);
    this._exchanger(S.sOn, S.eOn, S.bypass ? clamp(S.bypass, 0, 100) / 100 : 0, cFresh, cSup, cExt, cExh);

    const deg = (v) => (v == null ? "—" : `${this._f(v, 1)}<small>°</small>`);
    this._html("m_out", deg(S.fresh));
    this._html("m_sup", deg(S.supply));
    this._html("m_eff", S.eff != null ? `${this._f(S.eff, 0)}<small>%</small>` : "—");
    const co2 = this._n("co2");
    this._html("m_co2", co2 != null ? `${this._f(co2, 0)}<small>ppm</small>` : "—");
    this._cls("m_co2_w", "hide", !this._has("co2"));
  }
}

if (!customElements.get("swegon-casa-card")) customElements.define("swegon-casa-card", SwegonCasaCard);
if (!customElements.get("swegon-casa-mini-card")) customElements.define("swegon-casa-mini-card", SwegonCasaMiniCard);
window.customCards = window.customCards || [];
if (!window.customCards.find((c) => c.type === "swegon-casa-card")) {
  window.customCards.push({
    type: "swegon-casa-card",
    name: "Swegon CASA",
    description: "Schéma animé de la centrale double flux : échangeur à flux croisés, by-pass, batteries, ventilateurs, modes et qualité d'air.",
    preview: true,
  });
}
if (!window.customCards.find((c) => c.type === "swegon-casa-mini-card")) {
  window.customCards.push({
    type: "swegon-casa-mini-card",
    name: "Swegon CASA — Mini",
    description: "Version compacte : mode, températures, rendement et CO₂.",
    preview: true,
  });
}
console.info(`%c SWEGON-CASA-CARD %c v${CARD_VERSION} `, "background:#3d7bff;color:#fff;font-weight:700;border-radius:4px 0 0 4px", "background:#22262c;color:#fff;border-radius:0 4px 4px 0");
