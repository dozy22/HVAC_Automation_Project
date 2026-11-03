"""Quick design studio — six answers, a sized system and a design day.

This page is the friendly front door that the detailed curriculum modules
needed: the visitor describes the space, and the studio answers the two
questions that matter first — how much cooling, and by which method — then
plays the hottest day back hour by hour.
"""

from __future__ import annotations

import html
import math

from i18n import st_ar as st

import i18n
import ui
from hvac.charts import (
    day_cooling_chart,
    day_energy_chart,
    day_gain_chart,
    day_humidity_chart,
    day_temperature_chart,
)
from hvac.day_sim import DayResult, simulate_design_day
from hvac.quick_design import (
    AUTO_SYSTEM,
    CITIES,
    ENVELOPE_QUALITY,
    ORIENTATIONS,
    SPACE_TYPES,
    SYSTEM_LABELS,
    QuickDesign,
    QuickInputs,
    build_quick_design,
)


def _t(text: str) -> str:
    return i18n.translate_text(text)


def _sentence(point) -> str:
    """Translate one live recommendation sentence, then interpolate values."""
    return i18n.translate_template(point.template, **point.values)


def _open(page: str) -> None:
    st.session_state["page"] = page


def _phase(hour: float) -> str:
    if hour < 5.0 or hour >= 20.0:
        return "night"
    if hour < 7.5:
        return "dawn"
    if hour < 17.0:
        return "day"
    return "dusk"


def _orb_position(hour: float) -> tuple[float, float]:
    """Place the sun (or moon) on a shallow arc across the scene."""
    if 6.0 <= hour <= 18.0:
        fraction = (hour - 6.0) / 12.0
    else:
        wrapped = (hour - 18.0) % 24.0
        fraction = wrapped / 12.0
    x = 6.0 + 88.0 * fraction
    y = 72.0 - 54.0 * math.sin(math.pi * fraction)
    return x, y


def _window_ratio() -> int:
    return int(round(float(st.session_state.get("qd_glazing", 25.0))))


def _manual_occupants() -> bool:
    return bool(st.session_state.get("qd_manual_occ", False))


def _auto_count() -> int:
    space = st.session_state.get("qd_space", "Office")
    area = float(st.session_state.get("qd_area", 96.0))
    preset = SPACE_TYPES.get(space)
    if preset is None:
        return 1
    return max(1, int(round(area / preset.area_per_person_m2)))


def _hero() -> None:
    st.markdown(
        f"""
<section class="module-hero design-hero" data-index="Q">
<div class="hero-kicker">
<span class="module-label">{html.escape(_t("Quick design studio"))}</span>
<span class="chapter">{html.escape(_t("6 answers"))}</span>
</div>
<h1>{html.escape(_t("Six answers."))}<br><em>{html.escape(_t("A sized system and a design day."))}</em></h1>
<p class="hero-description">{html.escape(_t("Say what the space is, where it is and how it is built. The studio calculates the cooling it needs, recommends the most sensible system and runs the hottest day hour by hour. The detailed engineering modules stay one click away."))}</p>
<div class="hero-facts">
<span class="hero-fact">{html.escape(_t("Inputs"))} <b>{html.escape(_t("6 answers"))}</b></span>
<span class="hero-fact">{html.escape(_t("Physics"))} <b>{html.escape(_t("Chapter-4 load engine"))}</b></span>
<span class="hero-fact">{html.escape(_t("Simulation"))} <b>{html.escape(_t("24 h · 10 min steps"))}</b></span>
<span class="hero-fact">{html.escape(_t("View"))} <b>{html.escape(_t("Arabic · English"))}</b></span>
</div>
</section>
""",
        unsafe_allow_html=True,
    )


def _form() -> None:
    with st.container(border=True):
        ui.panel_title("Tell the studio about the space", "Six answers")
        row_one = st.columns(3, gap="medium")
        with row_one[0]:
            ui.selectbox(
                "Type of space",
                options=list(SPACE_TYPES),
                index=1,
                key="qd_space",
                help="Occupancy density, lighting, equipment, fresh air, infiltration and the daily schedule all follow this choice.",
            )
        with row_one[1]:
            ui.number_input(
                "Floor area (m²)",
                min_value=10.0,
                max_value=4000.0,
                value=96.0,
                step=4.0,
                key="qd_area",
                help="The cooled floor area. Room shape, wall area and roof area are derived from it.",
            )
        with row_one[2]:
            ui.selectbox(
                "City",
                options=list(CITIES),
                index=0,
                key="qd_city",
                help="Sets the outdoor design dry bulb, wet bulb and the day–night swing. Choose Other / custom to enter your own.",
            )

        row_two = st.columns(3, gap="medium")
        with row_two[0]:
            ui.slider(
                "Window area (% of wall)",
                min_value=5,
                max_value=70,
                value=25,
                step=5,
                key="qd_glazing",
                help="Glazed share of the exposed wall. More glass means more daylight and more solar gain.",
            )
        with row_two[1]:
            ui.selectbox(
                "Main window orientation",
                options=list(ORIENTATIONS),
                index=3,
                key="qd_orientation",
                help="The façade that receives the main afternoon or morning sun. West is the harshest in a hot climate.",
            )
        with row_two[2]:
            ui.selectbox(
                "Build quality",
                options=list(ENVELOPE_QUALITY),
                index=1,
                key="qd_envelope",
                help="Wall, roof and window U-values, shading and infiltration follow this choice.",
            )

        space = SPACE_TYPES.get(st.session_state.get("qd_space", "Office"))
        city = CITIES.get(st.session_state.get("qd_city", "Baghdad"))
        envelope = ENVELOPE_QUALITY.get(st.session_state.get("qd_envelope", "Standard"))
        notes = " ".join(
            _t(preset.note) for preset in (space, city, envelope) if preset is not None
        )
        st.caption(
            _t(
                "Height, occupancy, lighting, equipment, fresh air and infiltration follow the space type. "
                "Open the advanced panel only if you need to change them."
            )
            + " "
            + notes
        )

    with st.expander(_t("Fine-tune the assumptions")):
        advanced_one = st.columns(3, gap="medium")
        with advanced_one[0]:
            ui.toggle(
                "Set occupancy manually",
                key="qd_manual_occ",
                help="Off: the studio counts people from the space type and floor area. On: use your own count.",
            )
            if _manual_occupants():
                ui.number_input(
                    "Occupants",
                    min_value=0,
                    max_value=3000,
                    value=_auto_count(),
                    step=1,
                    key="qd_occupants",
                    help="People add both sensible and latent heat and set the fresh-air flow.",
                )
            else:
                st.caption(
                    i18n.translate_template(
                        "Automatic occupancy: {n} people, about one person per {area:.1f} m².",
                        n=_auto_count(),
                        area=SPACE_TYPES.get(
                            st.session_state.get("qd_space", "Office"),
                            SPACE_TYPES["Office"],
                        ).area_per_person_m2,
                    )
                )
        with advanced_one[1]:
            ui.number_input(
                "Indoor setpoint (°C)",
                min_value=20.0,
                max_value=28.0,
                value=24.0,
                step=0.5,
                key="qd_indoor_db",
                help="The dry-bulb temperature the control loop holds while the space is occupied.",
            )
            ui.number_input(
                "Indoor relative humidity (%)",
                min_value=30.0,
                max_value=70.0,
                value=50.0,
                step=5.0,
                key="qd_indoor_rh",
                help="Design indoor moisture condition. It fixes the room humidity ratio and the latent load.",
            )
        with advanced_one[2]:
            ui.selectbox(
                "System preference",
                options=[AUTO_SYSTEM]
                + [SYSTEM_LABELS[key]["name"] for key in SYSTEM_LABELS],
                index=0,
                key="qd_system",
                help="Leave on Auto to let the studio choose from the size and the space type.",
            )
            ui.slider(
                "Selection margin (%)",
                min_value=0,
                max_value=30,
                value=12,
                step=1,
                key="qd_margin",
                help="Spare capacity above the calculated load for duct gain, fan heat and real-world tolerance.",
            )

        if st.session_state.get("qd_city") == "Other / custom":
            custom_one, custom_two = st.columns(2, gap="medium")
            with custom_one:
                ui.number_input(
                    "Custom outdoor dry bulb (°C)",
                    min_value=25.0,
                    max_value=55.0,
                    value=43.0,
                    step=0.5,
                    key="qd_custom_db",
                    help="Peak design outdoor dry-bulb temperature for your site.",
                )
            with custom_two:
                ui.number_input(
                    "Custom outdoor wet bulb (°C)",
                    min_value=5.0,
                    max_value=35.0,
                    value=23.0,
                    step=0.5,
                    key="qd_custom_wb",
                    help="Coincident outdoor wet bulb. It must stay below the dry bulb.",
                )


def _build_inputs() -> QuickInputs:
    return QuickInputs.from_state(st.session_state)


def _answer(design: QuickDesign) -> None:
    load = design.load
    rec = design.recommendation
    ui.section_heading(
        "What the space needs",
        kicker="The answer",
        description=(
            "One calculation gives both the cooling duty and the most sensible way to deliver it. "
            "The recommendation follows size, space type and climate, and keeps a visible safety margin."
        ),
    )
    ui.metric_grid(
        [
            {
                "label": "Required cooling",
                "value": f"{load.design_total_kw:,.1f}",
                "unit": "kW",
                "foot": i18n.translate_template(
                    "{tr:.1f} TR · includes outdoor-air ventilation",
                    tr=load.design_tr,
                ),
                "tone": "terra",
                "help": "Peak coil load at the design condition: room sensible and latent gains plus the fresh-air load.",
            },
            {
                "label": "Recommended system",
                "value": _t(rec.name),
                "unit": "",
                "foot": _t(rec.family),
                "tone": "teal",
                "help": "Rule-based selection from the cooling duty, the space type and the daily operating pattern.",
            },
            {
                "label": "Installed capacity",
                "value": f"{rec.capacity_kw:,.1f}",
                "unit": "kW",
                "foot": i18n.translate_template(
                    "{units} × {unit:.1f} kW · {margin:.0f}% above the load",
                    units=rec.outdoor_units,
                    unit=rec.unit_size_kw,
                    margin=rec.margin_pct,
                ),
                "tone": "ochre",
                "help": "Nominal equipment sizes rounded up to the nearest standard unit, including the selection margin.",
            },
            {
                "label": "Supply airflow",
                "value": f"{rec.airflow_m3h:,.0f}",
                "unit": "m³/h",
                "foot": i18n.translate_template(
                    "Fresh air {oa:,.0f} m³/h · supply ΔT {dt:.0f} K",
                    oa=rec.fresh_air_m3h,
                    dt=rec.supply_dt_k,
                ),
                "tone": "blue",
                "help": "Airflow from the sensible duty and a practical supply-to-room temperature difference.",
            },
        ]
    )

    sensible_share = 100.0 * load.design_sensible_kw / max(1e-9, load.design_total_kw)
    latent_share = 100.0 * load.design_latent_kw / max(1e-9, load.design_total_kw)
    ventilation_share = 100.0 * load.ventilation_total_kw / max(1e-9, load.design_total_kw)
    ui.chip_row(
        [
            ("Sensible", f"{sensible_share:.0f}%"),
            ("Latent", f"{latent_share:.0f}%"),
            ("Outdoor air", f"{ventilation_share:.0f}%"),
            ("Room RSHF", f"{100 * load.room_rshf:.0f}%"),
            ("Occupants", f"{design.occupants}"),
            ("Design day", f"{design.inputs.design_db_c:.0f} °C DB / {design.inputs.design_wb_c:.0f} °C WB"),
        ]
    )

    reason_items = "".join(f"<li>{html.escape(_sentence(point))}</li>" for point in rec.reasons)
    caution_items = "".join(
        f"<li>{html.escape(_sentence(point))}</li>" for point in rec.cautions
    )
    st.markdown(
        f"""
<section class="recommend-card">
<div class="recommend-head">
<div class="recommend-copy">
<div class="rec-eyebrow">{html.escape(_t("Recommended system"))}</div>
<h3>{html.escape(_t(rec.name))}</h3>
<div class="rec-family">{html.escape(_t(rec.family))} · {html.escape(i18n.translate_template("{n} outdoor units", n=rec.outdoor_units))}</div>
<p class="rec-note">{html.escape(_t(rec.note))}</p>
</div>
<div class="rec-badge">
<b>{rec.capacity_kw:,.1f}</b>
<span>{html.escape(_t("kW installed"))}</span>
<small>{html.escape(i18n.translate_template("{margin:.0f}% above the load", margin=rec.margin_pct))}</small>
</div>
</div>
<div class="rec-specs">
<div><span>{html.escape(_t("Cooling load"))}</span><b>{load.design_total_kw:,.1f} kW</b></div>
<div><span>{html.escape(_t("Outdoor units"))}</span><b>{rec.outdoor_units}</b></div>
<div><span>{html.escape(_t("Indoor units"))}</span><b>{rec.indoor_units}</b></div>
<div><span>{html.escape(_t("Unit size"))}</span><b>{rec.unit_size_kw:,.1f} kW</b></div>
<div><span>{html.escape(_t("Nominal capacity"))}</span><b>{rec.capacity_tr:,.1f} TR</b></div>
<div><span>{html.escape(_t("Supply airflow"))}</span><b>{rec.airflow_m3h:,.0f} m³/h</b></div>
<div><span>{html.escape(_t("Fresh air"))}</span><b>{rec.fresh_air_m3h:,.0f} m³/h</b></div>
<div><span>{html.escape(_t("Supply ΔT"))}</span><b>{rec.supply_dt_k:.0f} K</b></div>
<div><span>{html.escape(_t("Rated COP"))}</span><b>{rec.cop_rated:.2f}</b></div>
<div><span>{html.escape(_t("Selection margin"))}</span><b>{rec.margin_pct:.1f}%</b></div>
</div>
<div class="rec-columns">
<div class="rec-why">
<h4>{html.escape(_t("Why this system"))}</h4>
<ul>{reason_items}</ul>
</div>
<div class="rec-watch">
<h4>{html.escape(_t("Before you buy"))}</h4>
<ul>{caution_items}</ul>
</div>
</div>
</section>
""",
        unsafe_allow_html=True,
    )


def _scene(day: DayResult, hour: float) -> str:
    sample = day.at_hour(hour)
    phase = _phase(hour)
    phase_label = {
        "night": _t("Night"),
        "dawn": _t("Dawn"),
        "day": _t("Daylight"),
        "dusk": _t("Dusk"),
    }[phase]
    orb_x, orb_y = _orb_position(hour)
    is_day = 6.0 <= hour <= 18.0
    lit = sample["occupied"]
    system_on = sample["system_on"]
    if not system_on:
        status = _t("System off · night setback")
        tone = "idle"
    elif sample["comfort"]:
        status = _t("Comfort held inside the band")
        tone = "ok"
    elif sample["rh_pct"] < 30.0 or sample["rh_pct"] > 70.0:
        status = _t("Cooling, but humidity is outside the band")
        tone = "warn"
    else:
        status = _t("Pulling the room back to setpoint")
        tone = "warn"

    windows = "".join(
        f'<span class="scene-window{" lit" if lit and 7 <= hour <= 19 else ""}" style="--i:{index};"></span>'
        for index in range(4)
    )
    return f"""
<div class="day-scene phase-{phase}" style="--orb-x:{orb_x:.1f}%;--orb-y:{orb_y:.1f}%;">
<div class="scene-stars"></div>
<div class="scene-orb {"orb-sun" if is_day else "orb-moon"}"></div>
<div class="scene-haze"></div>
<div class="scene-city"></div>
<div class="scene-ground"></div>
<div class="scene-building">
<div class="scene-roof"></div>
<div class="scene-face">{windows}</div>
<div class="scene-unit {"on" if system_on else ""}"><span></span><span></span><span></span></div>
</div>
<div class="scene-readout">
<div class="scene-time-row"><span class="scene-time">{int(round(hour)):02d}:00</span><span class="scene-phase">{html.escape(phase_label)}</span></div>
<div class="scene-temps">
<div><span>{html.escape(_t("Outside"))}</span><b>{sample["outdoor_c"]:.1f} °C</b></div>
<div><span>{html.escape(_t("Inside"))}</span><b>{sample["room_c"]:.1f} °C</b></div>
</div>
<div class="scene-status {tone}"><i></i>{html.escape(status)}</div>
</div>
</div>
"""


def _simulation(day: DayResult) -> None:
    design = day.design
    rec = design.recommendation
    ui.section_heading(
        "The hottest day, hour by hour",
        kicker="Design-day simulation",
        description=(
            "The recommended system is put through a full design day: a sine-shaped outdoor "
            "temperature, orientation-specific solar gain, the real occupancy schedule and a "
            "capacity-limited controller. Scrub the day and watch the room, the load and the meter."
        ),
    )

    summary = st.columns([1.65, 1], gap="medium")
    with summary[1]:
        st.caption(
            _t(
                "Choose an hour to inspect. The scene, the four readings and the hourly table all follow the same time step."
            )
        )
    with summary[0]:
        hour = st.select_slider(
            _t("Scrub through the day"),
            options=list(range(24)),
            value=15,
            format_func=lambda value: f"{value:02d}:00",
            key="qd_hour",
            help="Every reading below is sampled at the chosen hour of the simulated design day.",
        )

    sample = day.at_hour(float(hour))
    st.markdown(_scene(day, float(hour)), unsafe_allow_html=True)

    ui.metric_grid(
        [
            {
                "label": "Outdoor air",
                "value": f"{sample['outdoor_c']:.1f}",
                "unit": "°C",
                "foot": i18n.translate_template(
                    "Design day · {city}", city=_t(design.city.name)
                ),
                "tone": "terra",
                "help": "Outdoor dry-bulb temperature at the selected hour, following the design-day swing.",
            },
            {
                "label": "Room temperature",
                "value": f"{sample['room_c']:.1f}",
                "unit": "°C",
                "foot": i18n.translate_template(
                    "Setpoint {sp:.1f} °C · RH {rh:.0f}%",
                    sp=sample["setpoint_c"],
                    rh=sample["rh_pct"],
                ),
                "tone": "teal",
                "help": "Zone dry-bulb temperature after the thermal capacitance and the controller response.",
            },
            {
                "label": "Cooling delivered",
                "value": f"{sample['cooling_kw']:.1f}",
                "unit": "kW",
                "foot": i18n.translate_template(
                    "{pct:.0f}% of installed capacity",
                    pct=sample["part_load_pct"],
                ),
                "tone": "blue",
                "help": "Total coil duty at this instant, split between sensible and latent removal.",
            },
            {
                "label": "Electric demand",
                "value": f"{sample['electric_kw']:.2f}",
                "unit": "kW",
                "foot": _t("Compressor and fan"),
                "tone": "ochre",
                "help": "Compressor power after the ambient and part-load corrections, plus the fan share.",
            },
        ]
    )

    ui.chip_row(
        [
            (
                "Peak load",
                i18n.translate_template(
                    "{kw:.1f} kW at {hour:02d}:00",
                    kw=day.peak_cooling_kw,
                    hour=int(round(day.peak_hour)),
                ),
                "terra",
            ),
            ("Comfort while occupied", f"{day.occupied_comfort_pct:.0f}%", "green"),
            ("Electricity", f"{day.electric_energy_kwh:.1f} kWh", "ochre"),
            ("Day COP", f"{day.day_cop:.2f}", "teal"),
            ("System on", f"{day.system_on_hours:.1f} h", ""),
        ]
    )

    ui.section_heading(
        "Five views of the same day",
        kicker="Charts",
        description=(
            "Temperature and control first, then the cooling duty, the gains that create it, "
            "the moisture result and the electricity that pays for it."
        ),
    )
    ui.plot(day_temperature_chart(day), key="qd_chart_temperature")
    left, right = st.columns(2, gap="medium")
    with left:
        ui.plot(day_cooling_chart(day), key="qd_chart_cooling")
    with right:
        ui.plot(day_gain_chart(day), key="qd_chart_gains")
    left_two, right_two = st.columns(2, gap="medium")
    with left_two:
        ui.plot(day_humidity_chart(day), key="qd_chart_humidity")
    with right_two:
        ui.plot(day_energy_chart(day), key="qd_chart_energy")

    with st.expander(_t("Hour-by-hour results and export")):
        frame = day.hourly_frame()
        display = frame.copy()
        display["Occupied"] = frame["Occupied"].map(lambda value: _t("Yes") if value else _t("No"))
        display["Comfortable"] = frame["Comfortable"].map(
            lambda value: _t("Yes") if value else _t("No")
        )
        ui.show_table(
            display,
            height=380,
            formats={
                "Outdoor DB (degC)": "%.1f",
                "Room DB (degC)": "%.2f",
                "Setpoint (degC)": "%.1f",
                "RH (%)": "%.1f",
                "Cooling (kW)": "%.2f",
                "Capacity (kW)": "%.1f",
                "Electric demand (kW)": "%.2f",
            },
        )
        ui.download_csv(
            frame,
            filename="hvac_design_day.csv",
            label="Download the 24-hour simulation (CSV)",
            key="qd_download_day",
            help_text="Every hourly sample with temperatures, cooling, capacity, electricity and comfort flags.",
        )

    if day.unmet_hours > 0.5:
        ui.callout(
            "What the day is telling you",
            i18n.translate_template(
                "The room spends about {hours:.1f} hour(s) more than 0.5 K above setpoint while occupied. "
                "That is the honest limit of the installed capacity, not a calculation error. "
                "Extra capacity, better glazing or a tighter schedule would close the gap.",
                hours=day.unmet_hours,
            ),
            tone="ochre",
        )
    else:
        ui.callout(
            "What the day is telling you",
            i18n.translate_template(
                "The selected system holds the room at setpoint through every occupied hour, with {headroom:.0f}% headroom at the peak. "
                "The morning ramp and the night setback are visible in the temperature chart: that is the thermal inertia of the room, not a control fault.",
                headroom=max(0.0, day.headroom_pct),
            ),
            tone="teal",
        )

    with st.expander(_t("How this simulation works")):
        st.markdown(
            """
**The load.** Six answers are expanded into the full Chapter-4 input set: geometry from the floor area, occupancy and internal gains from the space type, and envelope values from the build quality. The same engine as Module 1 calculates the peak.

**The day.** Outdoor dry bulb follows a sine that peaks at 15:00, solar gain follows the main window orientation, and the selected system modulates against its installed capacity. The room has thermal and moisture inertia, so morning pull-down, night setback and the afternoon peak all emerge from the model.

**The limits.** This is a single-zone teaching model with a fixed coil sensible heat ratio and a simple ambient COP correction. It is not an hourly energy-compliance simulation. Use it to understand behaviour, then confirm the design with the detailed modules.
"""
        )

    next_steps = st.columns([1, 1], gap="medium")
    with next_steps[0]:
        st.button(
            _t("Open the detailed cooling-load module"),
            on_click=_open,
            args=(ui.PAGE_LOADS,),
            width="stretch",
            help=_t("Recalculate the same case from every envelope, solar and occupancy input."),
        )
    with next_steps[1]:
        st.button(
            _t("Open the psychrometric AHU module"),
            on_click=_open,
            args=(ui.PAGE_AHU,),
            width="stretch",
            help=_t("See the coil process, apparatus dew point and bypass factor for this air state."),
        )


def render() -> None:
    _hero()
    _form()
    ui.remember_inputs("qd_")

    try:
        design = build_quick_design(_build_inputs())
        day = simulate_design_day(design)
    except Exception as exc:  # pragma: no cover - exercised through the UI
        st.session_state["quick_design"] = None
        st.session_state["day_result"] = None
        ui.error_block(
            exc,
            "Check the floor area, the glazing ratio and the custom design temperatures.",
        )
        ui.page_footer()
        return

    st.session_state["quick_design"] = design
    st.session_state["day_result"] = day

    _answer(design)
    _simulation(day)
    ui.page_footer()
