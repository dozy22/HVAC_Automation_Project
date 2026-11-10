/* ==========================================================================
   HVAC Design Studio — interface logic
   ========================================================================== */
(function () {
  'use strict';

  var H = window.HVAC;
  if (!H) {
    var failedEn = document.documentElement.dataset.lang === 'en';
    document.body.innerHTML = '<main style="padding:40px;font-family:sans-serif"><h1>' +
      (failedEn ? 'Could not load the engine' : 'تعذر تحميل المحرك') + '</h1><p>' +
      (failedEn ? 'Make sure web/engine.js sits next to the page.' : 'تأكد من وجود ملف web/engine.js بجانب الصفحة.') +
      '</p></main>';
    return;
  }

  var $ = function (id) { return document.getElementById(id); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ================================================================== */
  /* Language and plain-language help                                   */
  /* ================================================================== */
  var I18N = window.HVAC_I18N || { ar: {}, en: {} };
  var HELP = window.HVAC_HELP || { ar: {}, en: {} };
  var DATA = window.HVAC_DATA || { systems: {}, components: {}, presets: {}, errors: {} };
  var LANG = document.documentElement.dataset.lang === 'en' ? 'en' : 'ar';

  function t(key, vars) {
    var table = I18N[LANG] || I18N.ar || {};
    var s = table[key];
    if (s == null) s = (I18N.ar && I18N.ar[key]);
    if (s == null) s = key;
    if (vars) {
      Object.keys(vars).forEach(function (k) {
        s = s.split('{' + k + '}').join(String(vars[k]));
      });
    }
    return s;
  }
  function L(ar, en) {
    if (LANG === 'en') return en == null ? ar : en;
    return ar == null ? en : ar;
  }
  function hasHelp(key) { return !!(key && ((HELP.ar && HELP.ar[key]) || (HELP.en && HELP.en[key]))); }
  function helpText(key) {
    var h = HELP[LANG] || {};
    return h[key] || (HELP.en && HELP.en[key]) || '';
  }
  function presetLabel(key, obj) {
    if (LANG === 'ar') return (obj && obj.ar) || key;
    var en = DATA.presets && DATA.presets[key];
    return (en && en.en) || key;
  }
  function systemName(rec) {
    if (!rec) return '';
    return LANG === 'en' ? (rec.nameEn || rec.name) : rec.name;
  }
  function systemFamily(rec) {
    if (!rec) return '';
    var en = DATA.systems && DATA.systems[rec.key];
    return LANG === 'en' ? ((en && en.en.family) || rec.family) : rec.family;
  }
  function systemNote(rec) {
    if (!rec) return '';
    var en = DATA.systems && DATA.systems[rec.key];
    return LANG === 'en' ? ((en && en.en.note) || rec.note) : rec.note;
  }
  function cityLabel(city, key) {
    if (!city) return key || '';
    return LANG === 'en' ? (key || city.ar) : city.ar;
  }
  function errText(err) {
    var msg = (err && err.message) ? err.message : String(err);
    var key = DATA.errors && DATA.errors[msg];
    return key ? t(key) : msg;
  }
  function componentName(name) {
    var c = DATA.components && DATA.components[name];
    return c ? L(c.ar, c.en) : name;
  }
  function basisText(text) {
    if (LANG !== 'ar' || !text) return text;
    return String(text)
      .replace('Sol-air', 'هواء شمسي')
      .replace('Connected equipment', 'أجهزة موصولة')
      .replace('per person', 'لكل شخص')
      .replace('people', 'أشخاص')
      .replace('shading', 'تظليل')
      .replace(' net ', ' صافي ')
      .replace('roof', 'سقف');
  }

  function applyStaticI18n() {
    $$('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      var val = I18N[LANG] && I18N[LANG][key];
      if (val == null) return;
      var buttons = $$('.help-btn', el);
      el.textContent = val;
      buttons.forEach(function (b) { el.appendChild(b); });
    });
    $$('[data-i18n-html]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-html');
      var val = I18N[LANG] && I18N[LANG][key];
      if (val != null) el.innerHTML = val;
    });
    $$('[data-i18n-aria]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-aria');
      var val = I18N[LANG] && I18N[LANG][key];
      if (val != null) el.setAttribute('aria-label', val);
    });
    $$('[data-i18n-title]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-title');
      var val = I18N[LANG] && I18N[LANG][key];
      if (val != null) el.setAttribute('title', val);
    });
    var close = $('help-pop-close');
    if (close) close.setAttribute('aria-label', t('a11y.close'));
  }

  function updateLangButton() {
    var btn = $('lang-btn');
    var label = $('lang-label');
    if (label) label.textContent = LANG === 'ar' ? 'EN' : 'ع';
    if (btn) {
      btn.setAttribute('title', t('d.langSwitch'));
      btn.setAttribute('aria-label', t('a11y.lang'));
    }
  }

  function setLang(lang, persist) {
    LANG = (lang === 'en') ? 'en' : 'ar';
    var root = document.documentElement;
    root.lang = LANG;
    root.dir = LANG === 'ar' ? 'rtl' : 'ltr';
    root.dataset.lang = LANG;
    document.title = t('meta.title');
    var meta = document.querySelector('meta[name="description"]');
    if (meta) meta.setAttribute('content', t('meta.desc'));
    if (persist !== false) {
      try { localStorage.setItem('hvac-lang', LANG); } catch (e) {}
    }
    applyStaticI18n();
    updateLangButton();
    refillAllSelects();
    try {
      recalcQuick();
      recalcLoads();
      recalcAhu();
      recalcCycle();
      recalcControl();
    } catch (e) {}
    closeHelp();
  }

  function initLang() {
    applyStaticI18n();
    updateLangButton();
    var btn = $('lang-btn');
    if (!btn) return;
    btn.addEventListener('click', function () {
      setLang(LANG === 'ar' ? 'en' : 'ar', true);
    });
  }

  function refillAllSelects() {
    fillQuickSelects();
    fillLoadSelects();
    fillAhuSelects();
    fillControlWeather();
  }

  function fmt(x, d) {
    var n = Number(x);
    if (!Number.isFinite(n)) return '—';
    return n.toFixed(d == null ? 1 : d);
  }
  function fmt0(x) {
    var n = Number(x);
    if (!Number.isFinite(n)) return '—';
    return Math.round(n).toLocaleString('en-US');
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(id, fallback) {
    var v = parseFloat($(id).value);
    return Number.isFinite(v) ? v : (fallback == null ? 0 : fallback);
  }
  function setText(id, value) { var el = $(id); if (el) el.textContent = value; }
  function setHTML(id, value) { var el = $(id); if (el) el.innerHTML = value; }
  function setStatus(id, text, isError) {
    var el = $(id);
    if (!el) return;
    el.textContent = text;
    el.classList.toggle('is-error', !!isError);
  }
  function nowClock() {
    var d = new Date();
    function p(n) { return ('0' + n).slice(-2); }
    return p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
  }
  function debounce(fn, ms) {
    var timer;
    return function () {
      var args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(null, args); }, ms);
    };
  }
  function fillSelect(id, items, selected) {
    var el = $(id);
    if (!el) return;
    el.innerHTML = items.map(function (item) {
      return '<option value="' + esc(item[0]) + '">' + esc(item[1]) + '</option>';
    }).join('');
    if (selected != null && items.some(function (i) { return i[0] === selected; })) {
      el.value = selected;
    }
  }
  function selectOptions(obj, labelFn) {
    return Object.keys(obj).map(function (key) { return [key, labelFn(obj[key], key)]; });
  }
  function nearestOption(obj, field, value) {
    var best = null, bestDiff = Infinity;
    Object.keys(obj).forEach(function (key) {
      var diff = Math.abs(Number(obj[key][field]) - value);
      if (diff < bestDiff) { bestDiff = diff; best = key; }
    });
    return best;
  }

  /* Engine tables carry Arabic labels; the English key doubles as its label. */
  function tableLabel(obj, key, suffix) {
    var label = LANG === 'en' ? key : ((obj[key] && obj[key].ar) || key);
    if (suffix) label += ' (' + suffix + ')';
    return label;
  }

  function fillQuickSelects() {
    var space = $('q-space'), city = $('q-city'), env = $('q-envelope');
    fillSelect('q-space', Object.keys(H.SPACE_TYPES).map(function (k) {
      return [k, tableLabel(H.SPACE_TYPES, k)];
    }), (space && space.value) || 'Office');
    fillSelect('q-city', Object.keys(H.CITIES).map(function (k) {
      return [k, tableLabel(H.CITIES, k)];
    }), (city && city.value) || 'Baghdad');
    fillSelect('q-envelope', Object.keys(H.ENVELOPE_QUALITY).map(function (k) {
      return [k, tableLabel(H.ENVELOPE_QUALITY, k)];
    }), (env && env.value) || 'Standard');
  }

  function fillLoadSelects() {
    fillSelect('l-wall', Object.keys(H.WALL_OPTIONS).map(function (k) {
      return [k, tableLabel(H.WALL_OPTIONS, k, 'U ' + H.WALL_OPTIONS[k].u)];
    }), ($('l-wall') && $('l-wall').value) || 'Brick + 50 mm insulation');
    fillSelect('l-roof', Object.keys(H.ROOF_OPTIONS).map(function (k) {
      return [k, tableLabel(H.ROOF_OPTIONS, k, 'U ' + H.ROOF_OPTIONS[k].u)];
    }), ($('l-roof') && $('l-roof').value) || 'Concrete + 75 mm insulation');
    fillSelect('l-glazing', Object.keys(H.GLAZING_OPTIONS).map(function (k) {
      return [k, tableLabel(H.GLAZING_OPTIONS, k, 'U ' + H.GLAZING_OPTIONS[k].u)];
    }), ($('l-glazing') && $('l-glazing').value) || 'Double low-e glass');
    fillSelect('l-weather', Object.keys(H.WEATHER_PRESETS).map(function (k) {
      return [k, presetLabel(k, H.WEATHER_PRESETS[k])];
    }), ($('l-weather') && $('l-weather').value) || 'Hot dry example');
    fillSelect('l-solar', Object.keys(H.WALL_SOLAR_OPTIONS).map(function (k) {
      return [k, tableLabel(H.WALL_SOLAR_OPTIONS, k)];
    }), ($('l-solar') && $('l-solar').value) || 'West facade (afternoon peak)');
    fillSelect('l-activity', Object.keys(H.ACTIVITY_PROFILES).map(function (k) {
      var p = H.ACTIVITY_PROFILES[k];
      return [k, tableLabel(H.ACTIVITY_PROFILES, k) + ' · ' + p.sensible_w + '/' + p.latent_w + ' W'];
    }), ($('l-activity') && $('l-activity').value) || 'Office work');
  }

  function fillAhuSelects() {
    fillSelect('a-outpreset', Object.keys(H.WEATHER_PRESETS).map(function (k) {
      return [k, presetLabel(k, H.WEATHER_PRESETS[k])];
    }), ($('a-outpreset') && $('a-outpreset').value) || 'Hot dry example');
  }

  function fillControlWeather() {
    fillSelect('k-weather', Object.keys(WEATHERS).map(function (k) {
      return [k, LANG === 'en' ? k : WEATHERS[k].ar];
    }), ($('k-weather') && $('k-weather').value) || 'Hot afternoon');
  }

  var state = {
    quick: null,
    load: null,
    loadFromQuick: false,
    ahu: null,
    cycle: null,
    sim: null
  };

  /* ================================================================== */
  /* Theme, navigation, toast                                          */
  /* ================================================================== */
  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('hvac-theme', theme); } catch (e) {}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'light' ? '#f1f5fa' : '#060e1a');
  }
  function initTheme() {
    var btn = $('theme-btn');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
      applyTheme(next);
    });
  }

  var PAGE_IDS = ['overview', 'quick', 'loads', 'ahu', 'cycle', 'control'];
  function route() {
    var id = (location.hash || '#overview').replace('#', '');
    if (PAGE_IDS.indexOf(id) === -1) id = 'overview';
    $$('.page').forEach(function (page) {
      page.classList.toggle('active', page.id === 'page-' + id);
    });
    $$('[data-nav]').forEach(function (link) {
      link.classList.toggle('active', link.getAttribute('data-nav') === id);
      if (link.getAttribute('data-nav') === id) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    window.scrollTo({ top: 0, behavior: 'auto' });
  }
  function go(page) {
    if (location.hash === '#' + page) route();
    else location.hash = page;
  }

  var toastTimer;
  function toast(message) {
    var el = $('toast');
    if (!el) return;
    el.textContent = message;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, 2600);
  }

  /* ================================================================== */
  /* SVG helpers                                                       */
  /* ================================================================== */
  function pathFrom(points) {
    return points.map(function (p, i) {
      return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    }).join(' ');
  }
  function svgWrap(w, h, inner, label) {
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" role="img" aria-label="' + esc(label) + '">' + inner + '</svg>';
  }
  function chartGrid(sx, sy, xTicks, yTicks, x0, x1, y0, y1) {
    var out = '';
    yTicks.forEach(function (t) {
      var y = sy(t);
      out += '<line class="grid-line" x1="' + x0 + '" y1="' + y.toFixed(1) + '" x2="' + x1 + '" y2="' + y.toFixed(1) + '"/>';
      out += '<text x="' + (x0 - 7) + '" y="' + (y + 3.2).toFixed(1) + '" text-anchor="end">' + fmt(t, Math.abs(t) < 10 ? 1 : 0) + '</text>';
    });
    xTicks.forEach(function (t) {
      var x = sx(t);
      out += '<line class="grid-line" x1="' + x.toFixed(1) + '" y1="' + y0 + '" x2="' + x.toFixed(1) + '" y2="' + y1 + '"/>';
    });
    return out;
  }

  /* ================================================================== */
  /* Quick design                                                      */
  /* ================================================================== */
  function initQuick() {
    fillQuickSelects();

    var pairs = [
      ['q-area', 'q-area-range'],
      ['q-glazing', 'q-glazing-range'],
      ['q-margin', 'q-margin-range']
    ];
    pairs.forEach(function (pair) {
      var number = $(pair[0]), range = $(pair[1]);
      if (!number || !range) return;
      range.addEventListener('input', function () {
        number.value = range.value;
        scheduleQuick();
      });
      number.addEventListener('input', function () {
        var v = Math.min(parseFloat(range.max), Math.max(parseFloat(range.min), parseFloat(number.value) || 0));
        range.value = v;
        scheduleQuick();
      });
    });

    $('q-manual').addEventListener('change', function () {
      $('q-occ').disabled = !this.checked;
      if (!this.checked) {
        var space = H.SPACE_TYPES[$('q-space').value];
        $('q-occ').value = Math.max(1, Math.round(num('q-area') / space.areaPerPerson));
      }
      recalcQuick();
    });

    $('q-city').addEventListener('change', function () {
      $('q-custom-wrap').classList.toggle('show', this.value === 'Other / custom');
      recalcQuick();
    });

    $('quick-form').addEventListener('input', scheduleQuick);
    $('quick-form').addEventListener('change', scheduleQuick);

    $('q-to-loads').addEventListener('click', transferQuickToLoads);
    $('q-to-cycle').addEventListener('click', function () {
      if (!state.quick) return;
      transferLoadToCycle(state.quick.load.designTotal, t('d.toast.quickCycle'));
    });

    recalcQuick();
  }

  var scheduleQuick = debounce(recalcQuick, 55);

  function readQuick() {
    var space = $('q-space').value;
    return {
      spaceType: space,
      floorArea: num('q-area', 96),
      city: $('q-city').value,
      glazing: num('q-glazing', 25) / 100,
      orientation: (document.querySelector('input[name="q-orient"]:checked') || {}).value || 'West',
      envelope: $('q-envelope').value,
      occupants: $('q-manual').checked ? Math.max(0, Math.round(num('q-occ'))) : null,
      indoorDb: num('q-indb', 24),
      indoorRh: num('q-inrh', 50),
      customDb: num('q-custom-db', 43),
      customWb: num('q-custom-wb', 23),
      systemPreference: $('q-system').value,
      margin: num('q-margin', 12) / 100
    };
  }

  function recalcQuick() {
    var t0 = performance.now();
    var inp = readQuick();
    var space = H.SPACE_TYPES[inp.spaceType];
    var autoOcc = Math.max(1, Math.round(inp.floorArea / space.areaPerPerson));
    if (!$('q-manual').checked) $('q-occ').value = autoOcc;
    $('q-occ-hint').textContent = $('q-manual').checked
      ? t('d.occ.manual')
      : t('d.occ.auto', { n: autoOcc });
    $('q-custom-wrap').classList.toggle('show', inp.city === 'Other / custom');
    $('q-area-range').value = Math.min(1000, Math.max(10, inp.floorArea));
    $('q-glazing-range').value = num('q-glazing', 25);
    $('q-margin-range').value = num('q-margin', 12);

    var d;
    try {
      d = H.buildQuick(inp);
    } catch (err) {
      setStatus('q-status', t('d.status.error', { msg: errText(err) }), true);
      return;
    }
    state.quick = d;
    var rec = d.rec;

    setText('q-system-name', systemName(rec));
    setText('q-family', systemFamily(rec));
    setText('q-note', systemNote(rec));
    setText('q-cap', fmt(rec.capacityKw, 1));
    setText('q-cap-tr', fmt(rec.capacityTr, 2));
    setText('q-load', fmt(d.load.designTotal, 1) + ' kW');
    setText('q-target', fmt(rec.targetKw, 1) + ' kW');
    setText('q-cap-label', fmt(rec.capacityKw, 1) + ' kW');
    setText('q-margin-out', fmt(rec.marginPct, 1) + '%');
    setText('q-cop', fmt(rec.cop, 2));
    setText('q-out-units', fmt0(rec.outdoorUnits));
    setText('q-unit-size', fmt(rec.unitSizeKw, 1));
    setText('q-in-units', fmt0(rec.indoorUnits));
    setText('q-air', fmt0(rec.airflow));
    setText('q-fresh', fmt0(rec.freshAir));
    setText('q-occ-count', fmt0(d.occupants));
    setText('q-outdb', fmt(d.outDb, 0));
    setText('q-city-label', cityLabel(d.city, d.inputs.city));
    setText('q-time', fmt(performance.now() - t0, 1) + ' ms');

    var denom = Math.max(rec.capacityKw, rec.targetKw, d.load.designTotal, 1e-6);
    $('q-bar-load').style.width = Math.max(2, d.load.designTotal / denom * 100).toFixed(1) + '%';
    $('q-bar-target').style.width = Math.max(2, rec.targetKw / denom * 100).toFixed(1) + '%';
    $('q-bar-cap').style.width = '100%';

    setHTML('q-reasons', d.reasons.map(function (r) { return '<li>' + esc(reasonText(r)) + '</li>'; }).join(''));
    setHTML('q-cautions', d.cautions.map(function (c) { return '<li>' + esc(cautionText(c)) + '</li>'; }).join(''));
    setHTML('q-day-chart', renderDayChart(d.outDb, d.dailySwing));
    setStatus('q-status', t('d.status.calc', { time: nowClock() }));
    updateOverview();
  }

  function reasonText(r) {
    var q = fmt(r.q, 1), tr = fmt(r.tr, 2), pct = fmt(r.pct, 0);
    switch (r.code) {
      case 'peak':
        return t('d.reason.peak', { q: q, tr: tr, margin: fmt(r.margin, 0) });
      case 'system-split':
        return t('d.reason.split');
      case 'system-ducted':
        return t('d.reason.ducted');
      case 'system-vrf':
        return t('d.reason.vrf');
      case 'system-chiller':
        return t('d.reason.chiller');
      case 'latent-high':
        return t('d.reason.latentHigh', { pct: pct });
      case 'latent-low':
        return t('d.reason.latentLow', { pct: pct });
      case 'wwr':
        return t('d.reason.wwr', { pct: pct });
      case 'west':
        return t('d.reason.west');
      default:
        return '';
    }
  }
  function cautionText(c) {
    switch (c.code) {
      case 'fresh':
        return t('d.caution.fresh', { oa: fmt0(c.oa) });
      case 'condenser':
        return t('d.caution.condenser');
      default:
        return t('d.disclaimer');
    }
  }

  function updateOverview() {
    if (!state.quick) return;
    var d = state.quick;
    setText('ov-load', fmt(d.load.designTotal, 1));
    setText('ov-tr', fmt(d.load.designTr, 2));
    setText('ov-system', systemName(d.rec));
    setText('ov-cap', fmt(d.rec.capacityKw, 0));
    setText('ov-area', fmt0(d.inputs.floorArea));
    setText('ov-cop', fmt(state.cycle ? state.cycle.cop : 3.98, 2));
    setText('ov-tag-city', cityLabel(d.city, d.inputs.city));
    var orientKey = d.inputs.orientation;
    var orientAr = { North: 'شمالية', East: 'شرقية', South: 'جنوبية', West: 'غربية' };
    setText('ov-tag-orient', LANG === 'en'
      ? orientKey + ' facade'
      : 'واجهة ' + (orientAr[orientKey] || ''));
    setText('ov-tag-glazing', LANG === 'en'
      ? 'Glazing ' + fmt(d.inputs.glazing * 100, 0) + '%'
      : 'زجاج \u200E' + fmt(d.inputs.glazing * 100, 0) + '%');
  }

  function renderDayChart(peakDb, swing) {
    var W = 560, H = 150, ml = 36, mr = 12, mt = 14, mb = 22;
    var lo = peakDb - Math.max(2, swing) - 1;
    var hi = peakDb + 1;
    var sx = function (h) { return ml + h / 24 * (W - ml - mr); };
    var sy = function (t) { return mt + (hi - t) / (hi - lo) * (H - mt - mb); };
    var pts = [];
    for (var h = 0; h <= 24; h += 0.5) {
      var temp = peakDb - swing / 2 + swing / 2 * Math.cos(2 * Math.PI * (h - 15) / 24);
      pts.push([sx(h), sy(temp)]);
    }
    var area = pathFrom(pts) + ' L' + sx(24) + ' ' + sy(lo) + ' L' + sx(0) + ' ' + sy(lo) + ' Z';
    var inner = '<defs><linearGradient id="dayGrad" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0%" stop-color="#2dd4bf" stop-opacity="0.32"/>' +
      '<stop offset="100%" stop-color="#2dd4bf" stop-opacity="0"/></linearGradient></defs>';
    inner += chartGrid(sx, sy, [0, 6, 12, 18, 24], [lo + 2, peakDb - 2, peakDb], 0, 0, 0, 0)
      .replace(/<line class="grid-line" x1="0"/g, '<line class="grid-line" x1="' + ml + '"')
      .replace(/x2="0"/g, 'x2="' + (W - mr) + '"');
    inner += '<path d="' + area + '" fill="url(#dayGrad)"/>';
    inner += '<path class="series-line" d="' + pathFrom(pts) + '" stroke="#2dd4bf"/>';
    inner += '<line class="guide" x1="' + sx(15) + '" y1="' + mt + '" x2="' + sx(15) + '" y2="' + (H - mb) + '"/>';
    inner += '<circle cx="' + sx(15) + '" cy="' + sy(peakDb) + '" r="4" fill="#f6b74a"/>';
    inner += '<text x="' + (sx(15) - 4) + '" y="' + (sy(peakDb) - 9) + '" text-anchor="middle" fill="#f6b74a" style="font-weight:700">' + fmt(peakDb, 0) + '°</text>';
    [0, 6, 12, 18, 24].forEach(function (h) {
      inner += '<text x="' + sx(h) + '" y="' + (H - 6) + '" text-anchor="middle">' + ('0' + h).slice(-2) + ':00</text>';
    });
    inner += '<text x="' + (ml - 6) + '" y="' + (mt + 6) + '" text-anchor="end" class="axis-label">°C</text>';
    return svgWrap(W, H, inner, t('q.day.aria'));
  }

  /* ================================================================== */
  /* Detailed cooling loads                                            */
  /* ================================================================== */
  function initLoads() {
    fillLoadSelects();

    $('l-wall').addEventListener('change', function () {
      var v = H.WALL_OPTIONS[this.value];
      $('l-wall-u').value = v.u;
      $('l-wall-abs').value = v.absorptivity;
      recalcLoads();
    });
    $('l-roof').addEventListener('change', function () {
      var v = H.ROOF_OPTIONS[this.value];
      $('l-roof-u').value = v.u;
      $('l-roof-abs').value = v.absorptivity;
      recalcLoads();
    });
    $('l-glazing').addEventListener('change', function () {
      var v = H.GLAZING_OPTIONS[this.value];
      $('l-window-u').value = v.u;
      $('l-shgc').value = v.shgc;
      recalcLoads();
    });
    $('l-weather').addEventListener('change', function () {
      var v = H.WEATHER_PRESETS[this.value];
      if (v && v.db_c != null) {
        $('l-outdb').value = v.db_c;
        $('l-outwb').value = v.wb_c;
      }
      recalcLoads();
    });
    $('l-solar').addEventListener('change', function () {
      var v = H.WALL_SOLAR_OPTIONS[this.value];
      if (v) $('l-roofsolar').value = $('l-roofsolar').value;
      recalcLoads();
    });

    $('loads-form').addEventListener('input', scheduleLoads);
    $('loads-form').addEventListener('change', scheduleLoads);
    $('l-reset').addEventListener('click', function () {
      resetLoadsForm();
      recalcLoads();
      toast(t('d.toast.resetLoads'));
    });
    $('l-to-ahu').addEventListener('click', transferLoadToAhu);
    $('l-to-cycle').addEventListener('click', function () {
      if (!state.load) return;
      transferLoadToCycle(state.load.designTotal, t('d.toast.loadCycle'));
    });

    recalcLoads();
  }

  var scheduleLoads = debounce(recalcLoads, 60);

  function resetLoadsForm() {
    var d = H.defaultLoadInputs();
    $('l-length').value = d.lengthM;
    $('l-width').value = d.widthM;
    $('l-height').value = d.heightM;
    $('l-exposed').value = d.exposedWallFraction;
    $('l-wall').value = 'Brick + 50 mm insulation';
    $('l-wall-u').value = d.wallU;
    $('l-wall-abs').value = d.wallAbs;
    $('l-roof').value = 'Concrete + 75 mm insulation';
    $('l-roof-u').value = d.roofU;
    $('l-roof-abs').value = d.roofAbs;
    $('l-glazing').value = 'Double low-e glass';
    $('l-window-u').value = d.windowU;
    $('l-shgc').value = d.windowShgc;
    $('l-window').value = d.windowArea;
    $('l-shading').value = d.shading;
    $('l-weather').value = 'Hot dry example';
    $('l-outdb').value = d.outdoorDb;
    $('l-outwb').value = d.outdoorWb;
    $('l-indb').value = d.indoorDb;
    $('l-inrh').value = d.indoorRh;
    $('l-solar').value = 'West facade (afternoon peak)';
    $('l-roofsolar').value = d.roofSolar;
    $('l-occ').value = d.occupants;
    $('l-activity').value = d.activity;
    $('l-light').value = d.lightingWm2;
    $('l-equip').value = d.equipmentW;
    $('l-ach').value = d.infiltrationAch;
    $('l-vent').value = d.ventilationLsp;
    $('l-status').classList.remove('is-error');
  }

  function readLoads() {
    return {
      lengthM: num('l-length', 12),
      widthM: num('l-width', 8),
      heightM: num('l-height', 3.2),
      exposedWallFraction: num('l-exposed', 0.8),
      wallU: num('l-wall-u', 0.55),
      wallAbs: num('l-wall-abs', 0.65),
      roofU: num('l-roof-u', 0.35),
      roofAbs: num('l-roof-abs', 0.75),
      windowU: num('l-window-u', 1.6),
      windowShgc: num('l-shgc', 0.4),
      windowArea: num('l-window', 18),
      shading: num('l-shading', 0.85),
      outdoorDb: num('l-outdb', 45),
      outdoorWb: num('l-outwb', 24),
      indoorDb: num('l-indb', 24),
      indoorRh: num('l-inrh', 50),
      wallSolar: (H.WALL_SOLAR_OPTIONS[$('l-solar').value] || {}).value || 600,
      roofSolar: num('l-roofsolar', 950),
      occupants: Math.max(0, Math.round(num('l-occ', 20))),
      activity: $('l-activity').value,
      lightingWm2: num('l-light', 8),
      equipmentW: num('l-equip', 1500),
      infiltrationAch: num('l-ach', 0.5),
      ventilationLsp: num('l-vent', 10)
    };
  }

  var CAT_COLOR = {
    Envelope: 'var(--accent)',
    Solar: 'var(--amber)',
    Internal: 'var(--blue)',
    Infiltration: 'var(--violet)',
    Ventilation: 'var(--orange)'
  };

  function recalcLoads() {
    var t0 = performance.now();
    var l;
    try {
      l = H.calcLoad(readLoads());
    } catch (err) {
      setStatus('l-status', t('d.status.error', { msg: errText(err) }), true);
      return;
    }
    state.load = l;

    setText('l-head-total', fmt(l.designTotal, 2));
    setText('l-total', fmt(l.designTotal, 2));
    setText('l-tr', fmt(l.designTr, 2));
    setText('l-rshf', fmt(l.roomRshf * 100, 1));
    setText('l-room', fmt(l.roomTotal, 2));
    setText('l-room-2', fmt(l.roomTotal, 2));
    setText('l-vent', fmt(l.ventTotal, 2));
    setText('l-vent-2', fmt(l.ventTotal, 2));
    setText('l-sensible', fmt(l.designSensible, 2));
    setText('l-latent', fmt(l.designLatent, 2));
    setText('l-volume', fmt(l.volume, 1));
    setText('l-area-tag', fmt0(l.area) + ' m²');
    $('l-split-room').style.width = (l.roomTotal / l.designTotal * 100).toFixed(1) + '%';
    $('l-split-vent').style.width = (Math.max(0, l.ventTotal) / l.designTotal * 100).toFixed(1) + '%';

    renderLoadTable(l);
    setHTML('l-notes', l.notes.map(function (note) {
      return '<li>' + esc(loadNote(note)) + '</li>';
    }).join(''));

    setStatus('l-status', t('d.status.ms', { ms: fmt(performance.now() - t0, 1), time: nowClock() }));
    updateOverview();
  }

  function loadNote(note) {
    if (note.indexOf('sol-air') !== -1) return t('d.note.solair');
    if (note.indexOf('RSHF') !== -1) return t('d.note.rshf');
    if (note.indexOf('Fan power') !== -1) return t('d.note.fan');
    if (note.indexOf('Window-to-wall') !== -1) return t('d.note.wwr');
    if (note.indexOf('drier') !== -1) return t('d.note.drier');
    return note;
  }

  function renderLoadTable(l) {
    var maxQ = 1e-6;
    l.components.forEach(function (c) { maxQ = Math.max(maxQ, Math.abs(c.total)); });
    var rows = l.components.map(function (c) {
      var color = CAT_COLOR[c.category] || 'var(--accent)';
      var bar = Math.min(100, Math.abs(c.total) / maxQ * 100).toFixed(1);
      var scope = c.scope === 'Room'
        ? '<span class="scope-badge room">' + t('d.scope.room') + '</span>'
        : '<span class="scope-badge outdoor">' + t('d.scope.out') + '</span>';
      return '<tr>' +
        '<td><div class="item-cell"><strong>' + esc(componentName(c.name)) + '</strong>' +
        '<span>' + scope + '</span>' +
        '<div class="mini-bar"><i style="width:' + bar + '%;background:' + color + '"></i></div></div></td>' +
        '<td class="num">' + (c.sensible ? fmt(c.sensible, 2) : '—') + '</td>' +
        '<td class="num">' + (c.latent ? fmt(c.latent, 2) : '—') + '</td>' +
        '<td class="num">' + fmt(c.total, 2) + '</td>' +
        '<td class="col-basis muted-cell">' + esc(basisText(c.basis)) + '</td>' +
        '</tr>';
    }).join('');
    var roomS = 0, roomL = 0, ventS = 0, ventL = 0;
    l.components.forEach(function (c) {
      if (c.scope === 'Room') { roomS += c.sensible; roomL += c.latent; }
      else { ventS += c.sensible; ventL += c.latent; }
    });
    var foot = '<tr><td>' + t('d.roomTotal') + '</td><td class="num">' + fmt(roomS, 2) +
      '</td><td class="num">' + fmt(roomL, 2) + '</td><td class="num">' + fmt(roomS + roomL, 2) +
      '</td><td class="col-basis"></td></tr>' +
      '<tr><td>' + t('d.ventTotal') + '</td><td class="num">' + fmt(ventS, 2) +
      '</td><td class="num">' + fmt(ventL, 2) + '</td><td class="num">' + fmt(ventS + ventL, 2) +
      '</td><td class="col-basis"></td></tr>' +
      '<tr><td>' + t('d.designLoad') + '</td><td class="num">' + fmt(l.designSensible, 2) +
      '</td><td class="num">' + fmt(l.designLatent, 2) + '</td><td class="num">' + fmt(l.designTotal, 2) +
      '</td><td class="col-basis">' + fmt(l.designTr, 2) + ' TR</td></tr>';
    var table = $('l-components');
    table.querySelector('tbody').innerHTML = rows;
    table.querySelector('tfoot').innerHTML = foot;
  }

  function transferQuickToLoads() {
    var d = state.quick;
    if (!d) return;
    var inp = d.loadInputs;
    $('l-length').value = fmt(inp.lengthM, 2);
    $('l-width').value = fmt(inp.widthM, 2);
    $('l-height').value = fmt(inp.heightM, 2);
    $('l-exposed').value = fmt(inp.exposedWallFraction, 2);
    $('l-wall').value = nearestOption(H.WALL_OPTIONS, 'u', inp.wallU);
    $('l-wall-u').value = fmt(inp.wallU, 2);
    $('l-wall-abs').value = fmt(inp.wallAbs, 2);
    $('l-roof').value = nearestOption(H.ROOF_OPTIONS, 'u', inp.roofU);
    $('l-roof-u').value = fmt(inp.roofU, 2);
    $('l-roof-abs').value = fmt(inp.roofAbs, 2);
    $('l-glazing').value = nearestOption(H.GLAZING_OPTIONS, 'u', inp.windowU);
    $('l-window-u').value = fmt(inp.windowU, 2);
    $('l-shgc').value = fmt(inp.windowShgc, 2);
    $('l-window').value = fmt(inp.windowArea, 1);
    $('l-shading').value = fmt(inp.shading, 2);
    $('l-outdb').value = fmt(inp.outdoorDb, 1);
    $('l-outwb').value = fmt(inp.outdoorWb, 1);
    $('l-indb').value = fmt(inp.indoorDb, 1);
    $('l-inrh').value = fmt(inp.indoorRh, 0);
    $('l-solar').value = Object.keys(H.WALL_SOLAR_OPTIONS).find(function (k) {
      return Math.abs(H.WALL_SOLAR_OPTIONS[k].value - inp.wallSolar) < 1e-6;
    }) || 'West facade (afternoon peak)';
    $('l-roofsolar').value = fmt(inp.roofSolar, 0);
    $('l-occ').value = fmt0(inp.occupants);
    $('l-activity').value = inp.activity;
    $('l-light').value = fmt(inp.lightingWm2, 1);
    $('l-equip').value = fmt(inp.equipmentW, 0);
    $('l-ach').value = fmt(inp.infiltrationAch, 2);
    $('l-vent').value = fmt(inp.ventilationLsp, 1);
    recalcLoads();
    go('loads');
    toast(t('d.toast.quickLoads'));
  }

  function transferLoadToCycle(kw, message) {
    $('c-load').value = fmt(kw, 2);
    recalcCycle();
    go('cycle');
    toast(message || t('d.toast.cycleLoad'));
  }

  function transferLoadToAhu() {
    if (!state.load) return;
    var l = state.load;
    $('a-roomdb').value = fmt(l.inputs.indoorDb, 1);
    $('a-roomrh').value = fmt(l.inputs.indoorRh, 0);
    $('a-outdb').value = fmt(l.inputs.outdoorDb, 1);
    $('a-outwb').value = fmt(l.inputs.outdoorWb, 1);
    $('a-sens').value = fmt(l.roomSensible, 2);
    $('a-lat').value = fmt(l.roomLatent, 2);
    $('a-outpreset').value = 'Custom';
    recalcAhu();
    go('ahu');
    toast(t('d.toast.loadAhu'));
  }

  /* ================================================================== */
  /* AHU + psychrometric chart                                         */
  /* ================================================================== */
  function initAhu() {
    fillAhuSelects();
    var d = H.calcLoad({});
    $('a-sens').value = fmt(d.roomSensible, 2);
    $('a-lat').value = fmt(d.roomLatent, 2);

    $('a-outpreset').addEventListener('change', function () {
      var v = H.WEATHER_PRESETS[this.value];
      if (v && v.db_c != null) {
        $('a-outdb').value = v.db_c;
        $('a-outwb').value = v.wb_c;
      }
      recalcAhu();
    });
    $('ahu-form').addEventListener('input', scheduleAhu);
    $('ahu-form').addEventListener('change', scheduleAhu);
    $('a-use-load').addEventListener('click', function () {
      if (!state.load) return;
      transferLoadToAhu();
    });
    $('a-to-cycle').addEventListener('click', function () {
      if (!state.ahu) return;
      transferLoadToCycle(state.ahu.coilTotal, t('d.toast.ahuCycle'));
    });

    recalcAhu();
  }

  var scheduleAhu = debounce(recalcAhu, 60);

  function recalcAhu() {
    var t0 = performance.now();
    var room, outdoor, ahu;
    try {
      room = H.psychro.stateFromRh(num('a-roomdb', 24), num('a-roomrh', 50), H.P_ATM);
      outdoor = H.psychro.stateFromWb(num('a-outdb', 45), num('a-outwb', 24), H.P_ATM);
      ahu = H.designAHU(
        room, outdoor,
        num('a-sens', 12.8), num('a-lat', 1.2),
        num('a-supply', 13.5), num('a-oa', 25) / 100,
        H.P_ATM
      );
    } catch (err) {
      setStatus('a-status', t('d.status.error', { msg: errText(err) }), true);
      return;
    }
    state.ahu = ahu;

    setText('a-head-coil', fmt(ahu.coilTotal, 2));
    setText('a-coil', fmt(ahu.coilTotal, 2));
    setText('a-coil-s', fmt(ahu.coilSensible, 2));
    setText('a-coil-l', fmt(ahu.coilLatent, 2));
    setText('a-adp', fmt(ahu.adpDb, 2));
    setText('a-bpf', fmt(ahu.bpf, 3));
    setText('a-air', fmt0(ahu.volume * 3600));
    setText('a-shr', fmt(ahu.coilShr, 3));
    setText('a-rshf', fmt(ahu.rshf, 3));

    renderStates(ahu);
    setHTML('a-chart', renderPsychroChart(ahu));
    setStatus('a-status', t('d.status.ms', { ms: fmt(performance.now() - t0, 1), time: nowClock() }));
  }

  function stateCard(code, name, st, cls) {
    return '<div class="state-card ' + (cls || '') + '">' +
      '<div class="state-code"><strong>' + code + '</strong><span>' + esc(name) + '</span></div>' +
      '<dl>' +
      '<dt>T</dt><dd>' + fmt(st.db, 1) + '°</dd>' +
      '<dt>RH</dt><dd>' + fmt(st.rh, 0) + '%</dd>' +
      '<dt>W</dt><dd>' + fmt(st.w * 1000, 2) + '</dd>' +
      '<dt>h</dt><dd>' + fmt(st.h, 1) + '</dd>' +
      '</dl></div>';
  }

  function renderStates(a) {
    setHTML('a-states',
      stateCard('RA', t('d.state.RA'), a.room, '') +
      stateCard('OA', t('d.state.OA'), a.outdoor, 'is-oa') +
      stateCard('MA', t('d.state.MA'), a.mixed, '') +
      stateCard('SA', t('d.state.SA'), a.supply, 'is-sa') +
      stateCard('ADP', t('d.state.ADP'), a.adp, '')
    );
  }

  function renderPsychroChart(a) {
    var W = 780, H = 410, ml = 52, mr = 20, mt = 18, mb = 44;
    var states = [a.room, a.outdoor, a.mixed, a.supply, a.adp];
    var tMin = Math.min(5, Math.min.apply(null, states.map(function (s) { return s.db; })) - 3);
    var tMax = Math.max(50, Math.max.apply(null, states.map(function (s) { return s.db; })) + 3);
    var gMax = Math.max(12, Math.max.apply(null, states.map(function (s) { return s.w * 1000; })) * 1.18);
    var sx = function (t) { return ml + (t - tMin) / (tMax - tMin) * (W - ml - mr); };
    var sy = function (g) { return mt + (1 - g / gMax) * (H - mt - mb); };

    var inner = '<defs><linearGradient id="satFill" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0%" stop-color="#2dd4bf" stop-opacity="0.16"/>' +
      '<stop offset="100%" stop-color="#2dd4bf" stop-opacity="0.01"/></linearGradient></defs>';

    var xTicks = [];
    for (var tick = Math.ceil(tMin / 5) * 5; tick <= tMax; tick += 5) xTicks.push(tick);
    var yTicks = [];
    for (var g = 0; g <= gMax + 1e-9; g += 2) yTicks.push(g);
    inner += chartGrid(sx, sy, xTicks, yTicks, ml, W - mr, mt, H - mb);

    // Saturation curve and shaded two-phase region below it.
    var satPts = [];
    for (var st = tMin; st <= tMax + 1e-9; st += 0.5) {
      var w = window.HVAC.psychro.satW(st, window.HVAC.P_ATM) * 1000;
      if (w > gMax) { satPts.push([sx(st), sy(gMax)]); break; }
      satPts.push([sx(st), sy(w)]);
    }
    var satPath = pathFrom(satPts);
    inner += '<path d="' + satPath + ' L' + sx(tMax) + ' ' + sy(0) + ' L' + sx(tMin) + ' ' + sy(0) + ' Z" fill="url(#satFill)"/>';
    inner += '<path class="series-line" d="' + satPath + '" stroke="#2dd4bf" stroke-width="1.6" opacity="0.7"/>';

    // Constant-RH curves.
    [20, 40, 60, 80].forEach(function (rh) {
      var pts = [];
      for (var tt = tMin; tt <= tMax + 1e-9; tt += 0.5) {
        var ww = window.HVAC.psychro.wFromRh(tt, rh, window.HVAC.P_ATM) * 1000;
        if (ww > gMax) break;
        pts.push([sx(tt), sy(ww)]);
      }
      if (pts.length > 1) {
        inner += '<path d="' + pathFrom(pts) + '" fill="none" stroke="#8fa6bd" stroke-width="0.8" opacity="0.3" stroke-dasharray="3 4"/>';
        var last = pts[pts.length - 1];
        inner += '<text x="' + (last[0] - 2) + '" y="' + (last[1] - 4) + '" text-anchor="end" class="axis-label">' + rh + '%</text>';
      }
    });

    // Approximate comfort zone: ET* 23–26 at 30–70% RH.
    function comfortW(t, rh) { return window.HVAC.psychro.wFromRh(t, rh, window.HVAC.P_ATM) * 1000; }
    var comfort = [
      [22.2, 70], [25.2, 70], [26.8, 30], [23.8, 30]
    ].map(function (p) { return [sx(p[0]), sy(comfortW(p[0], p[1]))]; });
    inner += '<path d="' + pathFrom(comfort) + ' Z" fill="rgba(52,211,153,0.10)" stroke="rgba(52,211,153,0.55)" stroke-width="1" stroke-dasharray="4 3"/>';
    inner += '<text x="' + sx(24.5) + '" y="' + (sy(comfortW(24.5, 50)) - 6) + '" text-anchor="middle" fill="#34d399" class="axis-label">' + L('راحة', 'comfort') + '</text>';

    // Process lines.
    var ra = [sx(a.room.db), sy(a.room.w * 1000)];
    var oa = [sx(a.outdoor.db), sy(a.outdoor.w * 1000)];
    var ma = [sx(a.mixed.db), sy(a.mixed.w * 1000)];
    var sa = [sx(a.supply.db), sy(a.supply.w * 1000)];
    var adp = [sx(a.adp.db), sy(a.adp.w * 1000)];
    inner += '<line x1="' + oa[0] + '" y1="' + oa[1] + '" x2="' + ra[0] + '" y2="' + ra[1] + '" stroke="#8fa6bd" stroke-width="1" stroke-dasharray="4 4" opacity="0.55"/>';
    inner += '<line x1="' + ma[0] + '" y1="' + ma[1] + '" x2="' + sa[0] + '" y2="' + sa[1] + '" stroke="#2dd4bf" stroke-width="2.2"/>';
    inner += '<line x1="' + sa[0] + '" y1="' + sa[1] + '" x2="' + adp[0] + '" y2="' + adp[1] + '" stroke="#fb7185" stroke-width="1.4" stroke-dasharray="5 3"/>';
    inner += '<line x1="' + sa[0] + '" y1="' + sa[1] + '" x2="' + ra[0] + '" y2="' + ra[1] + '" stroke="#60a5fa" stroke-width="1.4" opacity="0.8"/>';

    function point(p, color, label, dx, dy) {
      return '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="4.2" fill="' + color + '" stroke="var(--panel)" stroke-width="1.5"/>' +
        '<text class="point-label" x="' + (p[0] + dx).toFixed(1) + '" y="' + (p[1] + dy).toFixed(1) + '" text-anchor="' + (dx < 0 ? 'end' : (dx > 0 ? 'start' : 'middle')) + '" fill="' + color + '">' + label + '</text>';
    }
    inner += point(oa, '#fb923c', 'OA', 7, -7);
    inner += point(ra, '#60a5fa', 'RA', -7, -7);
    inner += point(ma, '#a78bfa', 'MA', 7, 13);
    inner += point(sa, '#2dd4bf', 'SA', 7, 15);
    inner += point(adp, '#fb7185', 'ADP', -7, 28);

    xTicks.forEach(function (t) {
      inner += '<text x="' + sx(t) + '" y="' + (H - mb + 16) + '" text-anchor="middle" class="axis-label">' + t + '</text>';
    });
    inner += '<text x="' + (W - mr) + '" y="' + (H - 8) + '" text-anchor="end" class="axis-label">' + L('حرارة جافة °C', 'Dry-bulb °C') + '</text>';
    inner += '<text x="' + ml + '" y="' + (mt - 6) + '" text-anchor="start" class="axis-label">W (g/kg)</text>';
    return svgWrap(W, H, inner, t('a.chart.aria'));
  }

  /* ================================================================== */
  /* Refrigeration cycle                                               */
  /* ================================================================== */
  function initCycle() {
    $('cycle-form').addEventListener('input', scheduleCycle);
    $('cycle-form').addEventListener('change', scheduleCycle);
    $('c-use-load').addEventListener('click', function () {
      if (!state.load) return;
      transferLoadToCycle(state.load.designTotal, t('d.toast.cycleLoad'));
    });
    if (state.load) $('c-load').value = fmt(state.load.designTotal, 2);
    recalcCycle();
  }

  var scheduleCycle = debounce(recalcCycle, 60);

  function recalcCycle() {
    var t0 = performance.now();
    var c;
    try {
      c = H.computeCycle({
        evaporatingC: num('c-evap', 2),
        condensingC: num('c-cond', 45),
        superheatK: num('c-sh', 5),
        subcoolingK: num('c-sc', 5),
        isentropicEfficiency: num('c-eta', 0.75),
        coolingLoadKw: num('c-load', 19.16)
      });
    } catch (err) {
      setStatus('c-status', t('d.status.error', { msg: errText(err) }), true);
      return;
    }
    state.cycle = c;
    updateOverview();

    setText('c-head-cop', fmt(c.cop, 2));
    setText('c-cop', fmt(c.cop, 2));
    setText('c-carnot', fmt(c.carnotCop, 2));
    setText('c-second', fmt(c.secondLaw * 100, 1));
    setText('c-comp', fmt(c.compressorKw, 2));
    setText('c-condkw', fmt(c.condenserKw, 2));
    setText('c-mass', fmt(c.mass, 4));
    setText('c-pr', fmt(c.pressureRatio, 2));
    setText('c-discharge', fmt(c.states[1].T, 1));

    var rows = c.states.map(function (st) {
      return '<tr>' +
        '<td><strong>' + st.n + '</strong> · ' + esc(L(st.ar, st.label)) + '</td>' +
        '<td class="num">' + fmt(st.T, 1) + '</td>' +
        '<td class="num">' + fmt(st.P, 2) + '</td>' +
        '<td class="num">' + fmt(st.h, 1) + '</td>' +
        '<td class="num">' + fmt(st.s, 3) + '</td>' +
        '<td class="num">' + (st.quality == null ? '—' : fmt(st.quality, 3)) + '</td>' +
        '</tr>';
    }).join('');
    var tbody = $('c-states').querySelector('tbody');
    tbody.innerHTML = rows;

    setText('c-note', t(c.subcooled ? 'd.cycle.subcooled' : 'd.cycle.saturated', {
      x: fmt(c.states[3].quality, 3)
    }));

    setHTML('c-chart', renderCycleChart(c));
    setStatus('c-status', t('d.status.cycle', { ms: fmt(performance.now() - t0, 1), time: nowClock() }));
  }

  function renderCycleChart(c) {
    var W = 780, H = 390, ml = 50, mr = 22, mt = 18, mb = 44;
    var sat = window.R134A.sat;
    var tMin = Math.max(-40, Math.min(c.inputs.evaporatingC - 12, -8));
    var tMax = Math.min(90, Math.max(c.inputs.condensingC + 18, c.states[1].T + 8, 70));
    var sValues = [];
    sat.forEach(function (row) {
      if (row[0] >= tMin && row[0] <= tMax) { sValues.push(row[4], row[5]); }
    });
    c.states.forEach(function (st) { sValues.push(st.s); });
    var sMin = Math.min.apply(null, sValues) - 0.04;
    var sMax = Math.max.apply(null, sValues) + 0.04;
    var sx = function (s) { return ml + (s - sMin) / (sMax - sMin) * (W - ml - mr); };
    var sy = function (t) { return mt + (1 - (t - tMin) / (tMax - tMin)) * (H - mt - mb); };

    var xTicks = [];
    for (var s = Math.ceil(sMin * 10) / 10; s <= sMax; s += 0.1) xTicks.push(Math.round(s * 10) / 10);
    var yTicks = [];
    for (var temp = Math.ceil(tMin / 10) * 10; temp <= tMax; temp += 10) yTicks.push(temp);
    var inner = chartGrid(sx, sy, xTicks, yTicks, ml, W - mr, mt, H - mb);

    var left = [], right = [];
    sat.forEach(function (row) {
      if (row[0] >= tMin && row[0] <= tMax) {
        left.push([sx(row[4]), sy(row[0])]);
        right.push([sx(row[5]), sy(row[0])]);
      }
    });
    if (left.length > 1) {
      var dome = left.concat(right.slice().reverse());
      inner += '<path d="' + pathFrom(dome) + ' Z" fill="var(--line)" opacity="0.28"/>';
      inner += '<path d="' + pathFrom(left) + '" fill="none" stroke="var(--muted)" stroke-width="1.2" opacity="0.6"/>';
      inner += '<path d="' + pathFrom(right) + '" fill="none" stroke="var(--muted)" stroke-width="1.2" opacity="0.6"/>';
    }

    var cyclePts = c.states.map(function (st) { return [sx(st.s), sy(st.T)]; });
    inner += '<path d="' + pathFrom(cyclePts) + ' Z" fill="rgba(45,212,191,0.08)" stroke="#2dd4bf" stroke-width="2.2" stroke-linejoin="round"/>';

    var labels = [
      { dx: 9, dy: -8, anchor: 'start' },
      { dx: 9, dy: -8, anchor: 'start' },
      { dx: 9, dy: 14, anchor: 'start' },
      { dx: 9, dy: 14, anchor: 'start' }
    ];
    c.states.forEach(function (st, i) {
      var p = cyclePts[i], l = labels[i];
      inner += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="4.6" fill="#f6b74a" stroke="var(--panel)" stroke-width="1.8"/>';
      inner += '<text class="point-label" x="' + (p[0] + l.dx).toFixed(1) + '" y="' + (p[1] + l.dy).toFixed(1) + '" text-anchor="' + l.anchor + '" fill="#f6b74a">' + st.n + '</text>';
    });

    xTicks.forEach(function (s) {
      inner += '<text x="' + sx(s) + '" y="' + (H - mb + 16) + '" text-anchor="middle" class="axis-label">' + fmt(s, 1) + '</text>';
    });
    inner += '<text x="' + (W - mr) + '" y="' + (H - 8) + '" text-anchor="end" class="axis-label">' + L('الإنتروبيا s (kJ/kg·K)', 'Entropy s (kJ/kg·K)') + '</text>';
    inner += '<text x="' + ml + '" y="' + (mt - 5) + '" text-anchor="start" class="axis-label">T (°C)</text>';
    return svgWrap(W, H, inner, t('c.chart.aria'));
  }

  /* ================================================================== */
  /* Comfort and control                                               */
  /* ================================================================== */
  var WEATHERS = {
    'Hot afternoon': { ar: 'بعد ظهر حار', mean: 36.0, amp: 4.5, rh: 25 },
    'Peak summer': { ar: 'ذروة الصيف', mean: 39.0, amp: 4.0, rh: 22 },
    'Hot humid': { ar: 'حار رطب', mean: 34.0, amp: 3.0, rh: 55 },
    'Mild day': { ar: 'يوم معتدل', mean: 29.0, amp: 4.0, rh: 40 }
  };

  function initControl() {
    fillControlWeather();
    $('k-weather').addEventListener('change', function () {
      var w = WEATHERS[this.value];
      if (!w) return;
      $('k-outmean').value = w.mean;
      $('k-outamp').value = w.amp;
      $('k-outrh').value = w.rh;
      recalcControl();
    });
    $('k-reset').addEventListener('click', function () {
      var d = H.defaultSim();
      $('k-controller').value = d.controller;
      $('k-actuator').value = d.actuator;
      $('k-duration').value = d.durationH;
      $('k-start').value = d.startHour;
      $('k-set').value = d.setpointC;
      $('k-initial').value = d.initialDb;
      $('k-initialrh').value = d.initialRh;
      $('k-capacity').value = d.coolingCapacity;
      $('k-int-s').value = d.internalSensible;
      $('k-int-l').value = d.internalLatent;
      $('k-supplymin').value = d.supplyMin;
      $('k-supplymax').value = d.supplyMax;
      $('k-cop').value = d.cop;
      $('k-kp').value = d.kp;
      $('k-ki').value = d.ki;
      $('k-kd').value = d.kd;
      $('k-band').value = d.band;
      $('k-etmin').value = d.etMin;
      $('k-etmax').value = d.etMax;
      $('k-rhmin').value = d.rhMin;
      $('k-rhmax').value = d.rhMax;
      $('k-weather').value = 'Hot afternoon';
      $('k-outmean').value = d.outdoorMean;
      $('k-outamp').value = d.outdoorAmp;
      $('k-outrh').value = d.outdoorRh;
      recalcControl();
      toast(t('d.toast.resetSim'));
    });
    $('control-form').addEventListener('input', scheduleControl);
    $('control-form').addEventListener('change', scheduleControl);
    recalcControl();
  }

  var scheduleControl = debounce(recalcControl, 90);

  function readControl() {
    return {
      controller: $('k-controller').value,
      actuator: $('k-actuator').value,
      durationH: num('k-duration', 8),
      timestepS: 60,
      startHour: num('k-start', 8),
      setpointC: num('k-set', 24.5),
      initialDb: num('k-initial', 28.8),
      initialRh: num('k-initialrh', 55),
      outdoorMean: num('k-outmean', 36),
      outdoorAmp: num('k-outamp', 4.5),
      outdoorRh: num('k-outrh', 25),
      coolingCapacity: num('k-capacity', 10),
      internalSensible: num('k-int-s', 4.5),
      internalLatent: num('k-int-l', 0.9),
      supplyMin: num('k-supplymin', 12.5),
      supplyMax: num('k-supplymax', 22),
      cop: num('k-cop', 3.2),
      kp: num('k-kp', 22),
      ki: num('k-ki', 0.07),
      kd: num('k-kd', 25),
      band: num('k-band', 0.6),
      etMin: num('k-etmin', 23),
      etMax: num('k-etmax', 26),
      rhMin: num('k-rhmin', 30),
      rhMax: num('k-rhmax', 70)
    };
  }

  function recalcControl() {
    var t0 = performance.now();
    var both;
    try {
      both = H.simulateBoth(readControl());
    } catch (err) {
      setStatus('k-status', t('d.status.error', { msg: errText(err) }), true);
      return;
    }
    state.sim = both;
    var selected = both.pid.inputs.controller === 'Threshold' ? both.threshold : both.pid;
    if (both.pid.inputs.controller !== 'Threshold' && both.threshold.inputs.controller === 'Threshold') {
      selected = $('k-controller').value === 'Threshold' ? both.threshold : both.pid;
    }

    setText('k-head-comfort', fmt(selected.comfortLastHalfPct, 0));
    setText('k-comfort', fmt(selected.comfortLastHalfPct, 0));
    setText('k-humid', fmt(selected.humidityPct, 0));
    setText('k-delivered', fmt(selected.deliveredKwh, 1));
    setText('k-electric', fmt(selected.electricityKwh, 1));
    setText('k-switches', fmt0(selected.switches));
    setText('k-final', fmt(selected.finalDb, 2));
    setText('k-finalrh', fmt(selected.finalRh, 0));
    setText('k-finalet', fmt(selected.finalEt, 1));
    setText('k-run-tag', t('d.steps', { n: fmt0(selected.steps) }));

    setTone('k-comfort', selected.comfortLastHalfPct, 98, 85);
    setTone('k-humid', selected.humidityPct, 95, 80);

    setHTML('k-chart', renderSimChart(selected));
    setHTML('k-demand-chart', renderDemandChart(selected));
    attachSimHover(selected);

    renderCompare(both);
    setStatus('k-status', t('d.status.steps', {
      n: both.pid.steps + both.threshold.steps,
      ms: fmt(performance.now() - t0, 1),
      time: nowClock()
    }));
  }

  function setTone(id, value, good, warn) {
    var el = $(id);
    if (!el) return;
    var metric = el.closest('.metric');
    if (!metric) return;
    metric.classList.remove('is-good', 'is-warn', 'is-bad');
    if (value >= good) metric.classList.add('is-good');
    else if (value >= warn) metric.classList.add('is-warn');
    else metric.classList.add('is-bad');
  }

  function renderCompare(both) {
    var rows = [both.pid, both.threshold];
    var minElectric = Math.min(both.pid.electricityKwh, both.threshold.electricityKwh);
    var body = rows.map(function (r) {
      var name = r.inputs.controller === 'PID' ? t('d.pid') : t('d.threshold');
      var comfortCls = r.comfortLastHalfPct >= 98 ? 'good' : (r.comfortLastHalfPct >= 85 ? 'warn' : '');
      var elecCls = Math.abs(r.electricityKwh - minElectric) < 1e-9 ? 'good' : '';
      return '<tr>' +
        '<td><strong>' + name + '</strong></td>' +
        '<td class="num ' + comfortCls + '">' + fmt(r.comfortLastHalfPct, 0) + '%</td>' +
        '<td class="num">' + fmt(r.humidityPct, 0) + '%</td>' +
        '<td class="num">' + fmt(r.deliveredKwh, 1) + '</td>' +
        '<td class="num ' + elecCls + '">' + fmt(r.electricityKwh, 1) + '</td>' +
        '<td class="num">' + fmt0(r.switches) + '</td>' +
        '<td class="num">' + fmt(r.finalDb, 2) + '°</td>' +
        '</tr>';
    }).join('');
    $('k-compare').querySelector('tbody').innerHTML = body;
  }

  function renderSimChart(sim) {
    var W = 780, H = 310, ml = 46, mr = 20, mt = 16, mb = 34;
    var tMax = sim.inputs.durationH;
    var temps = Array.prototype.slice.call(sim.outdoorT).concat(Array.prototype.slice.call(sim.roomT));
    var lo = Math.min(sim.inputs.etMin - 1.5, Math.min.apply(null, temps) - 1);
    var hi = Math.max(sim.inputs.etMax + 2.5, Math.max.apply(null, temps) + 1);
    lo = Math.max(10, lo);
    hi = Math.min(48, hi);
    var sx = function (t) { return ml + t / tMax * (W - ml - mr); };
    var sy = function (t) { return mt + (1 - (t - lo) / (hi - lo)) * (H - mt - mb); };

    var xTicks = [];
    var step = tMax <= 8 ? 1 : 2;
    for (var tick = 0; tick <= tMax + 1e-9; tick += step) xTicks.push(tick);
    var yTicks = [];
    for (var y = Math.ceil(lo / 5) * 5; y <= hi; y += 5) yTicks.push(y);
    var inner = chartGrid(sx, sy, xTicks, yTicks, ml, W - mr, mt, H - mb);

    inner += '<rect x="' + ml + '" y="' + sy(sim.inputs.etMax).toFixed(1) + '" width="' + (W - ml - mr) +
      '" height="' + Math.max(0, sy(sim.inputs.etMin) - sy(sim.inputs.etMax)).toFixed(1) +
      '" fill="rgba(52,211,153,0.09)"/>';
    inner += '<line x1="' + ml + '" y1="' + sy(sim.inputs.etMin).toFixed(1) + '" x2="' + (W - mr) + '" y2="' + sy(sim.inputs.etMin).toFixed(1) + '" stroke="rgba(52,211,153,0.45)" stroke-width="1" stroke-dasharray="4 3"/>';
    inner += '<line x1="' + ml + '" y1="' + sy(sim.inputs.etMax).toFixed(1) + '" x2="' + (W - mr) + '" y2="' + sy(sim.inputs.etMax).toFixed(1) + '" stroke="rgba(52,211,153,0.45)" stroke-width="1" stroke-dasharray="4 3"/>';

    var roomPts = [], outPts = [];
    for (var i = 0; i < sim.timeH.length; i++) {
      roomPts.push([sx(sim.timeH[i]), sy(sim.roomT[i])]);
      outPts.push([sx(sim.timeH[i]), sy(sim.outdoorT[i])]);
    }
    inner += '<path class="series-line" d="' + pathFrom(outPts) + '" stroke="#f6b74a" stroke-width="1.6" stroke-dasharray="5 4"/>';
    inner += '<path class="series-line" d="' + pathFrom(roomPts) + '" stroke="#2dd4bf" stroke-width="2.5"/>';
    inner += '<line x1="' + ml + '" y1="' + sy(sim.inputs.setpointC).toFixed(1) + '" x2="' + (W - mr) + '" y2="' + sy(sim.inputs.setpointC).toFixed(1) + '" stroke="var(--muted)" stroke-width="1.2" stroke-dasharray="3 4"/>';

    xTicks.forEach(function (t) {
      var hour = Math.round(sim.inputs.startHour + t) % 24;
      inner += '<text x="' + sx(t) + '" y="' + (H - 8) + '" text-anchor="middle">' + ('0' + hour).slice(-2) + ':00</text>';
    });
    inner += '<text x="' + ml + '" y="' + (mt - 4) + '" text-anchor="start" class="axis-label">°C</text>';
    return svgWrap(W, H, inner, t('k.chart.aria'));
  }

  function attachSimHover(sim) {
    var el = $('k-chart');
    if (!el) return;
    var svg = el.querySelector('svg');
    if (!svg) return;
    el.style.position = 'relative';
    var W = 780, H = 310, ml = 46, mr = 20, mt = 16, mb = 34;
    var tMax = sim.inputs.durationH;
    var temps = Array.prototype.slice.call(sim.outdoorT).concat(Array.prototype.slice.call(sim.roomT));
    var lo = Math.min(sim.inputs.etMin - 1.5, Math.min.apply(null, temps) - 1);
    var hi = Math.max(sim.inputs.etMax + 2.5, Math.max.apply(null, temps) + 1);
    lo = Math.max(10, lo); hi = Math.min(48, hi);
    var sx = function (t) { return ml + t / tMax * (W - ml - mr); };
    var sy = function (t) { return mt + (1 - (t - lo) / (hi - lo)) * (H - mt - mb); };

    var guide = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    guide.setAttribute('class', 'guide');
    guide.setAttribute('y1', mt);
    guide.setAttribute('y2', H - mb);
    guide.style.display = 'none';
    svg.appendChild(guide);

    var tip = document.createElement('div');
    tip.className = 'chart-tooltip';
    tip.style.display = 'none';
    el.appendChild(tip);

    function hide() {
      guide.style.display = 'none';
      tip.style.display = 'none';
    }
    el.onpointermove = function (ev) {
      var rect = el.getBoundingClientRect();
      var px = (ev.clientX - rect.left) / rect.width * W;
      if (px < ml || px > W - mr) { hide(); return; }
      var t = (px - ml) / (W - ml - mr) * tMax;
      var best = 0, bestDiff = Infinity;
      for (var i = 0; i < sim.timeH.length; i++) {
        var diff = Math.abs(sim.timeH[i] - t);
        if (diff < bestDiff) { bestDiff = diff; best = i; }
      }
      var gx = sx(sim.timeH[best]);
      guide.setAttribute('x1', gx);
      guide.setAttribute('x2', gx);
      guide.style.display = '';
      var hour = Math.round(sim.inputs.startHour + sim.timeH[best]) % 24;
      tip.innerHTML = esc(t('d.tooltip', {
        time: ('0' + hour).slice(-2) + ':00',
        room: fmt(sim.roomT[best], 2),
        out: fmt(sim.outdoorT[best], 1),
        rh: fmt(sim.roomRh[best], 0)
      }));
      tip.style.display = '';
      var leftPct = gx / W * 100;
      tip.style.left = Math.min(88, Math.max(6, leftPct)) + '%';
      tip.style.top = Math.max(4, sy(sim.roomT[best]) / H * 100 - 8) + '%';
      tip.style.transform = 'translate(-50%, -100%)';
    };
    el.onpointerleave = hide;
  }

  function renderDemandChart(sim) {
    var W = 780, H = 220, ml = 46, mr = 20, mt = 14, mb = 34;
    var tMax = sim.inputs.durationH;
    var cap = sim.inputs.coolingCapacity;
    var sx = function (t) { return ml + t / tMax * (W - ml - mr); };
    var sy = function (kw) { return mt + (1 - kw / cap) * (H - mt - mb); };
    var xTicks = [];
    var step = tMax <= 8 ? 1 : 2;
    for (var tick = 0; tick <= tMax + 1e-9; tick += step) xTicks.push(tick);
    var yTicks = [0, cap * 0.25, cap * 0.5, cap * 0.75, cap];
    var inner = chartGrid(sx, sy, xTicks, yTicks, ml, W - mr, mt, H - mb);

    var base = [], top = [];
    for (var i = 0; i < sim.timeH.length; i++) {
      base.push([sx(sim.timeH[i]), sy(sim.sensible[i])]);
      top.push([sx(sim.timeH[i]), sy(sim.sensible[i] + sim.latent[i])]);
    }
    var latentArea = pathFrom(top) + ' L' + sx(tMax) + ' ' + sy(0) + ' L' + sx(0) + ' ' + sy(0) + ' Z';
    var sensibleArea = pathFrom(base) + ' L' + sx(tMax) + ' ' + sy(0) + ' L' + sx(0) + ' ' + sy(0) + ' Z';
    inner += '<path d="' + latentArea + '" fill="#60a5fa" opacity="0.32"/>';
    inner += '<path d="' + sensibleArea + '" fill="#2dd4bf" opacity="0.42"/>';

    xTicks.forEach(function (t) {
      var hour = Math.round(sim.inputs.startHour + t) % 24;
      inner += '<text x="' + sx(t) + '" y="' + (H - 8) + '" text-anchor="middle">' + ('0' + hour).slice(-2) + ':00</text>';
    });
    inner += '<text x="' + ml + '" y="' + (mt - 2) + '" text-anchor="start" class="axis-label">kW</text>';
    return svgWrap(W, H, inner, t('k.demand.aria'));
  }

  /* ================================================================== */
  /* Plain-language help popover                                       */
  /* ================================================================== */
  var helpPop = null, helpTitleEl = null, helpBodyEl = null, helpBackdrop = null;
  var helpBtn = null, helpPinned = false, helpShowTimer = 0, helpHideTimer = 0;

  function cleanText(node) {
    if (!node) return '';
    var clone = node.cloneNode(true);
    $$('.help-btn', clone).forEach(function (b) { b.remove(); });
    var pick = clone.querySelector('.lbl') ||
      clone.querySelector('h1, h2, h3, h4') ||
      clone.querySelector('.metric > span') ||
      clone.querySelector('span');
    return ((pick || clone).textContent || '').replace(/\s+/g, ' ').trim();
  }

  function makeHelpButton(key, host) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'help-btn';
    btn.setAttribute('data-help-key', key);
    btn.setAttribute('aria-label', t('a11y.help'));
    btn.setAttribute('aria-expanded', 'false');
    btn.textContent = '?';
    btn.__host = host;
    btn.addEventListener('mouseenter', function () {
      if (!window.matchMedia('(hover: hover)').matches) return;
      if (helpPinned) return;
      clearTimeout(helpHideTimer);
      clearTimeout(helpShowTimer);
      helpShowTimer = setTimeout(function () { showHelp(btn); }, 110);
    });
    btn.addEventListener('mouseleave', function () {
      if (!window.matchMedia('(hover: hover)').matches) return;
      clearTimeout(helpShowTimer);
      if (helpPinned) return;
      helpHideTimer = setTimeout(closeHelp, 180);
    });
    btn.addEventListener('focus', function () { showHelp(btn); });
    btn.addEventListener('blur', function () {
      if (!helpPinned) helpHideTimer = setTimeout(closeHelp, 150);
    });
    btn.addEventListener('click', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      if (helpBtn === btn && helpPinned) { closeHelp(); return; }
      helpPinned = true;
      showHelp(btn);
    });
    btn.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { ev.stopPropagation(); closeHelp(); }
    });
    return btn;
  }

  function placeHelpButton(host, key) {
    if (!host || host.querySelector(':scope > .help-btn')) return;
    var btn = makeHelpButton(key, host);
    if (/^H[1-6]$/.test(host.tagName)) {
      host.appendChild(btn);
      return;
    }
    if (host.classList.contains('section-head')) {
      var sh = host.querySelector('h1, h2, h3');
      (sh || host).appendChild(btn);
      return;
    }
    if (host.hasAttribute('data-help') && host.getAttribute('data-help').indexOf('s:') === 0) {
      var sspan = host.querySelector('span');
      (sspan || host).appendChild(btn);
      return;
    }
    var slot = host.querySelector('.panel-head') || host.querySelector('.result-top') ||
      host.querySelector('.status-head');
    if (slot) { slot.appendChild(btn); return; }
    host.classList.add('has-help-float');
    host.appendChild(btn);
  }

  function attachHelpToField(el, key) {
    var field = el.closest('.check-field') || el.closest('.field');
    if (!field || field.querySelector('.help-btn')) return;
    var span = el.closest('.check-field')
      ? field.querySelector('span:last-of-type')
      : field.querySelector('span');
    if (!span) return;
    span.appendChild(makeHelpButton(key, field));
  }

  function initHelp() {
    helpPop = $('help-pop');
    helpTitleEl = $('help-pop-title');
    helpBodyEl = $('help-pop-body');
    helpBackdrop = $('help-backdrop');
    if (!helpPop) return;

    $$('[data-help]').forEach(function (host) {
      var key = host.getAttribute('data-help');
      if (hasHelp(key)) placeHelpButton(host, key);
    });

    $$('.metric').forEach(function (m) {
      var strong = m.querySelector('strong[id]');
      if (!strong) return;
      var key = 'm:' + strong.id;
      if (!hasHelp(key)) return;
      var span = m.querySelector('span');
      if (span) span.appendChild(makeHelpButton(key, m));
    });

    $$('input[id], select[id], [role="radiogroup"][id]').forEach(function (el) {
      if (hasHelp(el.id)) attachHelpToField(el, el.id);
    });

    var close = $('help-pop-close');
    if (close) close.addEventListener('click', closeHelp);
    if (helpBackdrop) helpBackdrop.addEventListener('click', closeHelp);

    helpPop.addEventListener('mouseenter', function () {
      clearTimeout(helpHideTimer);
      clearTimeout(helpShowTimer);
    });
    helpPop.addEventListener('mouseleave', function () {
      if (!helpPinned) helpHideTimer = setTimeout(closeHelp, 200);
    });

    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && helpBtn) closeHelp();
    });
    document.addEventListener('pointerdown', function (ev) {
      if (!helpBtn) return;
      if (helpPop.contains(ev.target)) return;
      if (helpBtn.contains(ev.target)) return;
      closeHelp();
    }, true);
    window.addEventListener('resize', function () {
      if (helpBtn) positionHelp();
    });
    window.addEventListener('scroll', function () {
      if (helpBtn && !helpPinned) closeHelp();
    }, { passive: true });
    document.addEventListener('hashchange', closeHelp);
  }

  function showHelp(btn) {
    if (!btn || !helpPop) return;
    var key = btn.getAttribute('data-help-key');
    var text = helpText(key);
    if (!text) return;
    if (helpBtn && helpBtn !== btn) helpBtn.setAttribute('aria-expanded', 'false');
    helpBtn = btn;
    var host = btn.__host || btn.parentElement;
    var title = cleanText(host);
    helpTitleEl.textContent = title || t('d.helpTitle');
    helpBodyEl.textContent = text;
    helpPop.hidden = false;
    helpBackdrop.hidden = true;
    btn.setAttribute('aria-expanded', 'true');
    positionHelp();
  }

  function positionHelp() {
    if (!helpBtn || !helpPop) return;
    var sheet = window.matchMedia('(max-width: 640px)').matches;
    helpPop.classList.toggle('is-sheet', sheet);
    if (sheet) {
      if (helpBackdrop) helpBackdrop.hidden = false;
      helpPop.style.left = '';
      helpPop.style.top = '';
      helpPop.style.width = '';
      return;
    }
    if (helpBackdrop) helpBackdrop.hidden = true;
    var r = helpBtn.getBoundingClientRect();
    var vw = window.innerWidth, vh = window.innerHeight;
    var w = Math.min(310, vw - 24);
    helpPop.style.width = w + 'px';
    var left = r.left + r.width / 2 - w / 2;
    left = Math.max(12, Math.min(vw - w - 12, left));
    var h = helpPop.offsetHeight || 130;
    var top = r.bottom + 10;
    if (top + h > vh - 12) top = Math.max(12, r.top - h - 10);
    helpPop.style.left = Math.round(left) + 'px';
    helpPop.style.top = Math.round(top) + 'px';
  }

  function closeHelp() {
    clearTimeout(helpShowTimer);
    clearTimeout(helpHideTimer);
    helpPinned = false;
    if (helpBtn) helpBtn.setAttribute('aria-expanded', 'false');
    helpBtn = null;
    if (helpPop) helpPop.hidden = true;
    if (helpBackdrop) helpBackdrop.hidden = true;
  }

  /* ================================================================== */
  /* Boot                                                              */
  /* ================================================================== */
  function initServiceWorker() {
    if (!('serviceWorker' in navigator) || !/^https?:$/.test(location.protocol)) return;
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }

  function boot() {
    initTheme();
    initLang();
    initServiceWorker();
    window.addEventListener('hashchange', route);
    initQuick();
    initLoads();
    initAhu();
    initCycle();
    initControl();
    initHelp();
    route();

    var t0 = performance.now();
    window.__HVAC_BOOT_MS = t0;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
