/* ==========================================================================
   HVAC Design Studio — offline calculation engine
   Pure JavaScript, no dependencies. Mirrors the Python modules:
   psychrometrics, thermal_loads, ahu, refrigeration (R134a table), controls,
   quick_design.  Exposes a single global: window.HVAC
   ========================================================================== */
(function (global) {
  'use strict';

  var P_ATM = 101.325;          // kPa
  var TR_KW = 3.5168525;
  var H_FG_0 = 2501.0;          // kJ/kg
  var MW_RATIO = 0.621945;

  function clamp(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }
  function finite(x, fallback) {
    var n = Number(x);
    return Number.isFinite(n) ? n : fallback;
  }

  /* ------------------------------------------------------------------ */
  /* Psychrometrics (ASHRAE Hyland–Wexler)                              */
  /* ------------------------------------------------------------------ */
  function satP(tC) {
    var t = Number(tC);
    if (!(t > -100 && t < 200)) throw new Error('Dry-bulb out of range');
    var k = t + 273.15;
    var ln;
    if (t <= 0) {
      ln = -5.6745359e3 / k + 6.3925247
        - 9.677843e-3 * k + 6.2215701e-7 * k * k
        + 2.0747825e-9 * k * k * k - 9.484024e-13 * Math.pow(k, 4)
        + 4.1635019 * Math.log(k);
    } else {
      ln = -5.8002206e3 / k + 1.3914993
        - 4.8640239e-2 * k + 4.1764768e-5 * k * k
        - 1.4452093e-8 * k * k * k + 6.5459673 * Math.log(k);
    }
    return Math.exp(ln) / 1000.0;
  }

  function satW(tC, P) {
    P = finite(P, P_ATM);
    var pws = satP(tC);
    if (pws >= P) return Infinity;
    return MW_RATIO * pws / (P - pws);
  }

  function wFromRh(tC, rhPct, P) {
    P = finite(P, P_ATM);
    var rh = Number(rhPct);
    if (!(rh >= 0 && rh <= 100)) throw new Error('RH out of range');
    var pws = satP(tC);
    var pw = rh / 100.0 * pws;
    if (pw >= P) throw new Error('Vapour pressure exceeds total pressure');
    return MW_RATIO * pw / (P - pw);
  }

  function rhFromW(tC, w, P) {
    P = finite(P, P_ATM);
    w = Math.max(0, Number(w));
    var pw = P * w / (MW_RATIO + w);
    var pws = satP(tC);
    return clamp(100.0 * pw / pws, 0, 100);
  }

  function enthalpy(tC, w) {
    return 1.006 * tC + w * (H_FG_0 + 1.86 * tC);
  }

  function specVol(tC, w, P) {
    P = finite(P, P_ATM);
    return 0.287042 * (tC + 273.15) * (1.0 + 1.607858 * w) / P;
  }

  function moistCp(w) { return 1.006 + 1.86 * w; }

  /* Raw ASHRAE wet-bulb relation; may go negative outside its domain. */
  function wbRaw(db, wb, P) {
    wb = Math.min(wb, db);
    var wsStar = satW(wb, P);
    if (!isFinite(wsStar)) throw new Error('Wet bulb out of range');
    var num, den;
    if (wb >= 0) {
      num = (H_FG_0 - 2.326 * wb) * wsStar - 1.006 * (db - wb);
      den = H_FG_0 + 1.86 * db - 4.186 * wb;
    } else {
      num = (2830.0 - 0.24 * wb) * wsStar - 1.006 * (db - wb);
      den = 2830.0 + 1.86 * db - 2.1 * wb;
    }
    return num / den;
  }

  function wbFromRh(db, rhPct, P) {
    P = finite(P, P_ATM);
    var rh = Number(rhPct);
    if (!(rh >= 0 && rh <= 100)) throw new Error('RH out of range');
    if (rh >= 99.999) return db;
    var target = wFromRh(db, rh, P);
    var high = db;
    if (target > wbRaw(db, high, P) + 1e-9) throw new Error('Wet bulb cannot be resolved');
    var low = db - 1.0;
    var wLow = wbRaw(db, low, P);
    var guard = 0;
    while (wLow > target && low > -95 && guard++ < 200) {
      low -= 1.0;
      wLow = wbRaw(db, low, P);
    }
    if (wLow > target) throw new Error('Wet bulb cannot be resolved');
    for (var i = 0; i < 120; i++) {
      var mid = 0.5 * (low + high);
      if (wbRaw(db, mid, P) < target) low = mid; else high = mid;
      if (high - low < 1e-7) break;
    }
    return 0.5 * (low + high);
  }

  function wFromWb(db, wb, P) {
    P = finite(P, P_ATM);
    wb = Number(wb);
    if (wb > db + 0.02) throw new Error('Wet bulb above dry bulb');
    wb = Math.min(wb, db);
    var w = wbRaw(db, wb, P);
    if (w < -1e-9) throw new Error('Invalid wet bulb');
    return Math.max(0, w);
  }

  function dewPoint(db, rhPct, P) {
    P = finite(P, P_ATM);
    var rh = Number(rhPct);
    if (!(rh >= 0 && rh <= 100)) throw new Error('RH out of range');
    if (rh === 0) return -95;
    var pw = rh / 100.0 * satP(db);
    if (pw <= 1e-9) return -95;
    var low = -95.0, high = Math.min(db, 200.0);
    for (var i = 0; i < 100; i++) {
      var mid = 0.5 * (low + high);
      if (satP(mid) < pw) low = mid; else high = mid;
      if (high - low < 1e-7) break;
    }
    return 0.5 * (low + high);
  }

  function finishState(db, w, rh, wb, P) {
    var pw = P * w / (MW_RATIO + w);
    return {
      db: db, wb: wb, dp: dewPoint(db, rh, P), rh: rh,
      w: w, h: enthalpy(db, w), v: specVol(db, w, P),
      pw: pw, p: P
    };
  }

  function stateFromRh(db, rhPct, P) {
    P = finite(P, P_ATM);
    db = Number(db);
    var rh = clamp(Number(rhPct), 0.001, 100);
    var w = wFromRh(db, rh, P);
    return finishState(db, w, rh, wbFromRh(db, rh, P), P);
  }

  function stateFromW(db, w, P) {
    P = finite(P, P_ATM);
    db = Number(db); w = Number(w);
    if (w < 0) throw new Error('Negative humidity ratio');
    var wSat = satW(db, P);
    if (w > wSat + 2e-6) throw new Error('Supersaturated state');
    w = Math.min(w, wSat);
    var rh = rhFromW(db, w, P);
    return finishState(db, w, rh, wbFromRh(db, rh, P), P);
  }

  function stateFromWb(db, wb, P) {
    P = finite(P, P_ATM);
    db = Number(db);
    var w = wFromWb(db, wb, P);
    var rh = rhFromW(db, w, P);
    return finishState(db, w, rh, Math.min(wb, db), P);
  }

  function stateFromHW(h, w, P) {
    var db = (h - H_FG_0 * w) / (1.006 + 1.86 * w);
    return stateFromW(db, w, P);
  }

  function effectiveTemperature(db, rh) { return db + 0.04 * (rh - 50.0); }

  var psychro = {
    P_ATM: P_ATM,
    satP: satP,
    satW: satW,
    wFromRh: wFromRh,
    rhFromW: rhFromW,
    wFromWb: wFromWb,
    wbFromRh: wbFromRh,
    dewPoint: dewPoint,
    enthalpy: enthalpy,
    specVol: specVol,
    moistCp: moistCp,
    stateFromRh: stateFromRh,
    stateFromW: stateFromW,
    stateFromWb: stateFromWb,
    stateFromHW: stateFromHW,
    effective: effectiveTemperature
  };

  /* ------------------------------------------------------------------ */
  /* Cooling loads (ASHRAE-style steady design)                         */
  /* ------------------------------------------------------------------ */
  var ACTIVITY_PROFILES = {
    'Seated, quiet': { total_w: 105, sensible_w: 60, latent_w: 45, ar: 'جلوس هادئ' },
    'Office work': { total_w: 130, sensible_w: 75, latent_w: 55, ar: 'عمل مكتبي' },
    'Standing / light work': { total_w: 160, sensible_w: 85, latent_w: 75, ar: 'وقوف / عمل خفيف' },
    'Light bench work': { total_w: 235, sensible_w: 130, latent_w: 105, ar: 'عمل مختبري خفيف' },
    'Moderate activity': { total_w: 295, sensible_w: 170, latent_w: 125, ar: 'نشاط متوسط' },
    'Heavy work': { total_w: 440, sensible_w: 250, latent_w: 190, ar: 'عمل شاق' }
  };

  var WALL_OPTIONS = {
    'Brick wall, 200 mm, uninsulated': { u: 1.70, absorptivity: 0.65, ar: 'طابوق 200 ملم بدون عزل' },
    'Brick + 50 mm insulation': { u: 0.55, absorptivity: 0.65, ar: 'طابوق + عزل 50 ملم' },
    'Concrete + 50 mm insulation': { u: 0.48, absorptivity: 0.60, ar: 'خرسانة + عزل 50 ملم' },
    'Insulated sandwich panel': { u: 0.30, absorptivity: 0.45, ar: 'ساندويتش بانل معزول' },
    'Glazed curtain wall': { u: 2.40, absorptivity: 0.30, ar: 'واجهة زجاجية كاملة' }
  };

  var ROOF_OPTIONS = {
    'Concrete roof, 150 mm, uninsulated': { u: 1.75, absorptivity: 0.75, ar: 'خرسانة 150 ملم بدون عزل' },
    'Concrete + 50 mm insulation': { u: 0.55, absorptivity: 0.75, ar: 'خرسانة + عزل 50 ملم' },
    'Concrete + 75 mm insulation': { u: 0.35, absorptivity: 0.75, ar: 'خرسانة + عزل 75 ملم' },
    'Metal deck + insulation': { u: 0.40, absorptivity: 0.55, ar: 'سقف معدني معزول' }
  };

  var GLAZING_OPTIONS = {
    'Single clear glass': { u: 5.80, shgc: 0.86, ar: 'زجاج مفرد شفاف' },
    'Double clear glass': { u: 2.80, shgc: 0.72, ar: 'زجاج مزدوج شفاف' },
    'Double low-e glass': { u: 1.60, shgc: 0.40, ar: 'زجاج مزدوج Low-E' },
    'Triple low-e glass': { u: 0.80, shgc: 0.28, ar: 'زجاج ثلاثي Low-E' }
  };

  var WEATHER_PRESETS = {
    'Hot dry example': { db_c: 45.0, wb_c: 24.0, ar: 'حار جاف' },
    'Hot humid example': { db_c: 38.0, wb_c: 28.0, ar: 'حار رطب' },
    'Mild example': { db_c: 32.0, wb_c: 22.0, ar: 'معتدل' },
    'Custom': { ar: 'مخصص' }
  };

  var WALL_SOLAR_OPTIONS = {
    'West facade (afternoon peak)': { value: 600.0, ar: 'واجهة غربية (ذروة العصر)' },
    'South facade': { value: 420.0, ar: 'واجهة جنوبية' },
    'East facade (morning peak)': { value: 480.0, ar: 'واجهة شرقية (ذروة الصباح)' },
    'North facade': { value: 130.0, ar: 'واجهة شمالية' },
    'Custom / user value': { value: 600.0, ar: 'قيمة مخصصة' }
  };

  function defaultLoadInputs() {
    return {
      projectName: 'HVAC design studio',
      lengthM: 12.0, widthM: 8.0, heightM: 3.2, exposedWallFraction: 0.80,
      wallU: 0.55, wallAbs: 0.65, roofU: 0.35, roofAbs: 0.75,
      windowU: 1.60, windowShgc: 0.40, windowArea: 18.0, shading: 0.85,
      wallSolar: 600.0, roofSolar: 950.0, outdoorFilm: 20.0,
      outdoorDb: 45.0, outdoorWb: 24.0, indoorDb: 24.0, indoorRh: 50.0,
      pressure: P_ATM,
      occupants: 20, activity: 'Office work',
      lightingWm2: 8.0, equipmentW: 1500.0,
      infiltrationAch: 0.50, ventilationLsp: 10.0
    };
  }

  function calcLoad(raw) {
    var inp = Object.assign(defaultLoadInputs(), raw || {});
    var area = inp.lengthM * inp.widthM;
    var volume = area * inp.heightM;
    var perimeter = 2.0 * (inp.lengthM + inp.widthM);
    var grossWall = perimeter * inp.heightM * inp.exposedWallFraction;
    if (inp.windowArea > grossWall + 1e-6) throw new Error('Window area exceeds exposed wall');
    var netWall = Math.max(0, grossWall - inp.windowArea);

    var outdoor = stateFromWb(inp.outdoorDb, inp.outdoorWb, inp.pressure);
    var indoor = stateFromRh(inp.indoorDb, inp.indoorRh, inp.pressure);

    var tSolWall = inp.outdoorDb + inp.wallAbs * inp.wallSolar / inp.outdoorFilm;
    var tSolRoof = inp.outdoorDb + inp.roofAbs * inp.roofSolar / inp.outdoorFilm;
    var qWall = inp.wallU * netWall * (tSolWall - inp.indoorDb) / 1000.0;
    var qRoof = inp.roofU * area * (tSolRoof - inp.indoorDb) / 1000.0;
    var qWinCond = inp.windowU * inp.windowArea * (inp.outdoorDb - inp.indoorDb) / 1000.0;
    var qWinSolar = inp.windowShgc * inp.windowArea * inp.wallSolar * inp.shading / 1000.0;

    var profile = ACTIVITY_PROFILES[inp.activity] || ACTIVITY_PROFILES['Office work'];
    var qPeopleS = inp.occupants * profile.sensible_w / 1000.0;
    var qPeopleL = inp.occupants * profile.latent_w / 1000.0;
    var qLight = inp.lightingWm2 * area / 1000.0;
    var qEquip = inp.equipmentW / 1000.0;

    var infM3s = volume * inp.infiltrationAch / 3600.0;
    var infMass = infM3s / outdoor.v;
    var infTotal = infMass * (outdoor.h - indoor.h);
    var infLatent = infMass * H_FG_0 * (outdoor.w - indoor.w);
    var infSensible = infTotal - infLatent;

    var ventM3s = inp.occupants * inp.ventilationLsp / 1000.0;
    var ventMass = ventM3s > 0 ? ventM3s / outdoor.v : 0;
    var ventTotal = ventMass * (outdoor.h - indoor.h);
    var ventLatent = ventMass * H_FG_0 * (outdoor.w - indoor.w);
    var ventSensible = ventTotal - ventLatent;

    function comp(name, scope, category, sensible, latent, basis) {
      return { name: name, scope: scope, category: category,
        sensible: sensible, latent: latent, total: sensible + latent, basis: basis };
    }

    var components = [
      comp('Wall conduction', 'Room', 'Envelope', qWall, 0,
        'Sol-air ' + tSolWall.toFixed(1) + ' °C · net ' + netWall.toFixed(1) + ' m²'),
      comp('Roof conduction', 'Room', 'Envelope', qRoof, 0,
        'Sol-air ' + tSolRoof.toFixed(1) + ' °C · roof ' + area.toFixed(1) + ' m²'),
      comp('Window conduction', 'Room', 'Envelope', qWinCond, 0,
        'U = ' + inp.windowU.toFixed(2) + ' W/m²K'),
      comp('Window solar transmission', 'Room', 'Solar', qWinSolar, 0,
        'SHGC = ' + inp.windowShgc.toFixed(2) + ' · shading ' + inp.shading.toFixed(2)),
      comp('Occupants, sensible', 'Room', 'Internal', qPeopleS, 0,
        inp.occupants + ' people × ' + profile.sensible_w.toFixed(0) + ' W'),
      comp('Occupants, latent', 'Room', 'Internal', 0, qPeopleL,
        inp.occupants + ' people × ' + profile.latent_w.toFixed(0) + ' W'),
      comp('Lighting', 'Room', 'Internal', qLight, 0,
        inp.lightingWm2.toFixed(1) + ' W/m² × ' + area.toFixed(1) + ' m²'),
      comp('Equipment', 'Room', 'Internal', qEquip, 0, 'Connected equipment'),
      comp('Infiltration, sensible', 'Room', 'Infiltration', infSensible, 0,
        inp.infiltrationAch.toFixed(2) + ' ACH'),
      comp('Infiltration, latent', 'Room', 'Infiltration', 0, infLatent,
        'ΔW ' + (1000 * (outdoor.w - indoor.w)).toFixed(2) + ' g/kg'),
      comp('Outdoor ventilation, sensible', 'Outdoor air', 'Ventilation', ventSensible, 0,
        (ventM3s * 3600).toFixed(0) + ' m³/h'),
      comp('Outdoor ventilation, latent', 'Outdoor air', 'Ventilation', 0, ventLatent,
        inp.ventilationLsp.toFixed(1) + ' L/s per person')
    ];

    var roomSensible = 0, roomLatent = 0;
    components.forEach(function (c) {
      if (c.scope === 'Room') { roomSensible += c.sensible; roomLatent += c.latent; }
    });
    var roomTotal = roomSensible + roomLatent;
    var roomRshf = roomTotal > 1e-9 ? roomSensible / roomTotal : 0;
    var designSensible = roomSensible + ventSensible;
    var designLatent = roomLatent + ventLatent;
    var designTotal = designSensible + designLatent;
    if (designTotal <= 0) throw new Error('This case produces no cooling load');

    var notes = [
      'Peak-load estimate uses a steady sol-air temperature for opaque surfaces.',
      'RSHF uses room gains only; ventilation is added for the coil load.',
      'Fan power, duct gain and envelope thermal lag are not included.'
    ];
    if (grossWall > 0 && inp.windowArea / grossWall > 0.5) {
      notes.push('Window-to-wall ratio is high; check solar gain and daylight design.');
    }
    if (outdoor.w < indoor.w) {
      notes.push('Outdoor air is drier than the room, so outdoor latent gain is negative.');
    }

    return {
      inputs: inp,
      components: components,
      roomSensible: roomSensible,
      roomLatent: roomLatent,
      roomTotal: roomTotal,
      roomRshf: roomRshf,
      ventSensible: ventSensible,
      ventLatent: ventLatent,
      ventTotal: ventSensible + ventLatent,
      designSensible: designSensible,
      designLatent: designLatent,
      designTotal: designTotal,
      designShr: designTotal !== 0 ? designSensible / designTotal : 0,
      designTr: designTotal / TR_KW,
      area: area,
      volume: volume,
      netWall: netWall,
      grossWall: grossWall,
      outdoor: outdoor,
      indoor: indoor,
      ventM3s: ventM3s,
      infM3s: infM3s,
      ventMass: ventMass,
      infMass: infMass,
      notes: notes
    };
  }

  /* ------------------------------------------------------------------ */
  /* Air handling unit                                                  */
  /* ------------------------------------------------------------------ */
  function mixAir(room, outdoor, fraction, P) {
    P = finite(P, P_ATM);
    var f = Number(fraction);
    if (!(f >= 0 && f <= 1)) throw new Error('Outdoor-air fraction out of range');
    var w = f * outdoor.w + (1 - f) * room.w;
    var h = f * outdoor.h + (1 - f) * room.h;
    return stateFromHW(h, w, P);
  }

  function supplyStateFromLoads(room, sensible, latent, supplyDb, P) {
    P = finite(P, P_ATM);
    sensible = Number(sensible); latent = Number(latent);
    if (sensible <= 0) throw new Error('Sensible load must be positive');
    if (latent < -1e-9) throw new Error('Latent load cannot be negative');
    if (supplyDb >= room.db - 0.2) throw new Error('Supply air must be at least 0.2 K below room');
    var cp = moistCp(room.w);
    var mass = sensible / (cp * (room.db - supplyDb));
    if (!(mass > 0) || !isFinite(mass)) throw new Error('Invalid supply airflow');
    var ws = room.w - latent / (mass * H_FG_0);
    var wSat = satW(supplyDb, P);
    if (ws < -1e-9) throw new Error('Latent load requires negative humidity ratio');
    if (ws > wSat + 1e-6) throw new Error('Supply air would be supersaturated');
    return { state: stateFromW(supplyDb, Math.max(0, ws), P), mass: mass };
  }

  function findADP(mixed, supply, P) {
    P = finite(P, P_ATM);
    var tm = mixed.db, wm = mixed.w, ts = supply.db, ws = supply.w;
    if (ts >= tm - 0.05) throw new Error('Leaving air must be cooler than entering mixture');
    if (wm < ws - 1e-7) throw new Error('Cooling process must not add moisture');
    if (tm === ts) throw new Error('Coil line has no span');
    var slope = (ws - wm) / (ts - tm);
    function lineW(t) { return wm + slope * (t - tm); }
    function diff(t) { return lineW(t) - satW(t, P); }

    var adpDb, adpTol = 1e-7;
    var fHigh = diff(ts);
    if (fHigh >= -1e-8) {
      adpDb = ts;
    } else {
      var step = 0.25, cursor = ts, found = false;
      var upperT = ts, lowerT = ts;
      while (cursor > -30) {
        cursor -= step;
        var value = diff(cursor);
        if (value >= 0) { lowerT = cursor; found = true; break; }
        upperT = cursor;
      }
      if (!found) throw new Error('Coil line does not cross saturation');
      var hi = upperT, lo = lowerT;
      for (var i = 0; i < 100; i++) {
        var mid = 0.5 * (hi + lo);
        if (diff(mid) < 0) hi = mid; else lo = mid;
        if (Math.abs(lo - hi) < adpTol) break;
      }
      adpDb = 0.5 * (hi + lo);
    }
    var adpW = Math.min(satW(adpDb, P), satW(adpDb, P));
    var adp = stateFromW(adpDb, adpW, P);
    if (wm - adpW <= 1e-10) throw new Error('ADP cannot be resolved');
    var bpf = clamp((wm - ws) / (wm - adpW), 0, 1);
    return { adp: adp, bpf: bpf };
  }

  function designAHU(room, outdoor, sensible, latent, supplyDb, oaFraction, P) {
    P = finite(P, P_ATM);
    var mixed = mixAir(room, outdoor, oaFraction, P);
    var sup = supplyStateFromLoads(room, sensible, latent, supplyDb, P);
    var supply = sup.state, mass = sup.mass;
    if (supply.db >= mixed.db) throw new Error('Supply must be cooler than mixed air');
    if (supply.w > mixed.w + 1e-7) throw new Error('Process would humidify the air');
    var adpRes = findADP(mixed, supply, P);
    var coilTotal = mass * (mixed.h - supply.h);
    var coilLatent = mass * H_FG_0 * (mixed.w - supply.w);
    var coilSensible = coilTotal - coilLatent;
    var spaceTotal = sensible + latent;
    return {
      room: room, outdoor: outdoor, mixed: mixed, supply: supply,
      adp: adpRes.adp, oaFraction: oaFraction, supplyDb: supplyDb,
      mass: mass, volume: mass * supply.v,
      spaceSensible: sensible, spaceLatent: latent,
      rshf: spaceTotal > 1e-9 ? sensible / spaceTotal : 0,
      coilTotal: coilTotal, coilSensible: coilSensible, coilLatent: coilLatent,
      coilShr: coilTotal > 1e-9 ? coilSensible / coilTotal : 0,
      bpf: adpRes.bpf, adpDb: adpRes.adp.db
    };
  }

  /* ------------------------------------------------------------------ */
  /* R134a property table + vapour-compression cycle                    */
  /* ------------------------------------------------------------------ */
  var _levels = null;

  function levels() {
    if (_levels) return _levels;
    if (!global.R134A || !global.R134A.grid) {
      throw new Error('R134a table not loaded');
    }
    var map = new Map();
    global.R134A.grid.forEach(function (row) {
      var p = row[0];
      if (!map.has(p)) map.set(p, []);
      map.get(p).push(row);
    });
    var arr = [];
    map.forEach(function (rows, p) {
      rows.sort(function (a, b) { return a[1] - b[1]; });
      arr.push({ p: p, rows: rows });
    });
    arr.sort(function (a, b) { return a.p - b.p; });
    _levels = arr;
    return arr;
  }

  function satAtT(tC) {
    var sat = global.R134A.sat;
    var t = Number(tC);
    if (t < sat[0][0] - 1e-9 || t > sat[sat.length - 1][0] + 1e-9) {
      throw new Error('Temperature outside refrigerant table');
    }
    if (t <= sat[0][0]) {
      var r0 = sat[0];
      return { T: r0[0], P: r0[1], hf: r0[2], hg: r0[3], sf: r0[4], sg: r0[5], rg: r0[6], vf: r0[7] };
    }
    for (var i = 0; i < sat.length - 1; i++) {
      var a = sat[i], b = sat[i + 1];
      if (t >= a[0] && t <= b[0]) {
        var f = (t - a[0]) / (b[0] - a[0]);
        function L(k) { return a[k] + (b[k] - a[k]) * f; }
        return { T: t, P: L(1), hf: L(2), hg: L(3), sf: L(4), sg: L(5), rg: L(6), vf: L(7) };
      }
    }
    throw new Error('Refrigerant table lookup failed');
  }

  function levelAt(level, tC) {
    var rows = level.rows;
    if (tC < rows[0][1] - 1e-9 || tC > rows[rows.length - 1][1] + 1e-9) return null;
    for (var i = 0; i < rows.length - 1; i++) {
      var a = rows[i], b = rows[i + 1];
      if (tC >= a[1] && tC <= b[1]) {
        var f = (tC - a[1]) / (b[1] - a[1]);
        return {
          h: a[2] + (b[2] - a[2]) * f,
          s: a[3] + (b[3] - a[3]) * f,
          rho: a[4] + (b[4] - a[4]) * f
        };
      }
    }
    var last = rows[rows.length - 1];
    return { h: last[2], s: last[3], rho: last[4] };
  }

  function bracket(p) {
    var lv = levels();
    if (p < lv[0].p - 1e-9 || p > lv[lv.length - 1].p + 1e-9) {
      throw new Error('Pressure outside R134a table');
    }
    if (p <= lv[0].p) return [lv[0], lv[1], 0];
    for (var i = 0; i < lv.length - 1; i++) {
      if (p >= lv[i].p && p <= lv[i + 1].p) {
        return [lv[i], lv[i + 1], (p - lv[i].p) / (lv[i + 1].p - lv[i].p)];
      }
    }
    var n = lv.length - 1;
    return [lv[n - 1], lv[n], 1];
  }

  function shProps(p, tC) {
    var pair = bracket(p), lo = pair[0], hi = pair[1], f = pair[2];
    var a = levelAt(lo, tC), b = levelAt(hi, tC);
    if (!a || !b) throw new Error('State outside superheated table');
    return {
      h: a.h + (b.h - a.h) * f,
      s: a.s + (b.s - a.s) * f,
      rho: a.rho + (b.rho - a.rho) * f
    };
  }

  function invert(p, target, prop) {
    var pair = bracket(p), lo = pair[0], hi = pair[1];
    var tMin = Math.max(lo.rows[0][1], hi.rows[0][1]) + 1e-6;
    var tMax = Math.min(lo.rows[lo.rows.length - 1][1], hi.rows[hi.rows.length - 1][1]) - 1e-6;
    var fLo = shProps(p, tMin)[prop];
    var fHi = shProps(p, tMax)[prop];
    if (target < Math.min(fLo, fHi) || target > Math.max(fLo, fHi)) {
      throw new Error('Cycle state is outside the property table');
    }
    var low = tMin, high = tMax;
    for (var i = 0; i < 100; i++) {
      var mid = 0.5 * (low + high);
      var val = shProps(p, mid)[prop];
      if (val < target) low = mid; else high = mid;
      if (high - low < 1e-7) break;
    }
    return 0.5 * (low + high);
  }

  function computeCycle(raw) {
    var inp = Object.assign({
      evaporatingC: 2.0, condensingC: 45.0, superheatK: 5.0,
      subcoolingK: 5.0, isentropicEfficiency: 0.75, coolingLoadKw: 19.16
    }, raw || {});
    var te = Number(inp.evaporatingC), tc = Number(inp.condensingC);
    var sh = Number(inp.superheatK), sc = Number(inp.subcoolingK);
    var eta = Number(inp.isentropicEfficiency), load = Number(inp.coolingLoadKw);
    if (te < -15 || te > 25) throw new Error('Evaporating temperature outside -15…25 °C');
    if (tc < 25 || tc > 60) throw new Error('Condensing temperature outside 25…60 °C');
    if (tc <= te + 3) throw new Error('Condensing must be at least 3 K above evaporating');
    if (sh < 0 || sh > 40) throw new Error('Superheat outside 0…40 K');
    if (sc < 0 || sc > 30) throw new Error('Subcooling outside 0…30 K');
    if (eta < 0.3 || eta > 1) throw new Error('Isentropic efficiency outside 0.30…1.00');
    if (!(load > 0)) throw new Error('Cooling load must be positive');

    var evap = satAtT(te), cond = satAtT(tc);
    var pE = evap.P, pC = cond.P;
    if (pE < 1.5 || pC > 20) throw new Error('Pressure outside R134a table');

    var saturatedSuction = sh <= 0.01;
    var h1, s1, rho1, t1;
    if (saturatedSuction) {
      h1 = evap.hg; s1 = evap.sg; rho1 = evap.rg; t1 = te;
    } else {
      t1 = te + sh;
      var pr1 = shProps(pE, t1);
      h1 = pr1.h; s1 = pr1.s; rho1 = pr1.rho;
    }

    var t2s = invert(pC, s1, 's');
    var h2s = shProps(pC, t2s).h;
    var h2 = h1 + (h2s - h1) / eta;
    var t2 = invert(pC, h2, 'h');
    var s2 = shProps(pC, t2).s;

    var noSubcooling = sc <= 0.01;
    var t3 = noSubcooling ? tc : tc - sc;
    var liq = satAtT(t3);
    var h3 = liq.hf, s3 = liq.sf;
    var subcooled = h3 < cond.hf - 1e-6;

    var h4 = h3;
    var x4 = (h4 - evap.hf) / (evap.hg - evap.hf);
    if (x4 < -1e-6 || x4 > 1.000001) throw new Error('Expansion state outside two-phase region');
    x4 = clamp(x4, 0, 1);
    var t4 = te;
    var s4 = evap.sf + x4 * (evap.sg - evap.sf);

    var qEvap = h1 - h4;
    var wComp = h2 - h1;
    var qCond = h2 - h3;
    if (qEvap <= 0 || wComp <= 0) throw new Error('Cycle states are not physical');

    var mass = load / qEvap;
    var compKw = mass * wComp;
    var condKw = mass * qCond;
    var cop = qEvap / wComp;
    var carnot = (te + 273.15) / (tc - te);
    var pr = pC / pE;
    var qVol = qEvap * rho1;

    return {
      inputs: inp,
      fluid: 'R134a',
      pEvapBar: pE, pCondBar: pC,
      pEvapKpa: pE * 100, pCondKpa: pC * 100,
      tEvap: te, tCond: tc,
      states: [
        { n: 1, label: 'Compressor suction', ar: 'دخول الضاغط', T: t1, P: pE, h: h1, s: s1,
          quality: saturatedSuction ? 1 : null },
        { n: 2, label: 'Compressor discharge', ar: 'خروج الضاغط', T: t2, P: pC, h: h2, s: s2, quality: null },
        { n: 3, label: subcooled ? 'Condenser exit (subcooled)' : 'Condenser exit (saturated liquid)',
          ar: subcooled ? 'خروج المكثف (سائل مبرد تحت التشبع)' : 'خروج المكثف (سائل مشبع)',
          T: t3, P: pC, h: h3, s: s3, quality: 0 },
        { n: 4, label: 'Expansion-valve outlet', ar: 'خروج صمام التمدد', T: t4, P: pE, h: h4, s: s4, quality: x4 }
      ],
      t2s: t2s,
      qEvap: qEvap, wComp: wComp, qCond: qCond,
      mass: mass, volume: mass / rho1,
      coolingKw: load, coolingTr: load / TR_KW,
      compressorKw: compKw, condenserKw: condKw,
      cop: cop, carnotCop: carnot, secondLaw: cop / carnot,
      pressureRatio: pr,
      qVolumetric: qVol,
      rho1: rho1,
      subcooled: subcooled,
      saturatedSuction: saturatedSuction
    };
  }

  /* ------------------------------------------------------------------ */
  /* Comfort and closed-loop control                                    */
  /* ------------------------------------------------------------------ */
  var COMFORT = { etMin: 23.0, etMax: 26.0, rhMin: 30.0, rhMax: 70.0 };

  function defaultSim() {
    return {
      controller: 'PID', actuator: 'Valve',
      durationH: 8.0, timestepS: 60, startHour: 8.0,
      setpointC: 24.5, initialDb: 28.8, initialRh: 55.0, pressure: P_ATM,
      outdoorMean: 36.0, outdoorAmp: 4.5, outdoorRh: 25.0,
      zoneUa: 0.15, capacitance: 2600.0, volume: 307.0, infiltrationAch: 0.50,
      internalSensible: 4.5, internalLatent: 0.90,
      coolingCapacity: 10.0, supplyMin: 12.5, supplyMax: 22.0, cop: 3.20,
      kp: 22.0, ki: 0.070, kd: 25.0, band: 0.6,
      etMin: COMFORT.etMin, etMax: COMFORT.etMax,
      rhMin: COMFORT.rhMin, rhMax: COMFORT.rhMax
    };
  }

  function simulateControl(raw) {
    var inp = Object.assign(defaultSim(), raw || {});
    var steps = Math.round(inp.durationH * 3600 / inp.timestepS);
    if (steps < 2) throw new Error('Simulation too short for time step');
    var dt = inp.durationH * 3600 / steps;
    var n = steps + 1;

    var tHist = new Float64Array(n);
    var rhHist = new Float64Array(n);
    var wHist = new Float64Array(n);
    var etHist = new Float64Array(n);
    var outHist = new Float64Array(n);
    var supHist = new Float64Array(n);
    var valveHist = new Float64Array(n);
    var coolHist = new Float64Array(n);
    var sensHist = new Float64Array(n);
    var latHist = new Float64Array(n);
    var comfortHist = new Uint8Array(n);
    var thermalHist = new Uint8Array(n);
    var humidHist = new Uint8Array(n);
    var timeH = new Float64Array(n);
    var clockH = new Float64Array(n);

    for (var s = 0; s <= steps; s++) {
      timeH[s] = s * dt / 3600;
      clockH[s] = (inp.startHour + timeH[s]) % 24;
    }

    var roomT = inp.initialDb;
    var roomW = wFromRh(roomT, inp.initialRh, inp.pressure);
    var mInf = inp.volume * inp.infiltrationAch / 3600.0 / 0.87;
    var cpRoom = moistCp(roomW);
    var designDt = Math.max(0.5, inp.setpointC - inp.supplyMin);
    var mSupply = inp.coolingCapacity / (cpRoom * designDt);

    var integral = 0, output = 0, previousT = roomT;
    var thresholdOn = false, switches = 0, previousOn = false;
    var qCoolPrev = 0, qLatPrev = 0, roomRh = inp.initialRh;

    function record(i) {
      tHist[i] = roomT;
      wHist[i] = roomW;
      roomRh = rhFromW(roomT, roomW, inp.pressure);
      rhHist[i] = roomRh;
      var et = effectiveTemperature(roomT, roomRh);
      etHist[i] = et;
      outHist[i] = inp.outdoorMean + inp.outdoorAmp *
        Math.cos(2 * Math.PI * (clockH[i] - 15.0) / 24.0);
      supHist[i] = qCoolPrev > 1e-6 ? roomT - qCoolPrev / (mSupply * cpRoom) : NaN;
      valveHist[i] = output;
      sensHist[i] = qCoolPrev;
      latHist[i] = qLatPrev;
      coolHist[i] = qCoolPrev + qLatPrev;
      var thermal = et >= inp.etMin && et <= inp.etMax;
      var humid = roomRh >= inp.rhMin && roomRh <= inp.rhMax;
      thermalHist[i] = thermal ? 1 : 0;
      humidHist[i] = humid ? 1 : 0;
      comfortHist[i] = thermal && humid ? 1 : 0;
    }

    record(0);

    for (var i = 0; i < steps; i++) {
      var outT = inp.outdoorMean + inp.outdoorAmp *
        Math.cos(2 * Math.PI * (clockH[i] - 15.0) / 24.0);
      var outW = wFromRh(outT, inp.outdoorRh, inp.pressure);
      roomRh = rhFromW(roomT, roomW, inp.pressure);

      if (inp.controller === 'PID') {
        var error = roomT - inp.setpointC;
        var derivative = (roomT - previousT) / (dt / 60.0);
        var unsaturated = clamp(inp.kp * error + inp.ki * integral + inp.kd * derivative, 0, 100);
        if ((unsaturated > 0 && unsaturated < 100) ||
            (unsaturated >= 100 && error < 0) ||
            (unsaturated <= 0 && error > 0)) {
          integral += error * dt;
          unsaturated = clamp(inp.kp * error + inp.ki * integral + inp.kd * derivative, 0, 100);
        }
        output = clamp(unsaturated, 0, 100);
      } else {
        if (roomT > inp.setpointC + inp.band / 2) thresholdOn = true;
        else if (roomT < inp.setpointC - inp.band / 2) thresholdOn = false;
        output = thresholdOn ? 100 : 0;
        var onState = output > 50;
        if (onState !== previousOn) { switches++; previousOn = onState; }
      }

      var qSens;
      if (inp.actuator === 'Valve') {
        qSens = inp.coolingCapacity * output / 100.0;
      } else {
        if (output <= 0.25) qSens = 0;
        else {
          var satTarget = inp.supplyMax - (inp.supplyMax - inp.supplyMin) * output / 100.0;
          var available = mSupply * cpRoom * Math.max(0, roomT - satTarget);
          qSens = Math.min(inp.coolingCapacity, available);
        }
      }
      qSens = clamp(qSens, 0, inp.coolingCapacity);

      var loadFraction = qSens / inp.coolingCapacity;
      var supplyW = roomW, qLat = 0;
      if (loadFraction > 0.02) {
        var bpfEff = 0.18 + 0.72 * (1.0 - loadFraction);
        var wAdp = 0.92 * satW(9.0, inp.pressure);
        supplyW = roomW - (1.0 - bpfEff) * Math.max(0, roomW - wAdp);
        supplyW = clamp(supplyW, 0, roomW);
        qLat = Math.max(0, mSupply * H_FG_0 * (roomW - supplyW));
      }

      var qExt = inp.zoneUa * (outT - roomT) + mInf * cpRoom * (outT - roomT);
      var dT = (inp.internalSensible + qExt - qSens) / inp.capacitance;
      roomT = roomT + dT * dt;

      var latentGain = inp.internalLatent / H_FG_0;
      var balance = mInf * (outW - roomW) + latentGain - mSupply * (roomW - supplyW);
      var moistureCap = Math.max(60.0, inp.volume * 1.18);
      roomW = Math.max(0, roomW + balance * dt / moistureCap);
      var wSat = satW(roomT, inp.pressure);
      if (roomW > 0.999 * wSat) roomW = 0.999 * wSat;

      previousT = tHist[i];
      qCoolPrev = qSens;
      qLatPrev = qLat;
      record(i + 1);
    }

    var comfortCount = 0, thermalCount = 0, humidCount = 0;
    var half = Math.max(1, Math.floor(steps / 2));
    var halfCount = 0;
    var delivered = 0, peak = 0;
    for (var k = 0; k <= steps; k++) {
      comfortCount += comfortHist[k];
      thermalCount += thermalHist[k];
      humidCount += humidHist[k];
      if (k >= half) halfCount += comfortHist[k];
      if (k >= 1) delivered += coolHist[k] * dt / 3600.0;
      if (coolHist[k] > peak) peak = coolHist[k];
    }

    return {
      inputs: inp, steps: steps, dt: dt,
      timeH: timeH, clockH: clockH,
      roomT: tHist, roomRh: rhHist, roomW: wHist, roomEt: etHist,
      outdoorT: outHist, supplyT: supHist, valve: valveHist,
      cooling: coolHist, sensible: sensHist, latent: latHist,
      comfort: comfortHist, thermal: thermalHist, humidity: humidHist,
      comfortPct: 100 * comfortCount / n,
      comfortLastHalfPct: 100 * halfCount / Math.max(1, n - half),
      thermalPct: 100 * thermalCount / n,
      humidityPct: 100 * humidCount / n,
      deliveredKwh: delivered,
      electricityKwh: delivered / inp.cop,
      peakKw: peak,
      finalDb: tHist[steps],
      finalRh: rhHist[steps],
      finalEt: etHist[steps],
      switches: switches
    };
  }

  function simulateBoth(raw) {
    var base = Object.assign(defaultSim(), raw || {});
    var pid = simulateControl(Object.assign({}, base, { controller: 'PID' }));
    var th = simulateControl(Object.assign({}, base, { controller: 'Threshold' }));
    return { pid: pid, threshold: th };
  }

  /* ------------------------------------------------------------------ */
  /* Quick design                                                       */
  /* ------------------------------------------------------------------ */
  var SPACE_TYPES = {
    'Apartment living room': { ar: 'غرفة معيشة', height: 2.9, areaPerPerson: 18, lighting: 5, equip: 7, activity: 'Seated, quiet', vent: 8, ach: 0.60, cap: 140, schedule: 'residential', open: false, note: 'احتلال مسائي وحمل داخلي أخف.' },
    'Office': { ar: 'مكتب', height: 3.0, areaPerPerson: 9, lighting: 9, equip: 12, activity: 'Office work', vent: 10, ach: 0.50, cap: 160, schedule: 'office', open: false, note: 'ساعات العمل هي الحاكمة؛ الأشخاص والأجهزة حمل ثابت.' },
    'Classroom': { ar: 'صف دراسي', height: 3.2, areaPerPerson: 2.5, lighting: 9, equip: 4, activity: 'Seated, quiet', vent: 8, ach: 0.60, cap: 150, schedule: 'classroom', open: false, note: 'كثافة إشغال عالية ليوم دراسي قصير.' },
    'Retail shop': { ar: 'محل تجاري', height: 3.5, areaPerPerson: 12, lighting: 12, equip: 6, activity: 'Standing / light work', vent: 8, ach: 0.70, cap: 120, schedule: 'retail', open: true, note: 'صالة عالية مفتوحة بإضاءة قوية وحركة أبواب.' },
    'Restaurant / café': { ar: 'مطعم / مقهى', height: 3.2, areaPerPerson: 3, lighting: 8, equip: 25, activity: 'Light bench work', vent: 12, ach: 0.70, cap: 160, schedule: 'restaurant', open: true, note: 'معدات المطبخ والجدول المسائي يقودان الحمل.' },
    'Mosque / assembly hall': { ar: 'مسجد / قاعة تجمع', height: 4.2, areaPerPerson: 2, lighting: 5, equip: 2, activity: 'Seated, quiet', vent: 8, ach: 0.80, cap: 220, schedule: 'assembly', open: true, note: 'حجم كبير وذروات صلاة كثيفة وكتلة إنشائية ثقيلة.' },
    'Clinic / laboratory': { ar: 'عيادة / مختبر', height: 3.0, areaPerPerson: 10, lighting: 11, equip: 20, activity: 'Light bench work', vent: 12, ach: 0.60, cap: 150, schedule: 'clinic', open: false, note: 'حمل معدات مستمر ومعدل هواء نقي أعلى.' }
  };

  var CITIES = {
    'Baghdad': { ar: 'بغداد', db: 46.0, wb: 24.0, swing: 13.0, note: 'يوم تصميم صيفي حار جاف.' },
    'Basra': { ar: 'البصرة', db: 46.0, wb: 27.5, swing: 11.0, note: 'يوم تصميم حار رطب على الخليج.' },
    'Mosul': { ar: 'الموصل', db: 42.0, wb: 23.0, swing: 14.0, note: 'صيف حار بفرق كبير بين الليل والنهار.' },
    'Erbil': { ar: 'أربيل', db: 40.0, wb: 21.5, swing: 15.0, note: 'صيف دافئ وليالٍ باردة.' },
    'Najaf': { ar: 'النجف', db: 45.5, wb: 23.5, swing: 13.5, note: 'يوم تصميم حار جاف.' },
    'Other / custom': { ar: 'أخرى / مخصص', db: 43.0, wb: 23.0, swing: 13.0, note: 'أدخل ظروف التصميم بنفسك.' }
  };

  var ENVELOPE_QUALITY = {
    'Basic (older building)': { ar: 'أساسي (بناء قديم)', wallU: 1.35, roofU: 1.00, windowU: 4.80, shgc: 0.67, shading: 0.95, infFactor: 1.30, note: 'زجاج مفرد وعزل ضعيف؛ توقع حملاً أعلى.' },
    'Standard': { ar: 'قياسي', wallU: 0.55, roofU: 0.35, windowU: 2.60, shgc: 0.50, shading: 0.85, infFactor: 1.00, note: 'جدار معزول وزجاج مزدوج: بناء حديث شائع.' },
    'High performance': { ar: 'عالي الأداء', wallU: 0.30, roofU: 0.22, windowU: 1.45, shgc: 0.30, shading: 0.65, infFactor: 0.75, note: 'زجاج Low-E وعزل جيد وتحكم بالتسرب.' }
  };

  var ORIENTATIONS = {
    'North': { ar: 'شمال', solar: 130.0, note: 'ضوء منتشر طوال اليوم؛ ألطف واجهة.' },
    'East': { ar: 'شرق', solar: 520.0, note: 'شمس الصباح؛ الذروة قبل الظهر.' },
    'South': { ar: 'جنوب', solar: 430.0, note: 'شمس ظهيرة عالية؛ المظلات فعالة.' },
    'West': { ar: 'غرب', solar: 600.0, note: 'شمس العصر؛ أسخن وأحدث ذروة.' }
  };

  var SYSTEM_LABELS = {
    split: { ar: 'مكيفات سبليت عالية الجدار', familyAr: 'DX أحادي المنطقة', noteAr: 'الأبسط والأقل كلفة أولية، ويمكن إضافة وحدة كل مرة.', en: 'High-wall split units' },
    ducted: { ar: 'وحدات باكج بمجاري', familyAr: 'DX بمجاري', noteAr: 'توزيع مجاري للمساحات المفتوحة مع مجرى هواء نقي.', en: 'Ducted packaged units' },
    vrf: { ar: 'VRF متعدد', familyAr: 'تدفق مبرد متغير', noteAr: 'وحدات داخلية منفصلة وكفاءة جزئية عالية طوال اليوم.', en: 'VRF multi-split' },
    chiller: { ar: 'تشيلر مبرد بالهواء + AHU', familyAr: 'ماء مبرد مركزي', noteAr: 'محطة مركزية تغذي وحدة مناولة هواء وتوزيع مجاري.', en: 'Air-cooled chiller + AHU' }
  };

  var SYSTEM_COP = { split: 3.15, ducted: 3.00, vrf: 3.65, chiller: 3.25 };
  var SYSTEM_FAN = { split: 0.10, ducted: 0.28, vrf: 0.16, chiller: 0.34 };
  var SYSTEM_DT = { split: 10.0, ducted: 10.0, vrf: 9.0, chiller: 8.0 };
  var SIZES = {
    split: [2.6, 3.5, 5.3, 7.1],
    vrf: [8, 10, 12.5, 14, 16, 18, 20],
    ducted: [10, 15, 20, 25, 30, 40, 50, 60],
    chiller: [40, 60, 80, 100, 130, 160, 200, 250, 300]
  };

  function pickSizes(target, sizes) {
    for (var i = 0; i < sizes.length; i++) {
      if (target <= sizes[i] + 1e-9) return { size: sizes[i], count: 1, capacity: sizes[i] };
    }
    var largest = sizes[sizes.length - 1];
    var count = Math.max(1, Math.ceil(target / largest));
    for (var j = 0; j < sizes.length; j++) {
      if (sizes[j] * count >= target - 1e-9) {
        return { size: sizes[j], count: count, capacity: sizes[j] * count };
      }
    }
    return { size: largest, count: count, capacity: largest * count };
  }

  function chooseSystem(inp, targetKw) {
    var pref = inp.systemPreference || 'Auto';
    if (pref !== 'Auto') {
      if (SYSTEM_LABELS[pref]) return pref;
      if (/split|سبليت/i.test(pref)) return 'split';
      if (/duct|باكج|مجاري/i.test(pref)) return 'ducted';
      if (/vrf/i.test(pref)) return 'vrf';
      if (/chiller|تشيلر/i.test(pref)) return 'chiller';
    }
    if (targetKw <= 7.5) return 'split';
    if (SPACE_TYPES[inp.spaceType] && SPACE_TYPES[inp.spaceType].open) {
      return targetKw <= 60 ? 'ducted' : 'chiller';
    }
    if (targetKw <= 100) return 'vrf';
    return 'chiller';
  }

  function defaultQuick() {
    return {
      spaceType: 'Office', floorArea: 96.0, city: 'Baghdad', glazing: 0.25,
      orientation: 'West', envelope: 'Standard', occupants: null,
      indoorDb: 24.0, indoorRh: 50.0, customDb: null, customWb: null,
      systemPreference: 'Auto', margin: 0.12
    };
  }

  function buildQuick(raw) {
    var inp = Object.assign(defaultQuick(), raw || {});
    var space = SPACE_TYPES[inp.spaceType];
    if (!space) throw new Error('Unknown space type');
    var city = CITIES[inp.city];
    if (!city) throw new Error('Unknown city');
    if (!ORIENTATIONS[inp.orientation]) throw new Error('Unknown orientation');
    var env = ENVELOPE_QUALITY[inp.envelope];
    if (!env) throw new Error('Unknown envelope quality');
    if (!(inp.floorArea >= 10 && inp.floorArea <= 4000)) throw new Error('Floor area must be 10…4000 m²');
    if (!(inp.glazing >= 0 && inp.glazing <= 0.70)) throw new Error('Glazing must be 0…70%');
    if (!(inp.margin >= 0 && inp.margin <= 0.40)) throw new Error('Margin must be 0…40%');

    var custom = inp.city === 'Other / custom';
    var outDb = custom && inp.customDb != null ? Number(inp.customDb) : city.db;
    var outWb = custom && inp.customWb != null ? Number(inp.customWb) : city.wb;
    if (outWb >= outDb) throw new Error('Wet bulb must be below dry bulb');

    var autoOcc = Math.max(1, Math.round(inp.floorArea / space.areaPerPerson));
    var occupants = inp.occupants == null ? autoOcc : Math.max(0, Math.round(inp.occupants));

    var length = Math.sqrt(inp.floorArea * 1.35);
    var width = inp.floorArea / length;
    var perimeter = 2.0 * (length + width);
    var height = space.height;
    var grossWall = perimeter * height * 0.85;
    var windowArea = Math.min(0.70 * grossWall, inp.glazing * grossWall);

    var loadInputs = {
      projectName: 'Quick design · ' + inp.spaceType,
      lengthM: length, widthM: width, heightM: height, exposedWallFraction: 0.85,
      wallU: env.wallU, wallAbs: 0.65, roofU: env.roofU, roofAbs: 0.75,
      windowU: env.windowU, windowShgc: env.shgc, windowArea: windowArea, shading: env.shading,
      wallSolar: ORIENTATIONS[inp.orientation].solar, roofSolar: 950.0, outdoorFilm: 20.0,
      outdoorDb: outDb, outdoorWb: outWb, indoorDb: inp.indoorDb, indoorRh: inp.indoorRh,
      pressure: P_ATM, occupants: occupants, activity: space.activity,
      lightingWm2: space.lighting, equipmentW: space.equip * inp.floorArea,
      infiltrationAch: space.ach * env.infFactor, ventilationLsp: space.vent
    };
    var load = calcLoad(loadInputs);

    var targetKw = load.designTotal * (1 + inp.margin);
    var key = chooseSystem(inp, targetKw);
    var pick = pickSizes(targetKw, SIZES[key]);

    var supplyDt = SYSTEM_DT[key];
    var airflow = load.designSensible / (1.02 * supplyDt) * 3600.0 / 1.15;
    airflow = Math.max(200.0, Math.round(airflow / 50.0) * 50.0);
    var freshAir = load.ventM3s * 3600.0;

    var indoorUnits;
    if (key === 'vrf') indoorUnits = Math.max(1, Math.ceil(inp.floorArea / 28.0));
    else if (key === 'chiller') indoorUnits = Math.max(1, Math.ceil(inp.floorArea / 450.0));
    else indoorUnits = pick.count;

    var latentPct = 100 * load.designLatent / Math.max(1e-9, load.designTotal);
    var wwrPct = 100 * windowArea / Math.max(1e-9, grossWall);
    var rec = {
      key: key,
      name: SYSTEM_LABELS[key].ar,
      nameEn: SYSTEM_LABELS[key].en,
      family: SYSTEM_LABELS[key].familyAr,
      note: SYSTEM_LABELS[key].noteAr,
      capacityKw: pick.capacity,
      capacityTr: pick.capacity / TR_KW,
      targetKw: targetKw,
      unitSizeKw: pick.size,
      outdoorUnits: pick.count,
      indoorUnits: indoorUnits,
      airflow: airflow,
      freshAir: freshAir,
      supplyDt: supplyDt,
      cop: SYSTEM_COP[key],
      fanPer1000: SYSTEM_FAN[key],
      marginPct: 100 * (pick.capacity / targetKw - 1),
      latentPct: latentPct,
      wwrPct: wwrPct
    };

    var reasons = [{ code: 'peak', q: load.designTotal, tr: load.designTr, margin: 100 * inp.margin }];
    reasons.push({ code: 'system-' + key });
    reasons.push({ code: latentPct >= 20 ? 'latent-high' : 'latent-low', pct: latentPct });
    if (wwrPct >= 40) reasons.push({ code: 'wwr', pct: wwrPct });
    if (inp.orientation === 'West') reasons.push({ code: 'west' });

    var cautions = [
      { code: 'fresh', oa: freshAir },
      { code: 'condenser' },
      { code: 'disclaimer' }
    ];

    return {
      inputs: inp,
      space: space,
      city: city,
      envelope: env,
      orientation: ORIENTATIONS[inp.orientation],
      loadInputs: loadInputs,
      load: load,
      rec: rec,
      occupants: occupants,
      autoOccupants: autoOcc,
      dailySwing: city.swing,
      outDb: outDb,
      outWb: outWb,
      reasons: reasons,
      cautions: cautions
    };
  }

  /* ------------------------------------------------------------------ */
  global.HVAC = {
    P_ATM: P_ATM,
    TR_KW: TR_KW,
    H_FG_0: H_FG_0,
    psychro: psychro,
    ACTIVITY_PROFILES: ACTIVITY_PROFILES,
    WALL_OPTIONS: WALL_OPTIONS,
    ROOF_OPTIONS: ROOF_OPTIONS,
    GLAZING_OPTIONS: GLAZING_OPTIONS,
    WEATHER_PRESETS: WEATHER_PRESETS,
    WALL_SOLAR_OPTIONS: WALL_SOLAR_OPTIONS,
    defaultLoadInputs: defaultLoadInputs,
    calcLoad: calcLoad,
    mixAir: mixAir,
    designAHU: designAHU,
    R134A: { satAtT: satAtT, props: shProps, invert: invert },
    computeCycle: computeCycle,
    COMFORT: COMFORT,
    defaultSim: defaultSim,
    simulateControl: simulateControl,
    simulateBoth: simulateBoth,
    SPACE_TYPES: SPACE_TYPES,
    CITIES: CITIES,
    ENVELOPE_QUALITY: ENVELOPE_QUALITY,
    ORIENTATIONS: ORIENTATIONS,
    SYSTEM_LABELS: SYSTEM_LABELS,
    defaultQuick: defaultQuick,
    buildQuick: buildQuick
  };
})(typeof window !== 'undefined' ? window : globalThis);
