"""Module 4 — closed-loop HVAC control and comfort dashboard."""

from __future__ import annotations

import pandas as pd
from i18n import st_ar as st

import ui
from hvac.charts import comfort_map_chart, control_action_chart, control_timeline_chart
from hvac.controls import (
    ACTUATOR_SUPPLY,
    ACTUATOR_VALVE,
    CONTROLLER_PID,
    CONTROLLER_THRESHOLD,
    WEATHER_SCENARIOS,
    ComfortLimits,
    SimulationInputs,
    controller_comparison,
    simulate_control,
)
from hvac.refrigeration import CycleResult

MODULE_FACTS = (
    ("Controllers", "PID & threshold hysteresis"),
    ("Actuators", "Chilled-water valve · SA temperature"),
    ("Comfort test", "ET* proxy + 30–70% RH"),
)


def _apply_weather() -> None:
    selected = st.session_state.get("m4_weather", "Hot afternoon")
    scenario = WEATHER_SCENARIOS.get(selected)
    if scenario:
        st.session_state["m4_out_mean"] = scenario["mean_c"]
        st.session_state["m4_out_amp"] = scenario["amplitude_c"]
        st.session_state["m4_out_rh"] = scenario["rh_pct"]


def render() -> None:
    ui.page_header(
        index="04",
        module_label="Automatic control & smart comfort",
        chapter="Chapters 3 & 11 · Comfort & control",
        title="Comfort under",
        accent="automatic control",
        description=(
            "Close the loop on a reduced-order zone. A PID or threshold controller commands "
            "either a chilled-water valve or a supply-air temperature to hold effective "
            "temperature and relative humidity inside the acceptance band."
        ),
        facts=MODULE_FACTS,
    )

    cycle = st.session_state.get("cycle_result")
    cycle_cop = cycle.cop if isinstance(cycle, CycleResult) else 3.2
    ui.chip_row(
        [
            ("Zone", "96 m² classroom · 307 m³", "teal"),
            ("Plant", "10 kW rated sensible demo coil"),
            ("COP source", f"Module 3 · {cycle_cop:.3f}" if isinstance(cycle, CycleResult) else "default 3.20", "ochre"),
            ("Model", "Reduced-order energy & moisture balance"),
        ]
    )
    st.caption(
        "The loop is a teaching model, not an equipment selection. Rated capacity is "
        "sensible; the wet-coil model removes latent heat separately, so the instantaneous "
        "total cooling demand can exceed the rated sensible value."
    )

    left, right = st.columns([0.86, 1.55], gap="medium")
    with left:
        with st.container(border=True):
            ui.panel_title("Control specification", "Closed loop")
            controller = ui.radio(
                "Controller",
                options=[CONTROLLER_PID, CONTROLLER_THRESHOLD],
                index=0,
                horizontal=True,
                key="m4_controller",
                help="PID modulates the actuator continuously. Threshold control switches between fully on and off with hysteresis.",
            )
            actuator = ui.selectbox(
                "Actuator",
                options=[ACTUATOR_VALVE, ACTUATOR_SUPPLY],
                index=0,
                key="m4_actuator",
                help="The valve modulates coil capacity. The supply-air option adjusts the air temperature delivered to the zone.",
            )
            weather = ui.selectbox(
                "Weather scenario",
                options=list(WEATHER_SCENARIOS),
                index=0,
                key="m4_weather",
                on_change=_apply_weather,
                help="Illustrative outdoor dry-bulb swing and humidity for the demonstration day.",
            )
            d1, d2 = st.columns(2)
            with d1:
                duration_h = ui.number_input(
                    "Simulation duration (h)",
                    min_value=2,
                    max_value=12,
                    value=8,
                    step=1,
                    key="m4_duration",
                    help="Length of the demonstration day. The comfort KPI uses the final half.",
                )
            with d2:
                setpoint_c = ui.number_input(
                    "Cooling setpoint (°C)",
                    min_value=20.0,
                    max_value=28.0,
                    value=24.5,
                    step=0.5,
                    key="m4_setpoint",
                    help="Dry-bulb setpoint used by both controllers.",
                )
            ui.slider(
                "Rated sensible cooling capacity (kW)",
                min_value=4.0,
                max_value=25.0,
                value=10.0,
                step=0.5,
                key="m4_capacity",
                help="Sensible coil capacity at the design supply-to-room temperature difference. Latent removal is modelled separately.",
            )
            use_cycle = ui.toggle(
                "Use COP from Module 3",
                value=isinstance(cycle, CycleResult),
                key="m4_use_cycle",
                help="Borrow the real-fluid cycle COP to convert delivered cooling into estimated electricity.",
            )
            if use_cycle and isinstance(cycle, CycleResult):
                compressor_cop = cycle.cop
                ui.number_input(
                    "Plant COP (–)",
                    min_value=1.0,
                    max_value=10.0,
                    value=float(round(compressor_cop, 3)),
                    step=0.01,
                    format="%.3f",
                    disabled=True,
                    help="Imported from the refrigeration cycle in Module 3.",
                )
            else:
                compressor_cop = ui.number_input(
                    "Plant COP (–)",
                    min_value=1.0,
                    max_value=10.0,
                    value=3.20,
                    step=0.05,
                    key="m4_cop",
                    help="Total cooling divided by electrical input. A seasonal system COP is normally lower than a design-point cycle COP.",
                )
            if controller == CONTROLLER_PID:
                st.caption(
                    "PID: error is room temperature minus setpoint. The output is bounded "
                    "to 0–100% with conditional-integration anti-windup."
                )
            else:
                st.caption(
                    "Threshold: the plant switches at setpoint ± half the deadband. "
                    "Hysteresis prevents rapid short-cycling."
                )

        with st.expander("PID gains & switching band"):
            if controller == CONTROLLER_PID:
                kp = ui.number_input(
                    "Proportional gain Kp (%/K)",
                    min_value=0.0,
                    max_value=120.0,
                    value=22.0,
                    step=1.0,
                    key="m4_kp",
                    help="Immediate valve or supply-temperature response to temperature error.",
                )
                ki = ui.number_input(
                    "Integral gain Ki (%/K·s)",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.070,
                    step=0.005,
                    format="%.3f",
                    key="m4_ki",
                    help="Removes steady-state offset. Too much integral action causes overshoot.",
                )
                kd = ui.number_input(
                    "Derivative gain Kd (%·min/K)",
                    min_value=0.0,
                    max_value=120.0,
                    value=25.0,
                    step=1.0,
                    key="m4_kd",
                    help="Damps fast temperature change. The implementation differentiates the measurement.",
                )
                threshold_band = 0.6
            else:
                threshold_band = ui.number_input(
                    "Switching deadband (K)",
                    min_value=0.2,
                    max_value=3.0,
                    value=0.6,
                    step=0.1,
                    key="m4_band",
                    help="Total deadband around the setpoint. A wider band means fewer switch changes but larger temperature swings.",
                )
                kp, ki, kd = 22.0, 0.070, 25.0

        with st.expander("Comfort acceptance band"):
            c1, c2 = st.columns(2)
            with c1:
                et_min_c = ui.number_input(
                    "ET* minimum (°C)",
                    min_value=19.0,
                    max_value=27.0,
                    value=23.0,
                    step=0.5,
                    key="m4_et_min",
                    help="Lower effective-temperature acceptance limit.",
                )
            with c2:
                et_max_c = ui.number_input(
                    "ET* maximum (°C)",
                    min_value=22.0,
                    max_value=31.0,
                    value=26.0,
                    step=0.5,
                    key="m4_et_max",
                    help="Upper effective-temperature acceptance limit.",
                )
            c3, c4 = st.columns(2)
            with c3:
                rh_min_pct = ui.number_input(
                    "RH minimum (%)",
                    min_value=10.0,
                    max_value=60.0,
                    value=30.0,
                    step=5.0,
                    key="m4_rh_min",
                    help="Project comfort criterion used as an acceptance gate.",
                )
            with c4:
                rh_max_pct = ui.number_input(
                    "RH maximum (%)",
                    min_value=40.0,
                    max_value=90.0,
                    value=70.0,
                    step=5.0,
                    key="m4_rh_max",
                    help="Project comfort criterion used as an acceptance gate.",
                )
            st.caption(
                "ET* is a transparent humidity-adjusted teaching proxy. The 30–70% RH "
                "band is a project criterion, not a universal Standard 55 requirement."
            )

        with st.expander("Zone and weather model"):
            z1, z2 = st.columns(2)
            with z1:
                outdoor_mean = ui.number_input(
                    "Outdoor mean DB (°C)",
                    min_value=22.0,
                    max_value=45.0,
                    value=36.0,
                    step=0.5,
                    key="m4_out_mean",
                    help="Mean outdoor dry bulb over the simulated day.",
                )
                outdoor_amplitude = ui.number_input(
                    "Outdoor swing (±K)",
                    min_value=0.0,
                    max_value=10.0,
                    value=4.5,
                    step=0.5,
                    key="m4_out_amp",
                    help="Half-amplitude of the sinusoidal outdoor dry-bulb profile, peaking around 15:00.",
                )
                outdoor_rh = ui.number_input(
                    "Outdoor RH (%)",
                    min_value=10.0,
                    max_value=90.0,
                    value=25.0,
                    step=5.0,
                    key="m4_out_rh",
                    help="Constant outdoor relative humidity used to compute ventilation moisture.",
                )
                initial_db = ui.number_input(
                    "Initial room DB (°C)",
                    min_value=20.0,
                    max_value=36.0,
                    value=28.8,
                    step=0.5,
                    key="m4_initial_db",
                    help="Starting zone temperature at the beginning of pull-down.",
                )
            with z2:
                initial_rh = ui.number_input(
                    "Initial room RH (%)",
                    min_value=20.0,
                    max_value=85.0,
                    value=55.0,
                    step=5.0,
                    key="m4_initial_rh",
                    help="Starting zone relative humidity.",
                )
                zone_ua = ui.number_input(
                    "Zone UA (kW/K)",
                    min_value=0.02,
                    max_value=1.0,
                    value=0.15,
                    step=0.01,
                    format="%.2f",
                    key="m4_ua",
                    help="Overall envelope conductance to outdoor air.",
                )
                thermal_capacity = ui.number_input(
                    "Zone capacitance (kJ/K)",
                    min_value=500.0,
                    max_value=10000.0,
                    value=2600.0,
                    step=100.0,
                    key="m4_capacity_zone",
                    help="Lumped thermal capacitance of the zone and its furnishings.",
                )
                volume = ui.number_input(
                    "Zone volume (m³)",
                    min_value=100.0,
                    max_value=1000.0,
                    value=307.0,
                    step=10.0,
                    key="m4_volume",
                    help="Used for infiltration airflow and moisture capacitance.",
                )
            z3, z4, z5 = st.columns(3)
            with z3:
                infiltration = ui.number_input(
                    "Infiltration (ACH)",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.50,
                    step=0.05,
                    key="m4_ach",
                    help="Envelope leakage expressed as air changes per hour.",
                )
            with z4:
                internal_sensible = ui.number_input(
                    "Internal sensible (kW)",
                    min_value=0.0,
                    max_value=20.0,
                    value=4.5,
                    step=0.5,
                    key="m4_internal_sensible",
                    help="People, lighting and equipment sensible gain retained in the reduced-order model.",
                )
            with z5:
                internal_latent = ui.number_input(
                    "Internal latent (kW)",
                    min_value=0.0,
                    max_value=5.0,
                    value=0.90,
                    step=0.1,
                    key="m4_internal_latent",
                    help="People and equipment moisture gain.",
                )
            st.caption(
                "The demonstration plant is deliberately smaller than the 19 kW peak "
                "design case. It exposes controller behaviour and pull-down dynamics "
                "without implying that a 10 kW coil is the selected equipment."
            )

    ui.remember_inputs("m4_")
    if et_min_c >= et_max_c:
        st.error("Comfort check: the ET* minimum must be below the ET* maximum.")
        ui.page_footer()
        return
    if rh_min_pct >= rh_max_pct:
        st.error("Comfort check: the RH minimum must be below the RH maximum.")
        ui.page_footer()
        return

    simulation = None
    error = None
    try:
        inputs = SimulationInputs(
            controller=controller,
            actuator=actuator,
            duration_h=float(duration_h),
            timestep_s=60,
            start_hour=8.0,
            setpoint_c=float(setpoint_c),
            initial_db_c=float(initial_db),
            initial_rh_pct=float(initial_rh),
            outdoor_mean_c=float(outdoor_mean),
            outdoor_amplitude_c=float(outdoor_amplitude),
            outdoor_rh_pct=float(outdoor_rh),
            zone_ua_kw_per_k=float(zone_ua),
            thermal_capacity_kj_per_k=float(thermal_capacity),
            room_volume_m3=float(volume),
            infiltration_ach=float(infiltration),
            internal_sensible_kw=float(internal_sensible),
            internal_latent_kw=float(internal_latent),
            cooling_capacity_kw=float(st.session_state.get("m4_capacity", 10.0)),
            supply_min_c=12.5,
            supply_max_c=22.0,
            compressor_cop=float(compressor_cop),
            kp=float(kp),
            ki=float(ki),
            kd=float(kd),
            threshold_band_k=float(threshold_band),
            comfort=ComfortLimits(
                et_min_c=float(et_min_c),
                et_max_c=float(et_max_c),
                rh_min_pct=float(rh_min_pct),
                rh_max_pct=float(rh_max_pct),
            ),
        )
        simulation = simulate_control(inputs)
        st.session_state["simulation_result"] = simulation
    except Exception as exc:  # pragma: no cover - UI validation path
        error = exc
        # Never show an older run as if it belonged to the current inputs.
        st.session_state["simulation_result"] = None

    with right:
        if simulation is not None:
            maintained = simulation.comfort_last_half_pct
            ui.metric_grid(
                [
                    {
                        "label": "Comfort maintained",
                        "value": f"{maintained:.0f}",
                        "unit": "%",
                        "foot": "Final half of the simulated day",
                        "tone": "teal" if maintained >= 95 else "terra",
                        "help": "Percentage of sampled control periods in the last half of the run that satisfy both ET* and RH criteria.",
                    },
                    {
                        "label": "Final room temperature",
                        "value": f"{simulation.final_db_c:.2f}",
                        "unit": "°C",
                        "foot": f"Setpoint {simulation.inputs.setpoint_c:.1f} °C",
                        "tone": "blue",
                        "help": "Zone dry-bulb temperature at the end of the simulated day.",
                    },
                    {
                        "label": "Final relative humidity",
                        "value": f"{simulation.final_rh_pct:.1f}",
                        "unit": "%",
                        "foot": f"Acceptance {simulation.inputs.comfort.rh_min_pct:.0f}–{simulation.inputs.comfort.rh_max_pct:.0f}%",
                        "tone": "green" if simulation.humidity_ok[-1] else "terra",
                    },
                    {
                        "label": "Delivered cooling",
                        "value": f"{simulation.delivered_cooling_kwh:.1f}",
                        "unit": "kWh",
                        "foot": f"Estimated electricity {simulation.estimated_electricity_kwh:.1f} kWh",
                        "tone": "ochre",
                        "help": "Integrated total coil cooling over the run. Electricity uses the selected plant COP.",
                    },
                ]
            )
            status_text = (
                "Setpoint held within 0.25 K and comfort maintained."
                if abs(simulation.final_db_c - simulation.inputs.setpoint_c) <= 0.25
                and maintained >= 99.0
                else "Review the trajectory and acceptance band."
            )
            ui.chip_row(
                [
                    ("Overall comfort", f"{simulation.comfort_pct:.1f}%", "teal"),
                    ("Thermal in band", f"{simulation.thermal_pct:.1f}%"),
                    ("RH in band", f"{simulation.humidity_pct:.1f}%"),
                    ("Peak total coil", f"{simulation.peak_cooling_kw:.1f} kW", "ochre"),
                    ("Switch changes", f"{simulation.switching_count}"),
                    ("Actuator", simulation.inputs.actuator),
                ]
            )
            st.markdown(
                f'<div class="status-pill">{status_text}</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Peak total coil includes latent removal during pull-down and may exceed "
                "the rated sensible capacity. This is intentional in the reduced-order plant."
            )
        else:
            ui.error_block(
                error,
                "Check that the setpoint exceeds the minimum supply temperature, comfort "
                "limits are ordered correctly, and zone properties are positive.",
            )

    if simulation is None:
        ui.page_footer()
        return

    ui.section_heading(
        "A day under closed-loop control",
        kicker="Control timeline",
        description=(
            "Temperature, humidity and effective temperature share the same clock. "
            "Green bands are the acceptance criteria; the dashed line is the temperature setpoint."
        ),
    )
    ui.plot(control_timeline_chart(simulation), key="m4_timeline")

    action_col, comfort_col = st.columns(2, gap="medium")
    with action_col:
        ui.panel_title("Actuator command", simulation.actuator_label)
        ui.plot(control_action_chart(simulation), key="m4_action")
    with comfort_col:
        ui.panel_title("Comfort trajectory", "ET* vs RH")
        ui.plot(comfort_map_chart(simulation), key="m4_comfort_map")

    ui.section_heading(
        "PID versus threshold",
        kicker="Controller comparison",
        description=(
            "Both controllers run on the same weather, zone and actuator. The useful "
            "comparison is stability and actuator wear, not a guaranteed energy saving "
            "in this simplified plant."
        ),
    )
    try:
        comparison = controller_comparison(simulation.inputs)
        display = comparison[
            [
                "Controller",
                "Comfort last half (%)",
                "Humidity in band (%)",
                "Delivered cooling (kWh)",
                "Estimated electricity (kWh)",
                "Switch changes",
            ]
        ].rename(
            columns={
                "Comfort last half (%)": "Comfort (%)",
                "Humidity in band (%)": "RH in band (%)",
                "Delivered cooling (kWh)": "Cooling (kWh)",
                "Estimated electricity (kWh)": "Electricity (kWh)",
                "Switch changes": "Switches",
            }
        )
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            ui.show_table(
                display,
                height=170,
                formats={
                    "Comfort (%)": "%.1f",
                    "RH in band (%)": "%.1f",
                    "Cooling (kWh)": "%.2f",
                    "Electricity (kWh)": "%.2f",
                },
            )
        with c2:
            pid_row = comparison[comparison["Controller"] == CONTROLLER_PID].iloc[0]
            threshold_row = comparison[
                comparison["Controller"] == CONTROLLER_THRESHOLD
            ].iloc[0]
            ui.callout(
                "Engineering reading",
                (
                    f"PID records {int(pid_row['Switch changes'])} actuator switch changes "
                    f"versus {int(threshold_row['Switch changes'])} for threshold control. "
                    f"Maintained comfort is {pid_row['Comfort last half (%)']:.0f}% and "
                    f"{threshold_row['Comfort last half (%)']:.0f}% respectively. Continuous "
                    "modulation reduces mechanical cycling, while on/off control is simpler "
                    "but produces larger swings."
                ),
                tone="ochre",
            )
        d1, d2 = st.columns(2)
        with d1:
            ui.download_csv(
                simulation.to_frame(),
                filename="hvac_module4_control_timeseries.csv",
                label="Download control time series (CSV)",
                key="m4_download_timeseries",
            )
        with d2:
            ui.download_csv(
                comparison,
                filename="hvac_module4_controller_comparison.csv",
                label="Download controller comparison (CSV)",
                key="m4_download_compare",
            )
    except Exception as exc:  # pragma: no cover - defensive
        ui.error_block(exc)

    with st.expander("Comfort definition, control logic and model limits"):
        st.markdown(
            """
**Effective-temperature proxy.** The dashboard uses
`ET* = T_db + 0.04·(RH − 50)`, anchored so that dry-bulb and ET* coincide at
50% RH. It captures the direction and rough magnitude of humidity's effect on
warmth but is not the full ASHRAE ET*.

**Comfort gate.** A sample is comfortable only when ET* is inside its band and RH
is between 30% and 70%. The relative-humidity band is a project/teaching
criterion supplied with this brief. ASHRAE Standard 55 does not impose one
universal lower RH limit; full compliance requires PMV/PPD with air temperature,
mean radiant temperature, air speed, humidity, clothing and metabolic rate.

**Controllers.** PID uses measurement-based derivative action and
conditional-integration anti-windup. Threshold control uses a deadband and
hysteresis. The chilled-water valve scales rated sensible capacity; the
supply-air actuator blends between minimum and maximum supply temperature.

**Zone model.** A lumped energy balance and moisture balance are integrated at
60 s steps:
`C·dT/dt = Q_internal + UA·(T_out − T_room) + Q_infiltration − Q_cool`.
Latent removal uses a simplified wet-coil bypass model. Thermal mass,
infiltration, internal gains and weather are illustrative rather than a
calibrated building-energy model.
"""
        )
        st.caption(
            "Comfort policy is explicitly educational. For a real design, document the "
            "chosen standard, activity, clothing and local code requirements."
        )
    ui.page_footer()
