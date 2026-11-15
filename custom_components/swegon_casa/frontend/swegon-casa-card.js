/*
 * Swegon CASA card for Home Assistant, shipped with the swegon_casa integration.
 *
 *   type: custom:swegon-casa-card
 *   device_id: <optional, when several units are configured>
 *   title: <optional>
 *
 * Entities are found by themselves (platform + translation key).
 */

const DOMAIN = "swegon_casa";
const CARD_VERSION = "0.1.0";

const T = {
  fr: {
    outside: "Extérieur", house: "Maison",
    fresh: "Air neuf", supply: "Soufflage", extract: "Extraction", exhaust: "Rejet",
    modes: { stopped: "Arrêt", away: "Absent", home: "Maison", boost: "Boost", travelling: "Voyage" },
    states: { external_stop: "Arrêt externe", user_stopped: "Arrêtée", starting: "Démarrage", normal: "En marche", commissioning: "Mise en service" },
    efficiency: "Rendement", airflow: "Débit", fans: "Ventilateurs", room: "Ambiance",
    co2: "CO2", humidity: "Humidité", voc: "COV",
    fireplace: "Cheminée", nightCooling: "Rafraîchissement nocturne", active: "actif",
    alarm: "Alarme", filter: "Filtre à remplacer", service: "Entretien à prévoir", confirm: "Acquitter",
    serviceIn: (h) => `Entretien dans ${h} h`, notFound: "Aucune centrale Swegon CASA trouvée.",
    rotor: "Roue", defrost: "Dégivrage", unavailable: "Centrale injoignable",
    bypass: "By-pass", preheater: "Préchauffe", postheater: "Post-chauffe",
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
    efficiency: "Efficiency", airflow: "Airflow", fans: "Fans", room: "Room",
    co2: "CO2", humidity: "Humidity", voc: "VOC",
    fireplace: "Fireplace", nightCooling: "Night cooling", active: "active",
    alarm: "Alarm", filter: "Replace the filter", service: "Service due", confirm: "Confirm",
    serviceIn: (h) => `Service in ${h} h`, notFound: "No Swegon CASA unit found.",
    rotor: "Rotor", defrost: "Defrost", unavailable: "Unit unreachable",
    bypass: "Bypass", preheater: "Preheater", postheater: "Re-heater",
    alarms: {},
  },
};

const ICON = {
  fan: "M12 11a1 1 0 1 0 0 2 1 1 0 0 0 0-2m.5-9C17 2 17.11 5.57 14.75 6.75c-.99.49-1.43 1.54-1.62 2.47.48.2.9.51 1.22.91 3.7-2 7.68-1.21 7.68 2.37C22 17 18.43 17.11 17.25 14.75c-.5-.99-1.56-1.43-2.48-1.62-.2.48-.51.89-.91 1.22 2 3.69 1.2 7.65-2.36 7.65C7 22 6.89 18.42 9.24 17.24c.98-.49 1.42-1.53 1.62-2.45-.49-.2-.92-.52-1.24-.92C5.94 15.87 2 15.08 2 11.5 2 7 5.56 6.89 6.74 9.26c.5.99 1.55 1.42 2.48 1.61.19-.48.51-.9.92-1.22C8.15 5.96 8.94 2 12.5 2z",
  fire: "M17.66 11.2c-.23-.3-.51-.56-.77-.82-.67-.6-1.43-1.03-2.07-1.66C13.33 7.26 13 4.85 13.95 3c-.95.23-1.78.75-2.49 1.32-2.59 2.08-3.61 5.75-2.39 8.9.04.1.08.2.08.33 0 .22-.15.42-.35.5-.23.1-.47.04-.66-.12a.58.58 0 0 1-.14-.17c-1.13-1.43-1.31-3.48-.55-5.12C5.78 10 4.87 12.3 5 14.47c.06.5.12 1 .29 1.5.14.6.41 1.2.71 1.73 1.08 1.73 2.95 2.97 4.96 3.22 2.14.27 4.43-.12 6.07-1.6 1.83-1.66 2.47-4.32 1.53-6.6l-.13-.26c-.21-.46-.77-1.26-.77-1.26z",
  moon: "M17.75 4.09 15.22 6.03l.91 3.06-2.63-1.81-2.63 1.81.91-3.06-2.53-1.94L12.44 4l1.06-3 1.06 3 3.19.09m3.5 6.91-1.64 1.25.59 1.98-1.7-1.17-1.7 1.17.59-1.98L15.75 11l2.06-.05L18.5 9l.69 1.95 2.06.05m-2.28 4.95c.83-.08 1.72 1.1 1.19 1.85-.32.45-.66.87-1.08 1.27C15.17 23 8.84 23 4.94 19.07c-3.91-3.9-3.91-10.24 0-14.14.4-.4.82-.76 1.27-1.08.75-.53 1.93.36 1.85 1.19-.27 2.86.69 5.83 2.89 8.02a9.96 9.96 0 0 0 8.02 2.89z",
  alert: "M13 14h-2V9h2m0 9h-2v-2h2M1 21h22L12 2 1 21z",
  wrench: "M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z",
};

function icon(name, size = 18) {
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" aria-hidden="true"><path fill="currentColor" d="${ICON[name]}"/></svg>`;
}

function esc(v) {
  return String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

class SwegonCasaCard extends HTMLElement {
  static getStubConfig() {
    return {};
  }

  setConfig(config) {
    this._config = config || {};
    this._busy = null;
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    this._sig = null;
  }

  getCardSize() {
    return 8;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6, rows: "auto" };
  }

  set hass(hass) {
    this._hass = hass;
    this._map = this._find();
    const ids = Object.values(this._map);
    const sig = JSON.stringify([ids.map((id) => [id, hass.states[id]?.state, hass.states[id]?.last_updated]), this._busy, hass.language]);
    if (sig === this._sig) return;
    this._sig = sig;
    this._render();
  }

  _t() {
    const lang = (this._hass?.locale?.language || this._hass?.language || "en").slice(0, 2);
    const base = T[lang] || T.en;
    return { ...T.en, ...base, alarms: { ...T.fr.alarms, ...(base.alarms || {}) } };
  }

  _find() {
    const mine = Object.values(this._hass?.entities || {}).filter((e) => e.platform === DOMAIN);
    const deviceId = this._config.device_id || mine[0]?.device_id;
    const map = {};
    for (const e of mine) {
      if (e.device_id !== deviceId || !e.translation_key) continue;
      map[`${e.entity_id.split(".")[0]}.${e.translation_key}`] = e.entity_id;
    }
    this._deviceId = deviceId;
    return map;
  }

  _s(key) {
    const id = this._map[key];
    return id ? this._hass.states[id] : undefined;
  }

  _n(key) {
    const v = parseFloat(this._s(key)?.state);
    return Number.isFinite(v) ? v : null;
  }

  _on(key) {
    return this._s(key)?.state === "on";
  }

  _fmt(v, digits = 0, unit = "") {
    if (v === null || v === undefined) return "–";
    const locale = this._hass?.locale?.language || this._hass?.language || "fr";
    return new Intl.NumberFormat(locale, { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(v) + unit;
  }

  _name() {
    if (this._config.title) return this._config.title;
    const d = this._hass?.devices?.[this._deviceId];
    return d?.name_by_user || d?.name || "Swegon CASA";
  }

  _exchangerType() {
    if (this._config.exchanger) return this._config.exchanger;
    if (this._map["binary_sensor.rotor_active"] || this._map["sensor.rotor_rpm"]) return "rotor";
    const model = this._hass?.devices?.[this._deviceId]?.model || "";
    return /\bR\d/i.test(model) ? "rotor" : "plate";
  }

  _bypassPct() {
    const auto = this._n("sensor.bypass_position");
    if (auto !== null) return Math.max(0, Math.min(100, auto));
    const manual = this._s("sensor.manual_bypass")?.state;
    if (manual === "open") return 100;
    if (manual === "closed") return 0;
    return null;
  }

  _coil(x, y, label, power, active, cooling) {
    // A finned battery across the duct; red when heating, blue when cooling.
    const tone = cooling ? "cool" : active || (power ?? 0) > 0 ? "heat" : "idle";
    const fins = Array.from({ length: 5 }, (_, i) => `<line x1="${x - 7}" y1="${y - 13 + i * 6.5}" x2="${x + 7}" y2="${y - 13 + i * 6.5}"/>`).join("");
    return `
      <g class="coil ${tone}">
        <rect x="${x - 8}" y="${y - 16}" width="16" height="32" rx="3"/>
        <g class="fins">${fins}</g>
        <text class="coil-label" x="${x}" y="${y + 30}" text-anchor="middle">${esc(label)}</text>
        ${power !== null && power !== undefined ? `<text class="coil-value" x="${x}" y="${y + 41}" text-anchor="middle">${this._fmt(power, 0, " %")}</text>` : ""}
      </g>`;
  }

  _diagram(t) {
    const fresh = this._n("sensor.fresh_air_temperature");
    const supply = this._n("sensor.supply_air_temperature");
    const extract = this._n("sensor.extract_air_temperature");
    const exhaust = this._n("sensor.exhaust_air_temperature");
    const supplyPct = this._n("sensor.supply_fan_control") ?? 0;
    const exhaustPct = this._n("sensor.exhaust_fan_control") ?? 0;
    const type = this._exchangerType();
    const rotorOn = this._on("binary_sensor.rotor_active");
    const defrost = this._on("binary_sensor.defrost");
    const bypass = this._bypassPct();
    const running = (this._s("fan.ventilation")?.state ?? "on") === "on" && (supplyPct > 0 || exhaustPct > 0);
    const dur = (pct) => Math.max(0.5, 3.2 - pct / 40).toFixed(2);
    const air = (cls, d, pct, opacity = 1) =>
      `<path class="air ${cls} ${running && pct > 0 ? "flowing" : ""}" d="${d}" style="opacity:${opacity.toFixed(2)};animation-duration:${dur(pct)}s"/>`;
    const tag = (x, y, label, value, cls, anchor = "start") => `
      <g class="tag ${cls}" transform="translate(${x} ${y})" text-anchor="${anchor}">
        <text class="tag-label" y="-6">${esc(label)}</text>
        <text class="tag-value" y="14">${value === null ? "–" : this._fmt(value, 1, " °C")}</text>
      </g>`;
    const fan = (x, y, pct) => `
      <g transform="translate(${x} ${y})">
        <g class="fan-icon ${running && pct > 0 ? "spinning" : ""}" style="animation-duration:${dur(pct)}s">
          <path transform="translate(-10 -10) scale(0.84)" fill="currentColor" d="${ICON.fan}"/>
        </g>
      </g>`;

    // Air path through the exchanger, and around it when the bypass opens.
    const share = bypass === null ? 0 : bypass / 100;
    const freshThrough = "M152 62 Q 162 62 168 104 L 232 104 Q 238 62 248 62";
    const extractThrough = "M248 168 Q 238 168 232 126 L 168 126 Q 162 168 152 168";
    const exchanger =
      type === "rotor"
        ? `<g transform="translate(200 115)">
             <g class="rotor ${rotorOn ? "spinning" : ""} ${defrost ? "defrost" : ""}">
               <circle r="34" class="rotor-ring"/>
               ${Array.from({ length: 12 }, (_, i) => `<line x1="0" y1="0" x2="${(32 * Math.cos((i * Math.PI) / 6)).toFixed(1)}" y2="${(32 * Math.sin((i * Math.PI) / 6)).toFixed(1)}" class="rotor-spoke"/>`).join("")}
               <circle r="6" class="rotor-hub"/>
             </g>
           </g>`
        : `<g class="plates ${defrost ? "defrost" : ""}">
             <polygon points="160,115 174,90 226,90 240,115 226,140 174,140" class="plate-body"/>
             ${Array.from({ length: 7 }, (_, i) => `<line x1="${170 - (i % 2)}" y1="${94 + i * 7}" x2="${230 + (i % 2)}" y2="${94 + i * 7}" class="plate-line ${i % 2 ? "warm" : "cold"}"/>`).join("")}
           </g>`;
    const damperAngle = bypass === null ? 90 : 90 - bypass * 0.9; // 90° = closed across the channel
    const bypassDrawing =
      bypass === null
        ? ""
        : `<path class="bypass-channel" d="M152 62 H248"/>
           ${air("cold", "M152 62 H248", supplyPct, share)}
           <g transform="translate(200 62)">
             <line class="damper" x1="0" y1="-9" x2="0" y2="9" transform="rotate(${(damperAngle - 90).toFixed(1)})"/>
             <circle r="2.5" class="damper-pivot"/>
           </g>
           <text class="bypass-label" x="200" y="46" text-anchor="middle">${esc(t.bypass)} ${this._fmt(bypass, 0, " %")}</text>`;

    const pre = this._map["sensor.preheater_power"] || this._map["binary_sensor.preheater_active"];
    const post = this._map["sensor.supply_control_power"];
    const preCoil = pre ? this._coil(130, 62, t.preheater, this._n("sensor.preheater_power"), this._on("binary_sensor.preheater_active"), false) : "";
    const postCoil = post ? this._coil(262, 62, t.postheater, this._n("sensor.supply_control_power"), false, this._on("binary_sensor.cooling_active")) : "";

    return `
      <svg class="diagram" viewBox="0 0 400 240" role="img" aria-label="CASA">
        <text class="side" transform="translate(12 115) rotate(-90)" text-anchor="middle">${esc(t.outside)}</text>
        <text class="side" transform="translate(390 115) rotate(90)" text-anchor="middle">${esc(t.house)}</text>
        <path class="duct cold" d="M30 62 H110"/>${air("cold", "M30 62 H110", supplyPct)}
        <path class="duct warm" d="M290 62 H370"/>${air("warm", "M290 62 H370", supplyPct)}
        <path class="arrow warm" d="M364 54 L376 62 L364 70"/>
        <path class="duct hot" d="M370 168 H290"/>${air("hot", "M370 168 H290", exhaustPct)}
        <path class="duct used" d="M110 168 H30"/>${air("used", "M110 168 H30", exhaustPct)}
        <path class="arrow used" d="M36 160 L24 168 L36 176"/>
        <rect class="unit" x="110" y="28" width="180" height="176" rx="16"/>
        <!-- internal ducts -->
        <path class="inner cold" d="M110 62 H152"/>${air("cold", "M110 62 H152", supplyPct)}
        <path class="inner warm" d="M248 62 H290"/>${air("warm", "M248 62 H290", supplyPct)}
        <path class="inner hot" d="M290 168 H248"/>${air("hot", "M290 168 H248", exhaustPct)}
        <path class="inner used" d="M152 168 H110"/>${air("used", "M152 168 H110", exhaustPct)}
        <path class="inner cold" d="${freshThrough}"/>${air("cold", freshThrough, supplyPct, 1 - share * 0.85)}
        <path class="inner hot" d="${extractThrough}"/>${air("hot", extractThrough, exhaustPct)}
        ${exchanger}
        ${bypassDrawing}
        ${preCoil}
        ${postCoil}
        ${fan(276, 42, supplyPct)}
        ${fan(124, 188, exhaustPct)}
        ${tag(34, 38, t.fresh, fresh, "cold")}
        ${tag(366, 38, t.supply, supply, "warm", "end")}
        ${tag(366, 196, t.extract, extract, "hot", "end")}
        ${tag(34, 196, t.exhaust, exhaust, "used")}
      </svg>`;
  }

  _quality(t) {
    const co2 = this._n("sensor.co2");
    const rh = this._n("sensor.humidity");
    const voc = this._n("sensor.voc");
    const room = this._n("sensor.room_temperature");
    const level = (v, a, b) => (v === null ? "" : v < a ? "good" : v < b ? "fair" : "poor");
    const chip = (label, value, cls) => `<div class="chip ${cls}"><span class="chip-label">${esc(label)}</span><span class="chip-value">${value}</span></div>`;
    const chips = [];
    if (room !== null) chips.push(chip(t.room, this._fmt(room, 1, " °C"), ""));
    if (co2 !== null) chips.push(chip(t.co2, this._fmt(co2, 0, " ppm"), level(co2, 800, 1200)));
    if (rh !== null) chips.push(chip(t.humidity, this._fmt(rh, 0, " %"), rh < 30 || rh > 70 ? "fair" : "good"));
    if (voc !== null) chips.push(chip(t.voc, this._fmt(voc, 0, " ppm"), level(voc, 500, 1000)));
    return chips.length ? `<div class="chips">${chips.join("")}</div>` : "";
  }

  _render() {
    const t = this._t();
    const root = this.shadowRoot;
    if (!this._hass) return;
    if (!Object.keys(this._map).length) {
      root.innerHTML = `<ha-card><div class="empty">${t.notFound}</div></ha-card>`;
      return;
    }
    const modeSel = this._s("select.operating_mode");
    const mode = modeSel?.state;
    const unitState = this._s("sensor.unit_state")?.state;
    const unavailable = !modeSel || modeSel.state === "unavailable";
    const alarm = this._on("binary_sensor.alarm");
    const alarms = this._s("binary_sensor.alarm")?.attributes?.alarms || [];
    const filter = this._on("binary_sensor.filter_info");
    const service = this._on("binary_sensor.service_info");
    const realAlarms = alarms.filter((a) => !["filter_guard", "service"].includes(a));
    const pill = unavailable
      ? { cls: "error", text: t.unavailable }
      : realAlarms.length
        ? { cls: "error", text: t.alarm }
        : { cls: unitState === "normal" ? "ok" : "idle", text: t.states[unitState] || unitState || "–" };
    const eff = this._n("sensor.heat_recovery_efficiency");
    const supFlow = this._n("sensor.supply_airflow");
    const exFlow = this._n("sensor.exhaust_airflow");
    const supPct = this._n("sensor.supply_fan_control");
    const exPct = this._n("sensor.exhaust_fan_control");
    const hours = this._n("sensor.hours_to_service");
    const fireplace = this._s("switch.fireplace");
    const nightCooling = this._on("binary_sensor.summer_cooling_active");
    const modes = ["stopped", "away", "home", "boost", "travelling"];

    root.innerHTML = `
      <style>${STYLE}</style>
      <ha-card>
        <div class="header">
          <div class="title">${esc(this._name())}</div>
          <div class="pill ${pill.cls}"><span class="dot"></span>${esc(pill.text)}</div>
        </div>
        ${realAlarms.length ? `<div class="banner error">${icon("alert")} ${realAlarms.map((a) => esc(t.alarms[a] || a)).join(" · ")}</div>` : ""}
        ${filter || service ? `<div class="banner warn">${icon("wrench")} <span>${[filter ? t.filter : "", service ? t.service : ""].filter(Boolean).join(" · ")}</span>
          ${this._map[filter ? "button.confirm_filter" : "button.confirm_service"] ? `<button class="link" data-press="${filter ? "button.confirm_filter" : "button.confirm_service"}">${t.confirm}</button>` : ""}</div>` : ""}
        ${this._diagram(t)}
        <div class="stats">
          <div><span class="stat-label">${t.efficiency}</span><span class="stat-value">${this._fmt(eff, 0, " %")}</span></div>
          <div><span class="stat-label">${t.airflow}</span><span class="stat-value">${supFlow !== null ? `${this._fmt(supFlow * 3.6, 0)} / ${this._fmt((exFlow ?? 0) * 3.6, 0)} m³/h` : "–"}</span></div>
          <div><span class="stat-label">${t.fans}</span><span class="stat-value">${supPct !== null ? `${this._fmt(supPct, 0)} / ${this._fmt(exPct, 0)} %` : "–"}</span></div>
        </div>
        <div class="modes" role="radiogroup">
          ${modes.map((m) => `<button class="mode ${mode === m ? "active" : ""} ${m}" data-mode="${m}" ${modeSel && !unavailable && this._busy !== "mode" ? "" : "disabled"} role="radio" aria-checked="${mode === m}">${esc(t.modes[m])}</button>`).join("")}
        </div>
        ${this._quality(t)}
        <div class="footer">
          ${fireplace ? `<button class="toggle ${fireplace.state === "on" ? "on" : ""}" data-toggle="switch.fireplace" ${this._busy === "switch.fireplace" ? "disabled" : ""}>${icon("fire", 16)} ${t.fireplace}</button>` : ""}
          ${nightCooling ? `<span class="badge">${icon("moon", 14)} ${t.nightCooling} ${t.active}</span>` : ""}
          ${hours !== null ? `<span class="muted">${t.serviceIn(this._fmt(hours, 0))}</span>` : ""}
        </div>
      </ha-card>`;

    root.querySelectorAll("[data-mode]").forEach((el) => el.addEventListener("click", () => this._setMode(el.dataset.mode)));
    root.querySelectorAll("[data-toggle]").forEach((el) => el.addEventListener("click", () => this._toggle(el.dataset.toggle)));
    root.querySelectorAll("[data-press]").forEach((el) => el.addEventListener("click", () => this._press(el.dataset.press)));
    root.querySelector(".diagram")?.addEventListener("click", () => this._more("sensor.supply_air_temperature"));
  }

  async _run(key, call) {
    this._busy = key;
    this._sig = null;
    this._render();
    try {
      await call();
    } catch (err) {
      this.dispatchEvent(new CustomEvent("hass-notification", { detail: { message: err?.message || String(err) }, bubbles: true, composed: true }));
    } finally {
      this._busy = null;
      this._sig = null;
      if (this._hass) this.hass = this._hass;
    }
  }

  _setMode(option) {
    const id = this._map["select.operating_mode"];
    if (!id || this._hass.states[id]?.state === option) return;
    this._run("mode", () => this._hass.callService("select", "select_option", { entity_id: id, option }));
  }

  _toggle(key) {
    const id = this._map[key];
    if (!id) return;
    const on = this._hass.states[id]?.state === "on";
    this._run(key, () => this._hass.callService("switch", on ? "turn_off" : "turn_on", { entity_id: id }));
  }

  _press(key) {
    const id = this._map[key];
    if (id) this._run(key, () => this._hass.callService("button", "press", { entity_id: id }));
  }

  _more(key) {
    const id = this._map[key];
    if (id) this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: id }, bubbles: true, composed: true }));
  }
}

const STYLE = `
  :host {
    --sc-cold: #3b82c4; --sc-warm: #e0a020; --sc-hot: #d9662b; --sc-used: #8a8f98;
    --sc-ok: var(--success-color, #2e9d5b); --sc-error: var(--error-color, #d64545); --sc-warn: var(--warning-color, #e0a020);
  }
  ha-card { padding: 16px; overflow: hidden; }
  .empty { color: var(--secondary-text-color); }
  .header { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
  .title { font-size: 1.15rem; font-weight: 600; color: var(--primary-text-color); }
  .pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-size: .8rem; white-space: nowrap;
          background: color-mix(in srgb, var(--secondary-text-color) 14%, transparent); color: var(--secondary-text-color); }
  .pill .dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
  .pill.ok { background: color-mix(in srgb, var(--sc-ok) 14%, transparent); color: var(--sc-ok); }
  .pill.error { background: color-mix(in srgb, var(--sc-error) 14%, transparent); color: var(--sc-error); }
  .banner { display: flex; align-items: center; gap: 8px; margin-top: 10px; padding: 8px 10px; border-radius: 10px; font-size: .85rem; }
  .banner svg { flex: none; }
  .banner.error { background: color-mix(in srgb, var(--sc-error) 12%, transparent); color: var(--sc-error); }
  .banner.warn { background: color-mix(in srgb, var(--sc-warn) 14%, transparent); color: var(--primary-text-color); }
  .banner.warn svg { color: var(--sc-warn); }
  .banner .link { margin-left: auto; border: 0; background: transparent; color: var(--primary-color); font: inherit; font-weight: 600; cursor: pointer; }
  .diagram { width: 100%; height: auto; display: block; margin: 8px 0 4px; cursor: pointer; }
  .side { font-size: 10px; fill: var(--secondary-text-color); letter-spacing: .08em; text-transform: uppercase; }
  .duct { fill: none; stroke-width: 16; stroke-linecap: round; opacity: .18; }
  .duct.cold { stroke: var(--sc-cold); } .duct.warm { stroke: var(--sc-warm); } .duct.hot { stroke: var(--sc-hot); } .duct.used { stroke: var(--sc-used); }
  .air { fill: none; stroke-width: 4; stroke-linecap: round; stroke-dasharray: 2 12; opacity: .9; }
  .air.cold { stroke: var(--sc-cold); } .air.warm { stroke: var(--sc-warm); } .air.hot { stroke: var(--sc-hot); } .air.used { stroke: var(--sc-used); }
  .air.flowing { animation: flow linear infinite; }
  .arrow { fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
  .arrow.warm { stroke: var(--sc-warm); } .arrow.used { stroke: var(--sc-used); }
  .inner { fill: none; stroke-width: 10; stroke-linecap: round; opacity: .14; }
  .inner.cold { stroke: var(--sc-cold); } .inner.warm { stroke: var(--sc-warm); } .inner.hot { stroke: var(--sc-hot); } .inner.used { stroke: var(--sc-used); }
  .plate-body { fill: var(--card-background-color, #fff); stroke: var(--secondary-text-color); stroke-width: 1.5; }
  .plate-line { stroke-width: 1.4; opacity: .7; }
  .plate-line.cold { stroke: var(--sc-cold); } .plate-line.warm { stroke: var(--sc-hot); }
  .plates.defrost .plate-body { stroke: var(--sc-cold); stroke-width: 2.5; }
  .bypass-channel { fill: none; stroke: var(--secondary-text-color); stroke-width: 12; stroke-linecap: round; opacity: .08; }
  .damper { stroke: var(--primary-text-color); stroke-width: 3; stroke-linecap: round; }
  .damper-pivot { fill: var(--primary-text-color); }
  .bypass-label { font-size: 10px; font-weight: 600; fill: var(--primary-text-color); }
  .coil rect { fill: var(--card-background-color, #fff); stroke: var(--secondary-text-color); stroke-width: 1.2; }
  .coil .fins line { stroke: var(--secondary-text-color); stroke-width: 1.2; }
  .coil.heat rect { stroke: var(--sc-error); fill: color-mix(in srgb, var(--sc-error) 14%, var(--card-background-color, #fff)); }
  .coil.heat .fins line { stroke: var(--sc-error); }
  .coil.cool rect { stroke: var(--sc-cold); fill: color-mix(in srgb, var(--sc-cold) 14%, var(--card-background-color, #fff)); }
  .coil.cool .fins line { stroke: var(--sc-cold); }
  .coil-label { font-size: 8px; fill: var(--secondary-text-color); }
  .coil-value { font-size: 9px; font-weight: 600; fill: var(--primary-text-color); }
  .unit { fill: var(--secondary-background-color, #f2f3f5); stroke: var(--divider-color, #d0d0d0); stroke-width: 1.5; }
  .split { stroke: var(--divider-color, #d0d0d0); stroke-dasharray: 4 4; }
  .rotor-ring { fill: var(--card-background-color, #fff); stroke: var(--secondary-text-color); stroke-width: 2; }
  .rotor-spoke { stroke: var(--secondary-text-color); stroke-width: 1.2; opacity: .55; }
  .rotor-hub { fill: var(--secondary-text-color); }
  .rotor, .fan-icon { transform-box: view-box; transform-origin: 0 0; }
  .rotor.spinning { animation: spin 4s linear infinite; }
  .rotor.defrost .rotor-ring { stroke: var(--sc-cold); }
  .fan-icon { color: var(--secondary-text-color); }
  .fan-icon.spinning { animation: spin linear infinite; }
  .tag-label { font-size: 10px; fill: var(--secondary-text-color); }
  .tag-value { font-size: 15px; font-weight: 600; fill: var(--primary-text-color); font-variant-numeric: tabular-nums; }
  .tag.cold .tag-label { fill: var(--sc-cold); } .tag.warm .tag-label { fill: var(--sc-warm); }
  .tag.hot .tag-label { fill: var(--sc-hot); } .tag.used .tag-label { fill: var(--sc-used); }
  @keyframes flow { to { stroke-dashoffset: -28; } }
  @keyframes spin { to { transform: rotate(360deg); } }
  @media (prefers-reduced-motion: reduce) { .air, .rotor, .fan-icon { animation: none !important; } }
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 4px 0 12px; }
  .stats > div { display: flex; flex-direction: column; }
  .stat-label { font-size: .75rem; color: var(--secondary-text-color); }
  .stat-value { font-size: 1rem; font-weight: 600; color: var(--primary-text-color); font-variant-numeric: tabular-nums; }
  .modes { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; padding: 3px; border-radius: 12px; background: var(--secondary-background-color, rgba(0,0,0,.05)); }
  .mode { border: 0; border-radius: 9px; padding: 9px 4px; font: inherit; font-size: .85rem; background: transparent; color: var(--secondary-text-color); cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .mode:disabled { cursor: default; }
  .mode.active { background: var(--card-background-color, #fff); color: var(--primary-text-color); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.15); }
  .mode.active.boost { color: var(--sc-hot); } .mode.active.away, .mode.active.travelling { color: var(--sc-cold); } .mode.active.home { color: var(--sc-ok); }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
  .chip { display: flex; flex-direction: column; padding: 6px 10px; border-radius: 10px; background: var(--secondary-background-color, rgba(0,0,0,.04)); min-width: 64px; }
  .chip-label { font-size: .72rem; color: var(--secondary-text-color); }
  .chip-value { font-size: .95rem; font-weight: 600; color: var(--primary-text-color); font-variant-numeric: tabular-nums; }
  .chip.good .chip-value { color: var(--sc-ok); } .chip.fair .chip-value { color: var(--sc-warn); } .chip.poor .chip-value { color: var(--sc-error); }
  .footer { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 12px; font-size: .8rem; }
  .toggle { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; border: 1px solid var(--divider-color, #ddd);
            background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
  .toggle.on { background: color-mix(in srgb, var(--sc-hot) 14%, transparent); border-color: color-mix(in srgb, var(--sc-hot) 40%, transparent); color: var(--sc-hot); }
  .badge { display: inline-flex; align-items: center; gap: 4px; color: var(--sc-cold); }
  .muted { color: var(--secondary-text-color); margin-left: auto; }
  @media (max-width: 420px) { .mode { font-size: .75rem; } .stat-value { font-size: .9rem; } }
`;

if (!customElements.get("swegon-casa-card")) {
  customElements.define("swegon-casa-card", SwegonCasaCard);
  window.customCards = window.customCards || [];
  window.customCards.push({ type: "swegon-casa-card", name: "Swegon CASA", description: "Schéma, températures, modes et qualité d'air de la centrale Swegon CASA.", preview: true });
  console.info(`%c SWEGON-CASA-CARD %c ${CARD_VERSION} `, "background:#3b82c4;color:#fff", "");
}
