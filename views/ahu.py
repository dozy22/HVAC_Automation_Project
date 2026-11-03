"""Module 2 — psychrometric processes, AHU mixing, coil and property explorer."""

from __future__ import annotations

import pandas as pd
from i18n import st_ar as st

import ui
from hvac.ahu import design_ahu, heating_and_steam_humidification
from hvac.charts import (
    ahu_psychrometric_chart,
    heating_process_chart,
    single_state_chart,
)
from hvac.psychrometrics import (
    P_ATM_STD_KPA,
    PsychrometricState,
    moist_air_specific_heat,
    psychrometric_state,
)
from hvac.thermal_loads import LoadResult

MODULE_FACTS = (
    ("Chain", "OA + RA → MA → SA"),
    ("Coil metrics", "ADP · BPF · SHR"),
    ("Linked inputs", "Module 1 loads"),
)


def _state_frame(result) -> pd.DataFrame:
    rows = []
    for label, state in (
        ("Outdoor air (OA)", result.outdoor),
        ("Return air (RA)", result.room),
        ("Mixed air (MA)", result.mixed),
        ("Supply air (SA)", result.supply),
        ("Apparatus dew point", result.apparatus_dew_point),
    ):
        rows.append(
            {
                "State": label,
                "DBT (°C)": state.dry_bulb_c,
                "WBT (°C)": state.wet_bulb_c,
                "RH (%)": state.relative_humidity_pct,
                "W (g/kg)": state.humidity_ratio_g_kg,
                "h (kJ/kg)": state.enthalpy_kj_kg,
                "v (m³/kg)": state.specific_volume_m3_kg,
            }
        )
    return pd.DataFrame(rows)


def _coil_summary(result) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Metric": [
                "Coil total load",
                "Coil sensible load",
                "Coil latent load",
                "Coil sensible heat ratio",
                "Supply-air mass flow",
                "Supply-air volume flow",
                "Outdoor-air fraction",
                "Bypass factor",
                "Contact factor",
            ],
            "Value": [
                result.coil_total_kw,
                result.coil_sensible_kw,
                result.coil_latent_kw,
                100.0 * result.coil_shr,
                result.supply_mass_flow_kg_s,
                3600.0 * result.supply_volume_flow_m3_s,
                100.0 * result.outdoor_air_fraction,
                result.bypass_factor,
                1.0 - result.bypass_factor,
            ],
            "Unit": [
                "kW",
                "kW",
                "kW",
                "%",
                "kg/s",
                "m³/h",
                "%",
                "–",
                "–",
            ],
        }
    )


def _auto_outdoor_fraction(load: LoadResult, supply_c: float) -> float:
    cp = moist_air_specific_heat(load.indoor_state.humidity_ratio)
    delta_t = max(0.5, load.indoor_state.dry_bulb_c - supply_c)
    supply_mass = load.room_sensible_kw / (cp * delta_t)
    if supply_mass <= 1e-9:
        return 0.20
    fraction = load.ventilation_mass_kg_s / supply_mass
    return float(min(0.90, max(0.02, fraction)))


def _cooling_tab(load: LoadResult) -> None:
    room = load.indoor_state
    outdoor = load.outdoor_state
    ui.chip_row(
        [
            ("Space", f"{load.inputs.project_name}", "teal"),
            ("Room design", f"{room.dry_bulb_c:.1f} °C · {room.relative_humidity_pct:.0f}% RH"),
            ("Outdoor design", f"{outdoor.dry_bulb_c:.1f} °C DB · {outdoor.wet_bulb_c:.1f} °C WB"),
            ("Room loads", f"{load.room_sensible_kw:.2f} kW S + {load.room_latent_kw:.2f} kW L", "ochre"),
        ]
    )

    left, right = st.columns([0.82, 1.55], gap="medium")
    with left:
        with st.container(border=True):
            ui.panel_title("AHU process inputs", "Cooling coil")
            use_room_loads = ui.toggle(
                "Use Module 1 room loads",
                value=True,
                key="m2_use_loads",
                help="Keep the psychrometric process consistent with the current cooling-load calculation.",
            )
            if use_room_loads:
                sensible_kw = load.room_sensible_kw
                latent_kw = load.room_latent_kw
                st.caption(
                    f"Connected: **{sensible_kw:.2f} kW sensible** and "
                    f"**{latent_kw:.2f} kW latent**. These set the supply airflow and "
                    "the room-load direction."
                )
            else:
                sensible_kw = ui.number_input(
                    "Room sensible load (kW)",
                    min_value=0.5,
                    max_value=100.0,
                    value=float(round(load.room_sensible_kw, 2)),
                    step=0.5,
                    key="m2_sensible",
                    help="Sensible load used to size supply airflow for the chosen supply temperature.",
                )
                latent_kw = ui.number_input(
                    "Room latent load (kW)",
                    min_value=0.0,
                    max_value=60.0,
                    value=float(round(load.room_latent_kw, 2)),
                    step=0.1,
                    key="m2_latent",
                    help="Latent load used to place the supply-state humidity ratio on the room RSHF line.",
                )
            supply_c = ui.slider(
                "Supply-air dry-bulb (°C)",
                min_value=7.0,
                max_value=20.0,
                value=13.0,
                step=0.5,
                key="m2_supply",
                help="Coil leaving-air temperature. Colder air reduces airflow but requires a colder coil and more dehumidification.",
            )
            auto_oa = ui.toggle(
                "Set outdoor-air fraction from ventilation",
                value=True,
                key="m2_auto_oa",
                help="Uses the Module 1 outdoor-air mass flow divided by the estimated supply mass flow.",
            )
            auto_fraction = _auto_outdoor_fraction(load, supply_c)
            if auto_oa:
                outdoor_fraction = auto_fraction
                ui.number_input(
                    "Outdoor-air fraction (%)",
                    min_value=2.0,
                    max_value=90.0,
                    value=round(100.0 * auto_fraction, 1),
                    step=1.0,
                    format="%.1f",
                    disabled=True,
                    help="Automatically calculated from the ventilation mass balance.",
                )
            else:
                outdoor_fraction = (
                    ui.slider(
                        "Outdoor-air mass fraction (%)",
                        min_value=2.0,
                        max_value=80.0,
                        value=float(round(100.0 * auto_fraction, 1)),
                        step=1.0,
                        key="m2_oa_manual",
                        help="Mass fraction of dry outdoor air in the mixed airstream.",
                    )
                    / 100.0
                )
            st.caption(
                "Mass basis, not volume. Adiabatic mixing follows conservation of "
                "dry air, water vapour and enthalpy."
            )

    result = None
    error = None
    try:
        result = design_ahu(
            room,
            outdoor,
            sensible_kw,
            latent_kw,
            supply_c,
            outdoor_fraction,
            room.pressure_kpa,
        )
        st.session_state["ahu_result"] = result
    except Exception as exc:  # pragma: no cover - UI validation path
        error = exc
        # Do not let a rejected coil condition size the refrigeration plant.
        st.session_state["ahu_result"] = None

    with right:
        if result is not None:
            ui.metric_grid(
                [
                    {
                        "label": "Coil design load",
                        "value": f"{result.coil_total_kw:.2f}",
                        "unit": "kW",
                        "foot": f"Mixed-to-supply enthalpy change",
                        "tone": "teal",
                        "help": "Total cooling delivered between the mixed-air and supply-air states.",
                    },
                    {
                        "label": "Coil sensible heat ratio",
                        "value": f"{100 * result.coil_shr:.1f}",
                        "unit": "%",
                        "foot": "Sensible ÷ total coil load",
                        "tone": "blue",
                        "help": "The coil SHR differs from the room RSHF because the mixed-air state and coil process are included.",
                    },
                    {
                        "label": "Apparatus dew point",
                        "value": f"{result.apparatus_dew_point_c:.2f}",
                        "unit": "°C",
                        "foot": "Intersection with saturation line",
                        "tone": "ochre",
                        "help": "ADP is the effective coil-surface condition found by extending the coil process line to saturation.",
                    },
                    {
                        "label": "Bypass factor",
                        "value": f"{result.bypass_factor:.3f}",
                        "unit": "–",
                        "foot": f"Contact factor {1 - result.bypass_factor:.3f}",
                        "tone": "terra",
                        "help": "BPF = (W_mixed − W_supply) / (W_mixed − W_ADP). A higher value means more air bypasses the coil surface.",
                    },
                ]
            )
            ui.chip_row(
                [
                    ("Mixed air", f"{result.mixed.dry_bulb_c:.2f} °C · {result.mixed.relative_humidity_pct:.1f}% RH", "teal"),
                    ("Supply air", f"{result.supply.dry_bulb_c:.1f} °C · {result.supply.relative_humidity_pct:.1f}% RH"),
                    ("Airflow", f"{result.supply_mass_flow_kg_s:.2f} kg/s · {3600 * result.supply_volume_flow_m3_s:.0f} m³/h"),
                    ("OA fraction", f"{100 * result.outdoor_air_fraction:.1f}%"),
                ]
            )
            st.caption(
                "The process line runs outdoor and return air to the mixed point, then "
                "through the coil toward ADP. The supply point sits on the room RSHF line."
            )
        else:
            ui.error_block(
                error,
                "Try a warmer supply temperature, lower room latent load, or a lower "
                "outdoor-air fraction. The tool will not display a supersaturated state.",
            )

    if result is None:
        return

    ui.section_heading(
        "The process, drawn to scale",
        kicker="Psychrometric chart",
        description=(
            "Hover any point for dry bulb, humidity ratio, relative humidity, enthalpy "
            "and wet bulb. Shaded bands are indicative rather than code-compliance zones."
        ),
    )
    ui.plot(ahu_psychrometric_chart(result), key="m2_psych_chart")

    table_col, state_col = st.columns([0.9, 1.35], gap="medium")
    with table_col:
        ui.panel_title("Coil performance", "Design point")
        ui.show_table(
            _coil_summary(result),
            height=390,
            formats={"Value": "%.3f"},
        )
    with state_col:
        ui.panel_title("State-point properties", "Moist air")
        states = _state_frame(result)
        ui.show_table(
            states,
            height=390,
            formats={
                "DBT (°C)": "%.2f",
                "WBT (°C)": "%.2f",
                "RH (%)": "%.1f",
                "W (g/kg)": "%.2f",
                "h (kJ/kg)": "%.1f",
                "v (m³/kg)": "%.3f",
            },
        )

    d1, d2 = st.columns(2)
    with d1:
        ui.download_csv(
            states,
            filename="hvac_module2_state_points.csv",
            label="Download state points (CSV)",
            key="m2_download_states",
        )
    with d2:
        ui.download_csv(
            _coil_summary(result),
            filename="hvac_module2_coil_design.csv",
            label="Download coil design (CSV)",
            key="m2_download_coil",
        )

    design_gap = result.coil_total_kw - load.design_total_kw
    if result.bypass_factor > 0.80:
        bpf_note = (
            f"A high bypass factor of {result.bypass_factor:.2f} means the coil process "
            "stays far from the saturation curve while still meeting a mostly sensible load. "
            "The ADP is therefore well below the supply dry bulb."
        )
    else:
        bpf_note = (
            f"With BPF {result.bypass_factor:.2f}, a meaningful share of the air reaches "
            "the coil surface, so the process bends toward the ADP and removes more moisture."
        )
    gap_text = (
        f"The independently sized Module 1 design load is {load.design_total_kw:.2f} kW; "
        f"the selected mixing and supply condition gives {result.coil_total_kw:.2f} kW "
        f"({design_gap:+.2f} kW difference)."
    )
    ui.callout(
        "Engineering reading",
        (
            f"{gap_text}"
            "\n\n"
            f"A {100 * result.outdoor_air_fraction:.1f}% outdoor-air mass fraction "
            f"produces mixed air at {result.mixed.dry_bulb_c:.2f} °C / "
            f"{result.mixed.relative_humidity_pct:.1f}% RH."
            "\n\n"
            f"{bpf_note}"
            "\n\n"
            f"Room RSHF is {100 * result.space_rshf:.1f}%, while the coil SHR is "
            f"{100 * result.coil_shr:.1f}%: the difference is the psychrometric effect of "
            "conditioning the outdoor air."
        ),
        tone="ochre",
    )

    with st.expander("Coil construction and method"):
        st.markdown(
            """
**Mixing.** Outdoor and return air combine adiabatically on a dry-air mass basis:
`W_mix = f·W_OA + (1−f)·W_RA` and `h_mix = f·h_OA + (1−f)·h_RA`.

**Supply state.** Sensible room load sets the dry-air mass flow,
`m = Q_s / [c_p,m·(T_RA − T_SA)]`. Latent room load then places the supply
humidity ratio: `W_SA = W_RA − Q_l / (m·h_fg)`.

**ADP and BPF.** The straight line from mixed air through supply air is extended
to its nearest intersection with the saturation curve. BPF is the humidity-ratio
distance ratio `(W_MA − W_SA) / (W_MA − W_ADP)`.

**Contact factor.** Reported as `1 − BPF`. A real coil also has air-side and
refrigerant-side resistances, which this chart-level model does not resolve.
"""
        )


def _heating_tab() -> None:
    st.markdown(
        "A winter air-handling process is built here as sensible preheat followed by "
        "idealised steam humidification."
    )
    left, right = st.columns([0.82, 1.55], gap="medium")
    with left:
        with st.container(border=True):
            ui.panel_title("Heating & humidification", "Winter process")
            h1, h2 = st.columns(2)
            with h1:
                entering_db = ui.number_input(
                    "Entering DB (°C)",
                    min_value=0.0,
                    max_value=35.0,
                    value=12.0,
                    step=0.5,
                    key="m2_heat_enter_db",
                    help="Air condition before the preheat coil.",
                )
            with h2:
                entering_rh = ui.number_input(
                    "Entering RH (%)",
                    min_value=10.0,
                    max_value=95.0,
                    value=60.0,
                    step=5.0,
                    key="m2_heat_enter_rh",
                    help="Relative humidity before heating.",
                )
            h3, h4 = st.columns(2)
            with h3:
                target_db = ui.number_input(
                    "Target DB (°C)",
                    min_value=15.0,
                    max_value=40.0,
                    value=22.0,
                    step=0.5,
                    key="m2_heat_target_db",
                    help="Room supply temperature after heating and humidification.",
                )
            with h4:
                target_rh = ui.number_input(
                    "Target RH (%)",
                    min_value=20.0,
                    max_value=90.0,
                    value=55.0,
                    step=5.0,
                    key="m2_heat_target_rh",
                    help="Desired relative humidity at the target dry bulb.",
                )
            mass_flow = ui.number_input(
                "Supply mass flow (kg/s)",
                min_value=0.05,
                max_value=5.0,
                value=0.50,
                step=0.05,
                key="m2_heat_flow",
                help="Dry-air mass flow through the heater and steam humidifier.",
            )
            st.caption(
                "Heating occurs at constant humidity ratio. Steam humidification is "
                "shown at approximately constant dry-bulb temperature."
            )

    result = None
    error = None
    try:
        entering = psychrometric_state(
            entering_db,
            P_ATM_STD_KPA,
            relative_humidity_pct=entering_rh,
        )
        result = heating_and_steam_humidification(
            entering,
            target_db,
            target_rh,
            mass_flow,
        )
    except Exception as exc:  # pragma: no cover - UI validation path
        error = exc

    with right:
        if result is not None:
            ui.metric_grid(
                [
                    {
                        "label": "Sensible heating",
                        "value": f"{result.heating_kw:.2f}",
                        "unit": "kW",
                        "foot": "Entering air to target dry bulb at constant W",
                        "tone": "terra",
                        "help": "Q = m·(h_heated − h_entering) along a constant humidity-ratio line.",
                    },
                    {
                        "label": "Steam added",
                        "value": f"{result.humidification_kg_h:.2f}",
                        "unit": "kg/h",
                        "foot": "Actual moisture addition rate",
                        "tone": "blue",
                        "help": "m_steam = m_dry_air·(W_target − W_entering), converted to kg/h.",
                    },
                    {
                        "label": "Humidifier heat",
                        "value": f"{result.humidification_energy_kw:.2f}",
                        "unit": "kW",
                        "foot": "Enthalpy added with the steam",
                        "tone": "ochre",
                        "help": "Energy carried by the added steam, not the electrical input of a real humidifier.",
                    },
                    {
                        "label": "Room supply state",
                        "value": f"{result.leaving.dry_bulb_c:.1f}",
                        "unit": "°C",
                        "foot": f"{result.leaving.relative_humidity_pct:.1f}% RH · W {result.leaving.humidity_ratio_g_kg:.2f} g/kg",
                        "tone": "teal",
                    },
                ]
            )
            ui.chip_row(ui.state_chip_items(result.leaving))
        else:
            ui.error_block(
                error,
                "The target must be warmer than the entering air and its humidity ratio "
                "must not be lower than the entering condition.",
            )

    if result is None:
        return

    ui.section_heading(
        "Heating and humidification path",
        kicker="Winter process",
        description=(
            "The terracotta segment is sensible heating at constant W; the blue segment "
            "is the idealised steam process that supplies the required moisture."
        ),
    )
    ui.plot(heating_process_chart(result), key="m2_heating_chart")
    ui.callout(
        "Engineering reading",
        (
            f"The air is first heated from {result.entering.dry_bulb_c:.1f} °C to "
            f"{result.heated.dry_bulb_c:.1f} °C without changing its moisture content. "
            f"Steam then raises the supply humidity ratio by "
            f"{(result.leaving.humidity_ratio - result.entering.humidity_ratio) * 1000:.2f} g/kg, "
            f"using {result.humidification_kg_h:.2f} kg/h of moisture."
            "\n\nA real steam humidifier adds both latent and small sensible heat; the "
            "horizontal representation is a standard teaching idealisation."
        ),
        tone="ochre",
    )


def _property_tab(load: LoadResult) -> None:
    st.markdown(
        "Calculate any moist-air state directly from dry-bulb temperature and either "
        "relative humidity or wet bulb."
    )
    with st.container(border=True):
        p1, p2, p3 = st.columns([1, 1.2, 1.2], gap="medium")
        with p1:
            dry_bulb = ui.number_input(
                "Dry-bulb temperature (°C)",
                min_value=0.0,
                max_value=50.0,
                value=25.0,
                step=0.5,
                key="m2_prop_db",
                help="Thermodynamic dry-bulb temperature at the stated pressure.",
            )
        with p2:
            basis = ui.radio(
                "Second property",
                options=["Relative humidity", "Wet bulb"],
                index=0,
                horizontal=True,
                key="m2_prop_basis",
                help="Choose the moisture property used to fix the thermodynamic state.",
            )
        with p3:
            if basis == "Wet bulb":
                wet_bulb = ui.number_input(
                    "Wet-bulb temperature (°C)",
                    min_value=-5.0,
                    max_value=49.0,
                    value=17.9,
                    step=0.5,
                    key="m2_prop_wb",
                    help="Thermodynamic wet-bulb temperature. Must be below the dry bulb.",
                )
                rh_value = None
            else:
                rh_value = ui.number_input(
                    "Relative humidity (%)",
                    min_value=1.0,
                    max_value=100.0,
                    value=50.0,
                    step=1.0,
                    key="m2_prop_rh",
                    help="Ratio of actual vapour pressure to saturation pressure at the dry bulb.",
                )
                wet_bulb = None

    state = None
    error = None
    try:
        state = psychrometric_state(
            dry_bulb,
            load.indoor_state.pressure_kpa,
            relative_humidity_pct=rh_value,
            wet_bulb_c=wet_bulb,
        )
    except Exception as exc:  # pragma: no cover - UI validation path
        error = exc

    if state is not None:
        ui.metric_grid(
            [
                {
                    "label": "Dry bulb",
                    "value": f"{state.dry_bulb_c:.1f}",
                    "unit": "°C",
                    "foot": "DBT",
                    "tone": "teal",
                },
                {
                    "label": "Wet bulb",
                    "value": f"{state.wet_bulb_c:.1f}",
                    "unit": "°C",
                    "foot": "Thermodynamic WBT",
                    "tone": "blue",
                },
                {
                    "label": "Dew point",
                    "value": f"{state.dew_point_c:.1f}",
                    "unit": "°C",
                    "foot": "At constant vapour pressure",
                    "tone": "violet",
                },
                {
                    "label": "Relative humidity",
                    "value": f"{state.relative_humidity_pct:.1f}",
                    "unit": "%",
                    "foot": "RH",
                    "tone": "green",
                },
                {
                    "label": "Humidity ratio",
                    "value": f"{state.humidity_ratio_g_kg:.2f}",
                    "unit": "g/kg",
                    "foot": "W per kg dry air",
                    "tone": "teal",
                },
                {
                    "label": "Enthalpy",
                    "value": f"{state.enthalpy_kj_kg:.2f}",
                    "unit": "kJ/kg",
                    "foot": "Moist-air mixture basis",
                    "tone": "ochre",
                },
                {
                    "label": "Specific volume",
                    "value": f"{state.specific_volume_m3_kg:.3f}",
                    "unit": "m³/kg",
                    "foot": "Per kg dry air",
                    "tone": "terra",
                },
                {
                    "label": "Vapour pressure",
                    "value": f"{state.vapor_pressure_kpa:.3f}",
                    "unit": "kPa",
                    "foot": f"At {state.pressure_kpa:.2f} kPa total pressure",
                    "tone": "blue",
                },
            ]
        )
        ui.plot(single_state_chart(state, "Calculated moist-air state"), key="m2_prop_chart")
        ui.callout(
            "Engineering reading",
            (
                f"At {state.dry_bulb_c:.1f} °C and {state.relative_humidity_pct:.1f}% RH, "
                f"each kilogram of dry air carries {state.humidity_ratio_g_kg:.2f} g of water "
                f"vapour and {state.enthalpy_kj_kg:.1f} kJ of mixture enthalpy. The dew point "
                f"is {state.dew_point_c:.1f} °C, so a surface below that temperature will "
                "condense moisture from this air."
            )
        )
    else:
        ui.error_block(
            error,
            "The wet bulb must lie below the dry bulb, and both must define a physically "
            "possible unsaturated state.",
        )

    with st.expander("Property equations used by the engine"):
        st.markdown(
            "Saturation pressure is evaluated with the Hyland–Wexler correlation. "
            "Humidity ratio, enthalpy, specific volume and dew point follow the "
            "ASHRAE Fundamentals relations."
        )
        st.latex(r"W = 0.621945\,\frac{p_w}{p - p_w}")
        st.latex(r"h = 1.006\,T_{db} + W\,(2501 + 1.86\,T_{db})")
        st.latex(r"v = \frac{R_{da}\,T\,(1 + 1.607858\,W)}{p}")
        st.caption(
            "Wet bulb is obtained by inverting the thermodynamic wet-bulb relation at the "
            "stated pressure; it is not a simple linear estimate. The comfort zone shown "
            "on the chart is an indicative teaching band, not a Standard 55 compliance check."
        )


def render() -> None:
    ui.page_header(
        index="02",
        module_label="Psychrometric processes & AHU",
        chapter="Chapters 2 & 3 · Moist air & air handling",
        title="Psychrometric",
        accent="processes & AHU",
        description=(
            "Move an airstream through mixing, cooling, dehumidification, heating and "
            "humidification while every state remains thermodynamically consistent. "
            "The coil solution reports ADP, bypass factor and the true coil SHR."
        ),
        facts=MODULE_FACTS,
    )

    load = st.session_state.get("load_result")
    if not isinstance(load, LoadResult):
        st.warning(
            "Module 1 has no valid design case yet. Open the cooling-load module, "
            "resolve any input error, then return here."
        )
        ui.page_footer()
        return

    tab_process, tab_heat, tab_properties = st.tabs(
        ["Cooling & dehumidification", "Heating & humidification", "Moist-air properties"]
    )
    with tab_process:
        _cooling_tab(load)
    with tab_heat:
        _heating_tab()
    with tab_properties:
        _property_tab(load)
    ui.remember_inputs("m2_")
    ui.page_footer()
