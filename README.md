# HVAC Design Studio

An advanced HVAC and psychrometric automation system for a four-part classroom
demonstration. It links a cooling-load estimate, an air-handling/coil design, a
real-fluid vapour-compression cycle and a closed-loop comfort simulation into one
connected design case. A quick studio at the front turns six simple answers into
a sized system and a full 24-hour design day before the detailed modules begin.

Built with Python, Streamlit, Plotly, pandas and CoolProp. The interface is a
single-page engineering workspace with a quick design studio, four detailed
modules and an overview. It opens in Arabic (right-to-left) by default, switches
to English instantly, and offers a warm light theme or a low-light dark theme.

**Designed by (HALF ENGINEERS)** · صمم بواسطة (HALF ENGINEERS)

## Run it

**On this laptop (already installed):** double-click `run_app.bat`. Streamlit
starts and the browser opens at <http://localhost:8501>. Close the console window
or press `Ctrl+C` to stop the server.

**On a fresh Windows machine:**

```bat
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\streamlit.exe run main.py
```

If the browser does not open by itself, visit <http://localhost:8501>. The pinned
versions are Streamlit 1.50.0, Plotly 6.3.1, pandas 2.3.3, NumPy 2.3.3,
CoolProp 6.7.0 and pytest 8.4.2.

## Language, appearance and credits

Both controls are at the top of the sidebar and take effect immediately without
recalculating or losing the current case.

- **Language / اللغة:** Arabic is the default (`العربية`). Every visible layer is
  localised: navigation, page prose, captions, tables, chart titles, legends,
  category axes, hover labels and the footer. The whole workspace mirrors to RTL;
  numbers, units, refrigerant codes and English abbreviations stay readable LTR.
  Calculate values remain language-independent, so switching never changes the
  engineering result.
- **Dark mode / الوضع الداكن:** a user toggle between the warm-paper light theme
  and a deep drawing-board dark theme. Cards, tables, inputs, steppers, dropdowns,
  charts, grids and the sidebar are all recoloured. The choice and language are
  kept when resetting the workspace or moving between modules.
- **Credit / الحقوق:** `صمم بواسطة (HALF ENGINEERS)` appears in the sidebar, in the
  page footer and in the app's About panel. The English interface shows
  `Designed by (HALF ENGINEERS)`.

## Quick design & simulation

The **Design & simulation** page is the front door for anyone who does not want
to enter every envelope layer. Six answers are enough:

1. space type (office, classroom, apartment, retail, restaurant, mosque, clinic),
2. floor area,
3. city (Baghdad, Basra, Mosul, Erbil, Najaf, or custom weather),
4. glazing ratio,
5. main window orientation,
6. envelope quality.

Presets fill in height, occupancy density, lighting, equipment, activity,
ventilation, infiltration, wall/roof/glass properties and solar irradiance. A
collapsible **Fine-tune the assumptions** panel exposes manual occupancy, the
indoor setpoint and humidity, a fixed system preference, the selection margin and
the custom design temperatures; every preset value can be inspected there.

The page then answers three questions on one screen:

- **How much cooling?** The six answers are mapped onto the same Chapter-4
  `LoadInputs` used by Module 1, so both paths run the identical load engine and
  reproduce each other exactly for the same inputs: 18.83 kW for the default
  96 m² Baghdad office.
- **Which system?** A transparent rule selects high-wall splits (≤ 7.5 kW),
  ducted packaged units for open plans up to 60 kW, VRF up to 100 kW, and an
  air-cooled chiller + AHU above that. The nominal size table is applied with the
  chosen margin (12% by default), and the card lists outdoor/indoor units, unit
  size, supply airflow, fresh air, supply ΔT, rated COP and the reasoning and
  cautions behind the choice.
- **What does the day look like?** A 24-hour reduced-order simulation at ten-minute
  resolution runs the selected capacity through a sine-shaped design day with
  orientation-specific solar gain, real occupancy/lighting/equipment schedules,
  two-hour pre-cooling, night setback, a capacity-limited PI controller, thermal
  and moisture inertia, a fixed coil SHR and an ambient/part-load COP correction.
  Five charts show temperature, cooling, gains, humidity and energy; a scrubbable
  hour selector drives an animated day scene and four live readings; the hourly
  table exports to CSV.

The detailed modules remain available for full engineering control, and buttons at
the bottom of the simulation open Module 1 and Module 2 with the same case.

## The four detailed modules

| Page | Curriculum area | What it does | Default result |
| --- | --- | --- | --- |
| 01 – Cooling load | Chapter 4 – load estimating | Sol-air envelope loads, glazing, people, lighting, equipment, infiltration and outdoor ventilation; RSHF and design coil load | 17.54 kW sensible + 1.62 kW latent = **19.16 kW (5.45 TR)**, RSHF 91.5% |
| 02 – Psychrometrics & AHU | Chapters 2–3 – moist air and air handling | Moist-air state solver, interactive ASHRAE-style chart, adiabatic mixing, supply-state sizing, ADP, bypass/contact factor, heating and steam humidification | **19.17 kW** coil, SHR 91.6%, ADP 12.21 °C, BPF 0.950 |
| 03 – Refrigeration cycle | Chapter 8 – vapour compression | CoolProp P–h cycle, kW and tons, COP, Carnot COP, second-law efficiency, mass flow, pressure ratio, superheat/subcooling sensitivity, refrigerant screen | R134a, **COP 3.976**, compressor 4.82 kW, 0.1296 kg/s |
| 04 – Comfort control | Chapters 3 & 11 – automatic control and comfort | Reduced-order zone model, ET* proxy, 30–70% RH criterion, PID or on/off control of a chilled-water valve or supply-air temperature, KPI comparison | PID: **100%** comfort in final half, 73.20 kWh cooling, 0 switch changes; threshold: 55 switches |

Every module can be used independently from the sidebar. A design change in
Module 1 flows into Module 2 (supply airflow and coil duty), Module 2 into Module 3
(connected cooling capacity), and Module 3 into Module 4 (plant COP). User inputs
are remembered while switching pages; **Reset workspace** restores the complete
default demonstration case.

## Project structure

```
HVAC_Automation_Project/
├── main.py                  Streamlit entry point and page router
├── ui.py                    Design-system widgets, navigation, state, charts helpers
├── i18n.py                  Arabic/English text, markup, table and figure localisation
├── calculations.py          Stable public calculation API for reports/tests
├── locales/
│   ├── ar.py                Arabic labels, sentences, numeric patterns and options
│   ├── ar_charts.py         Arabic chart titles, axes, legends and annotations
│   └── ar_design.py         Arabic text for the quick studio and the design day
├── hvac/
│   ├── psychrometrics.py    ASHRAE moist-air property engine
│   ├── thermal_loads.py     Peak cooling load, components and RSHF
│   ├── quick_design.py      Six answers → load, system size and recommendation
│   ├── day_sim.py           24-hour reduced-order design-day simulation
│   ├── ahu.py               Mixing, supply state, ADP/BPF, heating/humidification
│   ├── refrigeration.py     CoolProp vapour-compression cycle and sweeps
│   ├── controls.py          Zone model, PID/threshold control, comfort KPIs
│   └── charts.py            Psychrometric, load, cycle, control and day figures
├── views/
│   ├── overview.py          Presentation route and system architecture
│   ├── design.py            Quick design and simulation page
│   ├── loads.py             Module 1 page
│   ├── ahu.py               Module 2 page (three tabs)
│   ├── refrigeration.py     Module 3 page
│   └── comfort.py           Module 4 page
├── assets/
│   ├── style.css            Warm-paper / deep-teal visual system
│   ├── design.css           Quick-studio recommendation card and animated day scene
│   ├── theme_dark.css       Dark-theme overlay for cards, inputs, tables and charts
│   ├── rtl.css              Arabic right-to-left layout overlay
│   └── favicon.svg
├── tests/                   92 automated checks (pytest + Streamlit AppTest)
├── qa/                      Bilingual light/dark screenshot matrix and capture script
├── .streamlit/config.toml   Theme and server settings
├── requirements.txt
├── run_app.bat
└── README_AR.md             دليل عربي شامل للمشروع والتشغيل
```

## Engineering method

- **Moist air:** ASHRAE Hyland–Wexler saturation pressure, humidity ratio,
  enthalpy, specific volume, dew point and thermodynamic wet bulb, kept mutually
  consistent at 101.325 kPa.
- **Loads:** steady peak design day. Opaque surfaces use sol-air temperature;
  windows use U-value conduction plus SHGC solar gain and a shading factor.
  People, lighting and equipment gains are explicit. Ventilation and infiltration
  are separate from the room RSHF, which is why the coil SHR (91.6%) differs from
  the room RSHF (91.5%).
- **AHU:** adiabatic three-stream mixing on a dry-air mass basis; supply airflow
  from room sensible load; supply humidity ratio from room latent load; apparatus
  dew point found by intersecting the coil process line with the saturation curve;
  bypass factor from the mixed–supply–ADP geometry.
- **Refrigeration:** CoolProp real-fluid states at evaporating and condensing
  pressures, isentropic efficiency for actual discharge, isenthalpic expansion,
  and superheat/subcooling. COP is compared with the Carnot limit at the same
  saturation temperatures.
- **Quick design:** the same load engine behind a six-answer front end. Presets are
  explicit data (`SPACE_TYPES`, `CITIES`, `ENVELOPE_QUALITY`, `ORIENTATIONS`), the
  geometry is derived from floor area and preset height, and the sizing rules are
  readable in `recommend_system` rather than buried in the interface.
- **Design day:** one air node with thermal and moisture capacitance, ten-minute
  steps, a design-day sine for outdoor dry bulb (peak at 15:00), fixed outdoor
  humidity ratio, orientation-specific solar shapes, occupancy/lighting/equipment
  schedules, two-hour pre-cooling with a ramped setpoint (the pull-down can briefly
  draw more than the afternoon load while it charges the building mass), 28 °C
  night setback, PI control limited by installed sensible capacity, a fixed coil
  SHR for latent removal, ambient/part-load COP and fan energy. Comfort is evaluated
  only when the space is occupied and the plant is available.
- **Control:** lumped zone energy and moisture balance with outdoor temperature
  swing, infiltration and internal gains. PID uses conditional-integration
  anti-windup and derivative on measurement; the threshold controller uses a
  deadband. The comfort index is a transparent ET* teaching proxy,
  `ET* = Tdb + 0.04 (RH − 50)`, plus a 30–70% RH project gate.

## Tests and visual QA

```bat
.venv\Scripts\python.exe -m pytest -q
```

The suite covers psychrometric reference values, load components, coil geometry,
cycle references, controller behaviour, the quick-design sizing rules, the
design-day simulation and its capacity limit, Streamlit page rendering/navigation,
Arabic/RTL localisation, the credit strings and dark-theme persistence.
Latest result: **92 passed**.

`qa/i18n_visual_check.py` uses Playwright with installed Microsoft Edge to capture
the full Arabic/English × light/dark desktop matrix plus a 390 px mobile pass into
`qa/`. It also measures horizontal overflow, slider-thumb containment and
unthemed inputs. `qa/design_interaction_check.py` drives the quick studio end to
end: it scrubs to 03:00, checks the night scene and the pre-cool chart label,
opens the hourly table, downloads the CSV and expands the method notes. Both are
development aids, not application dependencies.

For a full Arabic walkthrough of the interface, modules, method and files, see
[README_AR.md](README_AR.md).

## Scope and limitations

This is a teaching and preliminary-design tool, not a construction-issue or
equipment-selection package.

- Loads are steady peak values; the design-day simulation is a reduced-order
  teaching model, not an annual/hourly energy simulation. It has one zone, one air
  node, a fixed coil SHR and a simple COP correction; ducts, fans, pumps, envelope
  thermal lag and real equipment part-load curves are simplified or excluded.
- Quick-design presets are typical engineering values, not a substitute for the
  project brief. The recommended system follows fixed capacity rules; confirm the
  final selection with a qualified engineer and local code.
- The coil is a lumped ADP/BPF model, not a row-by-row finned-tube selection.
- The refrigeration screen compares thermodynamics only; flammability, GWP,
  lubricant, safety classification and cost must be assessed separately.
- The comfort calculation is an ET* proxy with a humidity gate, not the full
  ASHRAE 55 PMV/PPD method (no clothing, air-speed or metabolic-rate inputs).
- Module 4 uses a deliberately small 10 kW demonstration plant to expose
  controller behaviour; it is not the 19 kW design coil selected in Modules 1–2.
- Results depend on the entered U-values, solar, internal gains and operating
  assumptions; verify them against the project specification before use.

## Curriculum alignment and references

The module sequence follows the course structure supplied for this project:
cooling-load estimating (Chapter 4), moist-air processes and air handling
(Chapters 2–3), vapour-compression refrigeration (Chapter 8), and automatic
control and comfort (Chapters 3 & 11), aligned with Dr. Adnan G. Tuaamah
Al-Hasnawi's air-conditioning and refrigeration curriculum.

- ASHRAE, *Handbook—Fundamentals*, psychrometrics and cooling-load chapters.
- ASHRAE, *Standard 55—Thermal Environmental Conditions for Human Occupancy*
  (used as context; this app implements a teaching proxy, not the full standard).
- Bell, I. H. et al., "Pure and Pseudo-pure Fluid Thermophysical Property
  Evaluation and the Open-Source Thermophysical Property Library CoolProp",
  *Industrial & Engineering Chemistry Research*, 53 (2014), 2498–2508.

For the live demonstration script, speaker roles, exact readings and likely
questions, see [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md).
