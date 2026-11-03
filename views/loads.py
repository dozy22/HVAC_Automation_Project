"""Module 1 — peak cooling-load calculation."""

from __future__ import annotations

from i18n import st_ar as st

import ui
from hvac.charts import load_breakdown_chart
from hvac.thermal_loads import (
    ACTIVITY_PROFILES,
    GLAZING_OPTIONS,
    ROOF_OPTIONS,
    WALL_OPTIONS,
    WALL_SOLAR_OPTIONS,
    WEATHER_PRESETS,
    LoadInputs,
    calculate_thermal_load,
)

MODULE_FACTS = (
    ("Deliverable", "RSH · RLH · RSHF"),
    ("Method", "Sol-air envelope"),
    ("Hand-off", "Room states → Module 2"),
)


def _apply_wall_material() -> None:
    selected = st.session_state.get("m1_wall_material")
    if selected in WALL_OPTIONS:
        st.session_state["m1_wall_u"] = WALL_OPTIONS[selected]["u"]
        st.session_state["m1_wall_abs"] = WALL_OPTIONS[selected]["absorptivity"]


def _apply_roof_material() -> None:
    selected = st.session_state.get("m1_roof_material")
    if selected in ROOF_OPTIONS:
        st.session_state["m1_roof_u"] = ROOF_OPTIONS[selected]["u"]
        st.session_state["m1_roof_abs"] = ROOF_OPTIONS[selected]["absorptivity"]


def _apply_glazing() -> None:
    selected = st.session_state.get("m1_glazing")
    if selected in GLAZING_OPTIONS:
        st.session_state["m1_window_u"] = GLAZING_OPTIONS[selected]["u"]
        st.session_state["m1_shgc"] = GLAZING_OPTIONS[selected]["shgc"]


def _apply_weather_preset() -> None:
    selected = st.session_state.get("m1_weather_preset", "Custom")
    preset = WEATHER_PRESETS.get(selected, {})
    if preset:
        st.session_state["m1_outdoor_db"] = preset["db_c"]
        st.session_state["m1_outdoor_wb"] = preset["wb_c"]


def _apply_facade() -> None:
    selected = st.session_state.get("m1_facade")
    if selected in WALL_SOLAR_OPTIONS:
        st.session_state["m1_wall_solar"] = WALL_SOLAR_OPTIONS[selected]


def _build_inputs() -> LoadInputs:
    return LoadInputs(
        project_name=st.session_state.get("m1_project", "HVAC design studio"),
        length_m=float(st.session_state.get("m1_length", 12.0)),
        width_m=float(st.session_state.get("m1_width", 8.0)),
        height_m=float(st.session_state.get("m1_height", 3.2)),
        exposed_wall_fraction=float(st.session_state.get("m1_exposed", 0.80)),
        wall_u_w_m2k=float(st.session_state.get("m1_wall_u", 0.55)),
        wall_absorptivity=float(st.session_state.get("m1_wall_abs", 0.65)),
        roof_u_w_m2k=float(st.session_state.get("m1_roof_u", 0.35)),
        roof_absorptivity=float(st.session_state.get("m1_roof_abs", 0.75)),
        window_u_w_m2k=float(st.session_state.get("m1_window_u", 1.60)),
        window_shgc=float(st.session_state.get("m1_shgc", 0.40)),
        window_area_m2=float(st.session_state.get("m1_window_area", 18.0)),
        shading_factor=float(st.session_state.get("m1_shading", 0.85)),
        wall_solar_w_m2=float(st.session_state.get("m1_wall_solar", 600.0)),
        roof_solar_w_m2=float(st.session_state.get("m1_roof_solar", 950.0)),
        outdoor_film_w_m2k=float(st.session_state.get("m1_film", 20.0)),
        outdoor_db_c=float(st.session_state.get("m1_outdoor_db", 45.0)),
        outdoor_wb_c=float(st.session_state.get("m1_outdoor_wb", 24.0)),
        indoor_db_c=float(st.session_state.get("m1_indoor_db", 24.0)),
        indoor_rh_pct=float(st.session_state.get("m1_indoor_rh", 50.0)),
        pressure_kpa=float(st.session_state.get("m1_pressure", 101.325)),
        occupants=int(st.session_state.get("m1_occupants", 20)),
        activity_key=st.session_state.get("m1_activity", "Office work"),
        lighting_w_m2=float(st.session_state.get("m1_lighting", 8.0)),
        equipment_w=float(st.session_state.get("m1_equipment", 1500.0)),
        infiltration_ach=float(st.session_state.get("m1_infiltration", 0.50)),
        ventilation_l_s_person=float(st.session_state.get("m1_ventilation", 10.0)),
    )


def render() -> None:
    ui.page_header(
        index="01",
        module_label="Thermal load calculation",
        chapter="Chapter 4 · Load estimating",
        title="Cooling load",
        accent="calculation",
        description=(
            "Build the peak design case from the envelope outward. Room sensible and latent "
            "gains, ventilation air and the resulting room sensible heat factor are evaluated "
            "together so the psychrometric design stays honest."
        ),
        facts=MODULE_FACTS,
    )
    kpi_slot = st.empty()

    st.markdown(
        '<div class="eyebrow" style="margin-bottom:0.55rem;">Design inputs</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        with st.container(border=True):
            ui.panel_title("Space & ventilation", "Zone definition")
            ui.text_input(
                "Project / room name",
                value="HVAC design studio",
                key="m1_project",
                help="Used on the exported calculation record and in the sidebar.",
            )
            d1, d2 = st.columns(2)
            with d1:
                ui.number_input(
                    "Length (m)",
                    min_value=3.0,
                    max_value=45.0,
                    value=12.0,
                    step=0.5,
                    key="m1_length",
                    help="Internal room length. The floor area is used for roof, lighting and occupancy gains.",
                )
            with d2:
                ui.number_input(
                    "Width (m)",
                    min_value=3.0,
                    max_value=35.0,
                    value=8.0,
                    step=0.5,
                    key="m1_width",
                    help="Internal room width.",
                )
            d3, d4 = st.columns(2)
            with d3:
                ui.number_input(
                    "Height (m)",
                    min_value=2.4,
                    max_value=6.0,
                    value=3.2,
                    step=0.1,
                    key="m1_height",
                    help="Floor-to-ceiling height; sets the room volume and infiltration flow.",
                )
            with d4:
                ui.number_input(
                    "Exposed wall fraction",
                    min_value=0.10,
                    max_value=1.00,
                    value=0.80,
                    step=0.05,
                    key="m1_exposed",
                    help="Fraction of the perimeter wall exposed to outdoor conditions.",
                )
            ui.slider(
                "Occupants",
                min_value=0,
                max_value=120,
                value=20,
                step=1,
                key="m1_occupants",
                help="People contribute both sensible and latent heat; the count also fixes ventilation airflow.",
            )
            s1, s2 = st.columns(2)
            with s1:
                ui.number_input(
                    "Ventilation (L/s·person)",
                    min_value=0.0,
                    max_value=40.0,
                    value=10.0,
                    step=0.5,
                    key="m1_ventilation",
                    help="Outdoor-air ventilation rate per person. This becomes the coil outdoor-air load.",
                )
            with s2:
                ui.number_input(
                    "Infiltration (ACH)",
                    min_value=0.0,
                    max_value=3.0,
                    value=0.50,
                    step=0.05,
                    key="m1_infiltration",
                    help="Air changes per hour through the envelope. This is an additional untempered load.",
                )

    with c2:
        with st.container(border=True):
            ui.panel_title("Envelope & glazing", "Opaque + transparent")
            ui.selectbox(
                "Wall construction",
                options=list(WALL_OPTIONS),
                index=1,
                key="m1_wall_material",
                on_change=_apply_wall_material,
                help="Selecting a construction updates the default U-value and solar absorptivity.",
            )
            w1, w2 = st.columns(2)
            with w1:
                ui.number_input(
                    "Wall U (W/m²·K)",
                    min_value=0.10,
                    max_value=3.00,
                    value=0.55,
                    step=0.05,
                    key="m1_wall_u",
                    help="Overall wall heat-transfer coefficient. Override the material default when you have a project value.",
                )
            with w2:
                ui.number_input(
                    "Wall absorptivity",
                    min_value=0.10,
                    max_value=1.00,
                    value=0.65,
                    step=0.05,
                    key="m1_wall_abs",
                    help="Solar absorptivity used in the sol-air temperature calculation.",
                )
            ui.selectbox(
                "Roof construction",
                options=list(ROOF_OPTIONS),
                index=2,
                key="m1_roof_material",
                on_change=_apply_roof_material,
                help="Roof U-value and absorptivity are set by this selection.",
            )
            r1, r2 = st.columns(2)
            with r1:
                ui.number_input(
                    "Roof U (W/m²·K)",
                    min_value=0.10,
                    max_value=3.00,
                    value=0.35,
                    step=0.05,
                    key="m1_roof_u",
                    help="Overall roof heat-transfer coefficient.",
                )
            with r2:
                ui.number_input(
                    "Roof absorptivity",
                    min_value=0.10,
                    max_value=1.00,
                    value=0.75,
                    step=0.05,
                    key="m1_roof_abs",
                    help="Solar absorptivity used in the roof sol-air temperature.",
                )
            ui.selectbox(
                "Glazing type",
                options=list(GLAZING_OPTIONS),
                index=2,
                key="m1_glazing",
                on_change=_apply_glazing,
                help="Selecting glass updates its U-value and solar heat gain coefficient (SHGC).",
            )
            g1, g2 = st.columns(2)
            with g1:
                ui.number_input(
                    "Window U (W/m²·K)",
                    min_value=0.30,
                    max_value=8.00,
                    value=1.60,
                    step=0.10,
                    key="m1_window_u",
                    help="Glazing conduction coefficient.",
                )
            with g2:
                ui.number_input(
                    "SHGC (–)",
                    min_value=0.05,
                    max_value=1.00,
                    value=0.40,
                    step=0.02,
                    key="m1_shgc",
                    help="Solar heat gain coefficient: the fraction of incident solar radiation admitted.",
                )
            g3, g4 = st.columns(2)
            with g3:
                ui.number_input(
                    "Window area (m²)",
                    min_value=0.0,
                    max_value=100.0,
                    value=18.0,
                    step=1.0,
                    key="m1_window_area",
                    help="Total glazed area; must not exceed the exposed opaque wall area.",
                )
            with g4:
                ui.number_input(
                    "Shading factor (–)",
                    min_value=0.0,
                    max_value=1.00,
                    value=0.85,
                    step=0.05,
                    key="m1_shading",
                    help="1.00 is unshaded; lower values represent blinds, overhangs or external shading.",
                )

    with c3:
        with st.container(border=True):
            ui.panel_title("Environment & activity", "Design conditions")
            ui.selectbox(
                "Weather preset",
                options=list(WEATHER_PRESETS),
                index=0,
                key="m1_weather_preset",
                on_change=_apply_weather_preset,
                help="Illustrative teaching conditions, not a weather-file design day.",
            )
            e1, e2 = st.columns(2)
            with e1:
                ui.number_input(
                    "Outdoor DB (°C)",
                    min_value=20.0,
                    max_value=55.0,
                    value=45.0,
                    step=0.5,
                    key="m1_outdoor_db",
                    help="Peak outdoor dry-bulb design temperature.",
                )
            with e2:
                ui.number_input(
                    "Outdoor WB (°C)",
                    min_value=5.0,
                    max_value=38.0,
                    value=24.0,
                    step=0.5,
                    key="m1_outdoor_wb",
                    help="Coincident outdoor wet-bulb temperature. Must be below the outdoor dry bulb.",
                )
            e3, e4 = st.columns(2)
            with e3:
                ui.number_input(
                    "Indoor DB (°C)",
                    min_value=20.0,
                    max_value=30.0,
                    value=24.0,
                    step=0.5,
                    key="m1_indoor_db",
                    help="Room cooling setpoint used as the indoor design dry bulb.",
                )
            with e4:
                ui.number_input(
                    "Indoor RH (%)",
                    min_value=20.0,
                    max_value=70.0,
                    value=50.0,
                    step=5.0,
                    key="m1_indoor_rh",
                    help="Indoor design relative humidity; fixes the room humidity ratio.",
                )
            ui.selectbox(
                "Occupant activity",
                options=list(ACTIVITY_PROFILES),
                index=1,
                key="m1_activity",
                help="ASHRAE-style activity profiles with sensible and latent heat per person.",
            )
            i1, i2 = st.columns(2)
            with i1:
                ui.number_input(
                    "Lighting (W/m²)",
                    min_value=0.0,
                    max_value=40.0,
                    value=8.0,
                    step=0.5,
                    key="m1_lighting",
                    help="Connected lighting power density. All of it is treated as a room sensible gain.",
                )
            with i2:
                ui.number_input(
                    "Equipment (W)",
                    min_value=0.0,
                    max_value=15000.0,
                    value=1500.0,
                    step=100.0,
                    key="m1_equipment",
                    help="Total equipment and plug-load heat gain in the room.",
                )
            ui.selectbox(
                "Solar exposure",
                options=list(WALL_SOLAR_OPTIONS),
                index=0,
                key="m1_facade",
                on_change=_apply_facade,
                help="Façade orientation sets the peak solar irradiance used for the wall and glazing.",
            )
            e5, e6 = st.columns(2)
            with e5:
                ui.number_input(
                    "Wall solar (W/m²)",
                    min_value=0.0,
                    max_value=1100.0,
                    value=600.0,
                    step=10.0,
                    key="m1_wall_solar",
                    help="Incident solar irradiance on the exposed wall and glazing.",
                )
            with e6:
                ui.number_input(
                    "Roof solar (W/m²)",
                    min_value=0.0,
                    max_value=1300.0,
                    value=950.0,
                    step=10.0,
                    key="m1_roof_solar",
                    help="Incident solar irradiance on the roof surface.",
                )

    with st.expander("Advanced surface & psychrometric settings"):
        a1, a2, a3 = st.columns(3)
        with a1:
            ui.number_input(
                "Outdoor film coefficient (W/m²·K)",
                min_value=5.0,
                max_value=40.0,
                value=20.0,
                step=1.0,
                key="m1_film",
                help="External convective coefficient used to convert absorbed solar radiation into sol-air temperature.",
            )
        with a2:
            ui.number_input(
                "Atmospheric pressure (kPa)",
                min_value=80.0,
                max_value=110.0,
                value=101.325,
                step=0.1,
                format="%.3f",
                key="m1_pressure",
                help="Site atmospheric pressure used in all psychrometric property calculations.",
            )
        with a3:
            st.caption(
                "The default case models a 96 m², 20-person space with a hot-dry "
                "45 °C design day. Use it as the common thread across all four modules."
            )

    ui.remember_inputs("m1_")
    try:
        result = calculate_thermal_load(_build_inputs())
        st.session_state["load_result"] = result
        error = None
    except Exception as exc:  # pragma: no cover - exercised through the UI
        result = None
        error = exc
        # A failed design must not leave an older result feeding downstream modules.
        st.session_state["load_result"] = None

    with kpi_slot.container():
        if result is not None:
            ui.metric_grid(
                [
                    {
                        "label": "Room sensible heat",
                        "value": f"{result.room_sensible_kw:,.2f}",
                        "unit": "kW",
                        "foot": "Envelope, solar, people, lighting, equipment",
                        "tone": "teal",
                        "help": "Sensible room gain only. The outdoor-air ventilation load is reported separately.",
                    },
                    {
                        "label": "Room latent heat",
                        "value": f"{result.room_latent_kw:,.2f}",
                        "unit": "kW",
                        "foot": f"{result.inputs.occupants} people + {result.inputs.infiltration_ach:.2f} ACH infiltration",
                        "tone": "blue",
                        "help": "Moisture gain from occupants and infiltration, expressed as an equivalent latent cooling load.",
                    },
                    {
                        "label": "Room sensible heat factor",
                        "value": f"{100 * result.room_rshf:.1f}",
                        "unit": "%",
                        "foot": "RSH ÷ (RSH + RLH), room loads only",
                        "tone": "ochre",
                        "help": "RSHF locates the room-load line on the psychrometric chart. A high value means a mostly sensible load.",
                    },
                    {
                        "label": "Design cooling load",
                        "value": f"{result.design_total_kw:,.2f}",
                        "unit": "kW",
                        "foot": f"{result.design_tr:.2f} TR including outdoor air",
                        "tone": "terra",
                        "help": "Room gains plus the outdoor-air ventilation load at the design condition. Fan power and duct gain are excluded.",
                    },
                ]
            )
            ui.chip_row(
                [
                    ("Floor area", f"{result.floor_area_m2:.1f} m²"),
                    ("Volume", f"{result.volume_m3:.1f} m³"),
                    ("Net wall", f"{result.net_wall_area_m2:.1f} m²"),
                    ("Outdoor", f"{result.outdoor_state.dry_bulb_c:.0f} °C / {result.outdoor_state.wet_bulb_c:.0f} °C WB"),
                    ("Room", f"{result.indoor_state.dry_bulb_c:.0f} °C / {result.indoor_state.relative_humidity_pct:.0f}% RH"),
                    ("Ventilation", f"{result.ventilation_m3_s * 3600:.0f} m³/h"),
                ]
            )
        else:
            ui.error_block(
                error,
                "Check that the outdoor wet bulb is below the outdoor dry bulb, the window area fits the exposed wall, and the design condition creates a positive load.",
            )

    if result is None:
        ui.page_footer()
        return

    ui.section_heading(
        "Where the heat comes from",
        kicker="Load breakdown",
        description=(
            "Room components are shown in teal and the separate outdoor-air ventilation "
            "load in amber. The design coil load is the sum of both scopes."
        ),
    )
    chart_col, summary_col = st.columns([1.55, 1], gap="medium")
    with chart_col:
        ui.plot(load_breakdown_chart(result), key="m1_breakdown")
    with summary_col:
        ui.panel_title("Design summary", "Peak condition")
        summary = result.summary_frame()
        ui.show_table(
            summary,
            height=415,
            formats={"Value": "%.2f"},
        )

    with st.expander("Component audit table & export"):
        components = result.component_frame(include_ventilation=True)
        ui.show_table(
            components,
            height=360,
            formats={
                "Sensible (kW)": "%.3f",
                "Latent (kW)": "%.3f",
                "Total (kW)": "%.3f",
            },
        )
        d1, d2 = st.columns(2)
        with d1:
            ui.download_csv(
                components,
                filename="hvac_module1_component_loads.csv",
                label="Download component schedule (CSV)",
                key="m1_download_components",
                help_text="Every load component with its calculation basis.",
            )
        with d2:
            ui.download_csv(
                summary,
                filename="hvac_module1_design_summary.csv",
                label="Download design summary (CSV)",
                key="m1_download_summary",
            )

    note_bits = " ".join(result.notes)
    ui.callout(
        "Engineering reading",
        (
            f"The room RSHF is {100 * result.room_rshf:.1f}%, so the space-load line is steep: "
            f"only {100 * (1 - result.room_rshf):.1f}% of the room gain is latent. "
            f"Adding outdoor air raises the coil load to {result.design_total_kw:.2f} kW "
            f"({result.design_tr:.2f} TR) with a coil SHR of {100 * result.design_shr:.1f}%."
            f"\n\n{note_bits}"
        ),
        tone="ochre",
    )

    with st.expander("Method notes and assumptions"):
        st.markdown(
            """
**Opaque envelope.** Wall and roof gains use sol-air temperature,
`T_sol = T_out + α·G / h_o`, so absorbed solar radiation is represented without a
separate radiant model.

**Glazing.** Conduction uses `U·A·(T_out − T_in)`. Solar transmission uses
`SHGC·A·G·SC`, where the shading factor reduces the incident irradiance.

**Room versus coil load.** Internal, envelope and infiltration gains form the room
load and set RSHF. Ventilation outdoor air is a separate coil load and is added
afterward for equipment sizing.

**Scope.** This is a steady peak estimate. It does not model thermal lag, fan heat,
duct gain, or hour-by-hour solar and occupancy profiles.
"""
        )
    ui.page_footer()
