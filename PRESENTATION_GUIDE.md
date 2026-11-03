# Live presentation guide

**One connected case · a quick studio · four speakers · about 17 minutes**

The story is a single 96 m² classroom: the room load sizes the coil, the coil duty
sizes the refrigeration cycle, and the cycle COP feeds the comfort controller.
A six-answer quick studio at the front shows the whole idea in two minutes, then
the four detailed modules prove the same physics layer by layer. Each speaker owns
one layer and hands a number to the next speaker.

## Before the professor arrives

1. Open the app at <http://localhost:8501> (or double-click `run_app.bat`).
2. Click **Reset workspace** at the bottom of the sidebar. All pages then show the
   default case and the numbers in this guide. Reset keeps your language and
   light/dark choice.
3. Open **Design & simulation** once before the talk and scrub the hour slider to
   15:00, to confirm the scene and the five charts render on the projector.
3. Choose the presentation language once, before you start: **العربية** (default)
   or **English** in the sidebar. Calculations are identical in both. If you switch
   mid-talk the page re-labels instantly; allow one redraw before speaking.
4. Choose **الوضع الداكن / Dark mode** if the room is dim or the projector washes
   out light backgrounds. The light theme is the safer choice in a bright room.
5. Use a 100% browser zoom and a maximised window. The sidebar must stay visible
   so the audience can follow the hand-offs.
6. Do not edit inputs until the presenter reaches the planned live-action step.
   Streamlit recalculates in about 1–3 seconds; wait for the result before
   speaking the next number.
7. Keep the final QA screenshots in `qa/` open in another window as a backup:
   `final_ar_light_overview.png` (or `final_en_light_overview.png`), the design
   page, and the four module images in the same language/theme.
8. If anything looks wrong, click **Reset workspace** and start again from the
   Overview page.

**The 30-second opening (Speaker 1):** "This is one design case, not four
calculators. Six client answers size the cooling and the system, then the room
load becomes a supply-air state, the supply-air state becomes a coil load, the
coil load becomes a refrigeration cycle, and the cycle COP closes the control
loop. Every number on screen is calculated from the one classroom case."

## The default numbers to quote

| Stage | Reading |
| --- | --- |
| Quick studio load | **18.83 kW**; Office, 96 m², Baghdad, 25% glazing, west, standard envelope, 11 occupants |
| Quick studio system | **VRF multi-split, 2 × 12.5 kW = 25 kW** installed, 18.5% margin; 6150 m³/h supply, 396 m³/h fresh air |
| Quick studio design day | Peak load **17.7 kW at 15:00**; 100% comfort while occupied; 190.9 kWh cooling / 72.8 kWh electricity; day COP 2.62. The 05:20 pre-cool pull-down briefly draws 23.7 kW |
| Room sensible / latent | 12.83 kW / 1.19 kW |
| Room RSHF | 91.5% |
| Outdoor ventilation load | 4.71 kW sensible + 0.43 kW latent = 5.13 kW |
| Design cooling load | **19.16 kW (5.45 TR)**; sensible 17.54 kW, latent 1.62 kW |
| Coil total / SHR | **19.17 kW / 91.6%** |
| ADP / bypass factor | 12.21 °C / 0.950 (contact factor 0.050) |
| Supply air | 13.0 °C DB, 12.56 °C WB, 95.2% RH, 1.140 kg/s (3374 m³/h) |
| Cycle | R134a, 2 °C evaporating, 45 °C condensing, 5 K superheat, 5 K subcooling, 75% isentropic |
| Cycle performance | **COP 3.976**; Carnot 6.399; second-law 62.1%; compressor 4.82 kW; condenser 23.99 kW; refrigerant 0.1296 kg/s |
| Cycle temperatures | Discharge 62.65 °C (isentropic 54.2 °C); subcooled liquid 40 °C |
| Comfort run | PID, valve, 10 kW rated sensible, 8 h, setpoint 24.5 °C |
| PID result | **100%** comfort in final half; final 24.50 °C / 39.9% RH; 73.20 kWh cooling; 18.41 kWh electricity; 0 switch changes |
| Threshold comparison | 100% comfort; 73.25 kWh; 18.42 kWh; **55 switch changes** |

## Opening — the quick studio (2 minutes)

**Open:** **Design & simulation** from the sidebar (or the **Open the quick studio**
button on the Overview page).

**Show:** the six answers, the four KPI cards, the recommendation card, then the
day scene and the five charts at 15:00.

**Say:**

- "Before the detailed engineering, the studio asks only what a client knows: the
  kind of space, its area, the city, how much glass, which way it faces and how
  well it is built. Six answers."
- "The same Chapter-4 engine used later in Module 1 turns those answers into
  **18.83 kW** of cooling. Nothing here is a separate shortcut calculation."
- "The rule selects a **VRF multi-split, two 12.5 kW outdoor units**, a 12% safety
  margin, 6150 m³/h of supply air and 396 m³/h of fresh air. The card explains why,
  and what to check before buying."
- "Then it runs the hottest day at ten-minute steps. The design-load peak is
  **17.7 kW at 15:00**; the taller spike before 06:00 is the pre-cool pull-down
  charging the building mass, and the chart names it. The room stays inside the
  comfort band through every occupied hour, and the day uses 190.9 kWh of cooling
  and 72.8 kWh of electricity at a day COP of 2.62."
- "Drag the hour slider: the scene, the four readings and the table all follow. This
  is the part a client remembers."

**Live action (20 seconds):** change **Floor area** from 96 to 180 m² and let the
load and the system size update. Change it back. Do not read a new number aloud
until the page finishes redrawing.

**Hand-off:** "That is the quick answer. Now the four speakers open the same case
layer by layer, starting with the load itself." Click **Reset workspace**, then
open **01 – Cooling load**.

## Speaker 1 — Cooling load (Chapter 4)

**Open:** Overview page, then **01 – Cooling load**.

**Show:** the four KPI cards, the three input columns, and the component bar
chart. Point to the live-case badge in the sidebar: 96 m², 20 people, 720 m³/h.

**Say:**

- "We start with a 12 × 8 × 3.2 m classroom with 96 m² floor area and 20 occupants.
  The design day is 45 °C DB / 24 °C WB outside and 24 °C / 50% RH inside."
- "The envelope is a brick wall with 50 mm insulation, a concrete roof with 75 mm
  insulation, and double low-e glazing. Solar hits the west facade in the
  afternoon, so the window load is dominant."
- "The room itself needs 12.83 kW sensible and 1.19 kW latent. That gives an RSHF
  of 91.5% — this is a mostly sensible room."
- "Outdoor ventilation at 10 L/s per person adds 4.71 kW sensible and 0.43 kW
  latent. The design coil load is therefore 19.16 kW, or 5.45 tons of
  refrigeration, with a coil SHR of 91.6%."
- "The RSHF and the coil SHR are close but not identical because RSHF uses room
  gains only, while the coil also has to condition the outdoor air."

**Live action (optional, 20 seconds):** change **Outdoor DB** from 45.00 to
48.00, press Enter, and let the load rise. Say "hotter design day, thicker coil
duty." Restore 45.00 and press Enter. Do not read a new number aloud unless you
wait for it.

**Hand-off:** "The room load is now fixed. Speaker 2 turns it into a supply-air
state and a coil duty."

## Speaker 2 — Psychrometrics and AHU (Chapters 2–3)

**Open:** **02 – Psychrometrics & AHU**, tab **Cooling & dehumidification**.

**Show:** the coil KPI cards first, then the psychrometric chart, then the two
state-point tables. Use the pointer to follow OA → MA → SA.

**Say:**

- "The AHU takes 19.2% outdoor air by mass, mixes it adiabatically with return
  air, cools and dehumidifies it, and delivers 13 °C supply air."
- "Outdoor air is 45 °C / 24 °C WB. Return air is 24 °C / 50% RH. The mixed point
  is 28.03 °C / 40% RH. The supply point is 13 °C / 95.2% RH at 1.140 kg/s."
- "The coil load is 19.17 kW with a sensible heat ratio of 91.6%. The apparatus
  dew point is 12.21 °C: that is the effective coil-surface condition where the
  process line meets the saturation curve."
- "The bypass factor is 0.950. A high bypass factor means only 5% of the air
  effectively reaches the ADP condition; this coil is shallow relative to the
  duty. It is a teaching result, not a manufacturer's selection."
- "The chart is drawn to scale: the room RSHF line sets the supply-state
  direction, and the coil line runs from the mixed state toward the ADP."

**Live action (20 seconds):** move **Supply-air dry-bulb** from 13.0 to 12.5 °C.
Point out that the airflow falls and the coil has to dehumidify further; move it
back to 13.0 °C. Then open **Heating & humidification** briefly: 12 °C / 60% RH
in, 22 °C / 55% RH out, 0.5 kg/s, 5.08 kW sensible heat and 6.93 kg/h steam.
Return to **Cooling & dehumidification** before handing over.

**Hand-off:** "The coil duty of 19.17 kW is the cooling capacity that Speaker 3
must produce."

## Speaker 3 — Vapour-compression cycle (Chapter 8)

**Open:** **03 – Refrigeration cycle**.

**Show:** the two rows of KPI cards, then the P–h diagram, then the state-point
and performance tables.

**Say:**

- "The cycle is sized from the connected Module 2 coil load, 19.17 kW. The
  refrigerant is R134a, evaporating at 2 °C and condensing at 45 °C, with 5 K
  superheat, 5 K subcooling and 75% isentropic efficiency."
- "State 1 is superheated suction vapour. 1 → 2 is compression, 2 → 3 is
  condensation, 3 → 4 is isenthalpic expansion. The actual discharge is 62.65 °C;
  the ideal isentropic endpoint would be 54.2 °C."
- "The compressor uses 4.82 kW and rejects 23.99 kW at the condenser. Refrigerant
  mass flow is 0.1296 kg/s. COP is 3.976."
- "The Carnot ceiling at the same saturation temperatures is 6.399, so the
  second-law efficiency is 62.1%. The gap is the real-fluid behaviour plus the
  75% isentropic efficiency."
- "Subcooling from 0 to 24 K raises COP by about 25% and lowers mass flow by about
  20%, because each kilogram of refrigerant produces more refrigeration effect.
  Superheat protects the compressor but lowers suction density and raises
  discharge temperature."

**Live action (20 seconds):** in the sensitivity section, click **Superheat**
and show the discharge-temperature curve, then return to **Subcooling**. Do not
change the design inputs; the sweep is a diagnostic, not a new design point.

**Hand-off:** "COP 3.976 is the plant efficiency that Speaker 4 uses to estimate
electricity in the comfort loop."

## Speaker 4 — Comfort and automatic control (Chapters 3 & 11)

**Open:** **04 – Comfort control**.

**Show:** the control panel, the KPI cards, the three timeline charts, and the
PID-versus-threshold table.

**Say:**

- "This is a reduced-order zone model, not a second load calculation. The plant is
  deliberately rated at 10 kW sensible so we can see pull-down and part-load
  behaviour. It is not the 19 kW design coil."
- "The room starts at 28.8 °C and 55% RH on a hot afternoon. The setpoint is
  24.5 °C for 8 hours. The PID controller commands the chilled-water valve."
- "The final condition is 24.50 °C and 39.9% RH, with 100% comfort in the final
  half of the run. The controller held the setpoint within 0.25 K."
- "The comfort index is an ET* teaching proxy, dry-bulb plus 0.04 times the
  deviation of RH from 50%, with a 30–70% RH project gate. At 24.5 °C / 40% RH the
  proxy is about 24.1 °C, comfortably inside the 23–26 °C band."
- "PID delivers 73.20 kWh of cooling for 18.41 kWh of electricity and makes no
  switching changes. The on/off controller delivers almost the same energy,
  73.25 kWh, but switches 55 times. The comparison is about stability and actuator
  wear, not a guaranteed energy saving."

**Live action (20 seconds):** switch the controller to **Threshold (on/off)**.
Point to the square-wave valve trace and 55 switch changes; switch back to **PID**.
Optionally raise the setpoint to 25.5 °C and note that the final temperature
follows, then restore 24.5 °C.

**Close:** return to **Overview**. "Four layers, one case: 19.16 kW of room load
became a 19.17 kW coil, a COP of 3.976, and a controlled 24.5 °C room."

## Likely professor questions

**Why does the quick studio say 18.83 kW while the detailed Module 1 says 19.16 kW?**
Different presets, same engine. The quick studio uses 11 occupants for a 96 m²
office, a 46 °C Baghdad design day and standard envelope defaults; the detailed
module's teaching case uses 20 occupants and 45 °C. Feed the quick studio's
`LoadInputs` into `calculate_thermal_load` and the two results are identical to the
digit.

**How does the studio choose the system?**
A readable capacity rule: split up to 7.5 kW; ducted packaged units for open plans
up to 60 kW; VRF up to 100 kW; air-cooled chiller + AHU above that. A nominal size
table is applied with the margin (12% by default), then the page reports the unit
count, airflow, fresh air, COP and the reasons and cautions. A fixed preference in
the fine-tune panel overrides the rule.

**Is the design-day simulation a real energy simulation?**
No. It is a reduced-order teaching model: one zone, one air node, ten-minute steps,
a fixed coil SHR, a simple ambient/part-load COP and no duct, fan-system or
envelope-lag detail beyond the fan power term. It is honest about behaviour — peak,
pull-down, night setback, comfort and energy — but it is not an hourly
energy-compliance tool.

**Why is the design load 19.16 kW but the coil 19.17 kW?**
Independent rounding and two routes to the same result. The room-plus-outdoor
component sum is 19.15 kW, the steady design estimate is 19.16 kW, and the
psychrometric coil path is 19.17 kW. The difference is 0.01 kW, well below the
precision of the input assumptions.

**Why is the coil SHR 91.6% when the room RSHF is 91.5%?**
RSHF contains room gains only. The coil also conditions outdoor air, which has a
different sensible/latent split, so the coil SHR is close but not identical.

**Why is the bypass factor 0.95?**
It follows from the mixed–supply–ADP geometry for this mostly sensible load. A
BPF of 0.95 means a contact factor of 0.05, i.e. a shallow/high-bypass coil in
this teaching model. A real selection would come from coil rows, fin spacing,
face velocity and manufacturer data.

**What is the difference between ADP and dew point?**
The apparatus dew point is the effective saturated coil-surface temperature found
by extending the coil process line to the saturation curve. The supply-air dew
point is a property of the leaving air. Here both are near 12.2 °C because the
supply air is close to saturation at 95.2% RH.

**Why is COP only 3.976 when Carnot is 6.399?**
The Carnot value is reversible operation between the same saturation
temperatures. The real cycle uses R134a properties, 75% isentropic efficiency and
finite temperature differences, giving a second-law efficiency of 62.1%.

**Why does subcooling improve COP but reduce refrigerant mass flow?**
Subcooling lowers the enthalpy entering the expansion valve, so each kilogram
produces more refrigeration in the evaporator. The compressor work per kilogram
is essentially unchanged at fixed pressures, so COP rises and the mass flow
needed for 19.17 kW falls.

**Why does more superheat raise discharge temperature?**
The suction vapour starts further from saturation and has a lower density. The
compressor must work on a hotter, thinner gas; the outlet temperature rises and
the mass flow for a given capacity changes.

**Why do PID and on/off use almost the same energy?**
Both run the same 8-hour load with the same plant and weather. The model does not
include compressor cycling efficiency penalties or start-up transients. The
meaningful difference shown is 0 switching versus 55 switching changes; the
energy comparison is deliberately honest rather than claiming a savings that the
model cannot prove.

**Why is the peak total coil 21.8 kW if the plant is rated 10 kW?**
The 10 kW rating is the sensible capacity. The plotted peak is total coil load,
sensible plus latent. During the humid pull-down the wet coil removes a large
latent load, so the total momentarily exceeds the sensible rating. The model caps
sensible capacity, not the sum.

**Is the comfort result ASHRAE 55?**
No. ET* is a transparent humidity-adjusted teaching proxy, and 30–70% RH is the
project criterion from the brief. Full ASHRAE 55 would require PMV/PPD with
clothing, metabolic rate, air speed and radiant temperature. The app labels this
limitation on the page.

**Why does the room finish at 39.9% RH rather than 50%?**
The controller regulates temperature only. The wet coil removes moisture while
pulling the room down, and this cooling-mode model has no rehumidifier. The final
RH remains inside the 30–70% comfort gate.

**Why does the valve trace start at 100% and then fall?**
The room starts 4.3 K above setpoint, so PID saturates the valve during pull-down.
As the error falls, the controller throttles back and the anti-windup logic stops
the integral term from overcharging.

**Which refrigerant is best?**
The expander can screen six fluids at the same operating point. At these
conditions R134a gives the highest COP, about 3.98; R32 needs lower mass flow but
has a much higher discharge temperature, and R290 also performs well
thermodynamically. The screen explicitly ignores flammability, GWP, lubricant and
safety classification, so it cannot pick a "best" refrigerant by itself.

## If something goes wrong

- **Wrong numbers on screen:** click **Reset workspace**, wait for the overview
  to reload, then continue from the planned page.
- **A module shows an error:** do not keep clicking. Read the red message, reset
  the workspace, and reopen the module. The default case is designed to be valid.
- **Server stopped:** close the console and double-click `run_app.bat` again.
  The browser address is <http://localhost:8501>.
- **No browser opened:** open a browser manually and enter the address.
- **Need to verify the build:** run
  `.venv\Scripts\python.exe -m pytest -q`; the expected result is **92 passed**.
- **Language looks mixed for a second:** Streamlit is redrawing; wait for the
  spinner to finish. The switch does not recalculate the design.
- **Backup:** the final matrix lives in `qa/` as
  `final_ar_light_*.png`, `final_ar_dark_*.png`, `final_en_light_*.png` and
  `final_en_dark_*.png` (`overview`, `design`, `loads`, `ahu`, `refrigeration`,
  `comfort`), plus `final_ar_mobile_overview.png`.

## Suggested timing

| Minute | Speaker | Content |
| --- | --- | --- |
| 0:00–0:30 | 1 | Opening and the connected-case idea |
| 0:30–2:30 | 1 | Quick studio: six answers, recommendation, design day |
| 2:30–3:00 | 1 | Reset, then the detailed load build-up |
| 3:00–6:00 | 1 | Module 1 load build-up and RSHF |
| 6:00–6:20 | 1 → 2 | Hand-off: room load to supply air |
| 6:20–10:00 | 2 | Mixing, ADP/BPF, coil duty, chart |
| 10:00–10:20 | 2 → 3 | Hand-off: coil duty to refrigeration |
| 10:20–14:00 | 3 | Cycle states, COP, sensitivity |
| 14:00–14:20 | 3 → 4 | Hand-off: COP to control |
| 14:20–17:00 | 4 | Comfort loop, PID vs threshold, close |
| 17:00+ | all | Questions; use the table above |
