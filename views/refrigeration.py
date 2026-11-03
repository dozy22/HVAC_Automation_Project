"""Module 3 — vapour-compression refrigeration cycle with CoolProp."""

from __future__ import annotations

import pandas as pd
from i18n import st_ar as st

import ui
from hvac.ahu import AhuDesignResult
from hvac.charts import cycle_sensitivity_chart, refrigeration_ph_chart
from hvac.refrigeration import (
    REFRIGERANTS,
    CycleInputs,
    compute_cycle,
    sensitivity_sweep,
)
from hvac.thermal_loads import LoadResult

MODULE_FACTS = (
    ("Fluids", "R134a · R410A · R32 · R290"),
    ("Library", "CoolProp real-fluid states"),
    ("Outputs", "kW · TR · COP · mass flow"),
)


def _summary_frame(cycle) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Metric": [
                "Cooling capacity",
                "Cooling capacity",
                "Specific refrigeration effect",
                "Refrigerant mass flow",
                "Volumetric refrigeration effect",
                "Compressor power",
                "Condenser heat rejection",
                "Coefficient of performance",
                "Carnot COP",
                "Second-law efficiency",
                "Pressure ratio",
                "Compressor discharge temperature",
            ],
            "Value": [
                cycle.cooling_kw,
                cycle.cooling_tr,
                cycle.specific_refrigeration_kj_kg,
                cycle.mass_flow_kg_s,
                cycle.volumetric_refrigeration_kj_m3,
                cycle.compressor_kw,
                cycle.condenser_kw,
                cycle.cop,
                cycle.carnot_cop,
                100.0 * cycle.second_law_efficiency,
                cycle.pressure_ratio,
                cycle.discharge.temperature_c,
            ],
            "Unit": [
                "kW",
                "TR",
                "kJ/kg",
                "kg/s",
                "kJ/m³",
                "kW",
                "kW",
                "–",
                "–",
                "%",
                "–",
                "°C",
            ],
        }
    )


def _connected_load() -> tuple[float, str]:
    ahu = st.session_state.get("ahu_result")
    if isinstance(ahu, AhuDesignResult):
        return ahu.coil_total_kw, "Module 2 cooling-coil design load"
    load = st.session_state.get("load_result")
    if isinstance(load, LoadResult):
        return load.design_total_kw, "Module 1 design cooling load"
    return 12.0, "default demonstration load"


def _comparison_frame(base: CycleInputs) -> pd.DataFrame:
    rows = []
    for label, fluid in REFRIGERANTS.items():
        try:
            cycle = compute_cycle(
                CycleInputs(
                    refrigerant=label,
                    evaporating_c=base.evaporating_c,
                    condensing_c=base.condensing_c,
                    superheat_k=base.superheat_k,
                    subcooling_k=base.subcooling_k,
                    isentropic_efficiency=base.isentropic_efficiency,
                    cooling_load_kw=base.cooling_load_kw,
                )
            )
            rows.append(
                {
                    "Refrigerant": label,
                    "COP (–)": cycle.cop,
                    "Compressor (kW)": cycle.compressor_kw,
                    "Mass flow (kg/s)": cycle.mass_flow_kg_s,
                    "Discharge (°C)": cycle.discharge.temperature_c,
                    "Pressure ratio": cycle.pressure_ratio,
                }
            )
        except Exception:
            rows.append(
                {
                    "Refrigerant": label,
                    "COP (–)": None,
                    "Compressor (kW)": None,
                    "Mass flow (kg/s)": None,
                    "Discharge (°C)": None,
                    "Pressure ratio": None,
                }
            )
    return pd.DataFrame(rows).sort_values("COP (–)", ascending=False, na_position="last")


def _sensitivity_panel(cycle) -> None:
    ui.section_heading(
        "Superheat and subcooling sensitivity",
        kicker="Cycle diagnostics",
        description=(
            "Hold the evaporating and condensing temperatures fixed and sweep one "
            "degree-of-superheat variable. The amber marker is the current design point."
        ),
    )
    mode = ui.radio(
        "Sweep variable",
        options=["Subcooling", "Superheat"],
        index=0,
        horizontal=True,
        key="m3_sweep_mode",
        help="Subcooling acts on the liquid line; superheat acts on the suction vapour.",
    )
    variable = "subcooling_k" if mode != "Superheat" else "superheat_k"
    values = [float(v) for v in range(0, 26, 2)]
    try:
        frame = sensitivity_sweep(cycle.inputs, variable, values)
    except Exception as exc:
        ui.error_block(exc, "Try a less extreme liquid or suction condition.")
        return

    current = float(getattr(cycle.inputs, variable))
    chart_col, table_col = st.columns([1, 1.35], gap="medium")
    with chart_col:
        ui.plot(
            cycle_sensitivity_chart(frame, variable, current),
            key=f"m3_sweep_chart_{variable}",
        )
    with table_col:
        variable_label = "Subcooling (K)" if variable == "subcooling_k" else "Superheat (K)"
        display = frame[
            [
                variable,
                "COP",
                "Compressor kW",
                "Mass flow kg/s",
                "Discharge temperature C",
            ]
        ].rename(
            columns={
                variable: variable_label,
                "Compressor kW": "Compressor kW",
                "Mass flow kg/s": "Mass flow kg/s",
                "Discharge temperature C": "Discharge °C",
            }
        )
        ui.panel_title(f"{mode} sweep", "0–25 K")
        ui.show_table(
            display,
            height=360,
            formats={
                "COP": "%.3f",
                "Compressor kW": "%.3f",
                "Mass flow kg/s": "%.4f",
                "Discharge °C": "%.2f",
            },
        )

    first, last = frame.iloc[0], frame.iloc[-1]
    cop_change = 100.0 * (last["COP"] - first["COP"]) / first["COP"]
    flow_change = 100.0 * (last["Mass flow kg/s"] - first["Mass flow kg/s"]) / first["Mass flow kg/s"]
    if variable == "subcooling_k":
        insight = (
            f"Raising subcooling from {first[variable]:.0f} K to {last[variable]:.0f} K "
            f"changes COP by {cop_change:+.2f}% and refrigerant mass flow by {flow_change:+.2f}%. "
            "Subcooling lowers the expansion-inlet enthalpy, so the evaporator produces more "
            "refrigeration per kilogram without changing the compressor pressure ratio."
        )
    else:
        insight = (
            f"Raising superheat from {first[variable]:.0f} K to {last[variable]:.0f} K "
            f"changes COP by {cop_change:+.2f}%, refrigerant mass flow by {flow_change:+.2f}%, "
            f"and discharge temperature from {first['Discharge temperature C']:.1f} °C to "
            f"{last['Discharge temperature C']:.1f} °C. Useful superheat protects the "
            "compressor from liquid slugs, but excessive suction superheat lowers suction "
            "density and increases discharge temperature."
        )
    ui.callout("Engineering reading", insight, tone="ochre")
    ui.download_csv(
        frame,
        filename=f"hvac_module3_{variable}_sweep.csv",
        label=f"Download {mode.lower()} sweep (CSV)",
        key=f"m3_download_{variable}",
    )


def render() -> None:
    ui.page_header(
        index="03",
        module_label="Vapour-compression refrigeration",
        chapter="Chapter 8 · Refrigeration cycles",
        title="Vapour-compression",
        accent="refrigeration",
        description=(
            "Evaluate a real-fluid cycle from evaporator to condenser: capacity in kW and "
            "tons, compressor power, COP, refrigerant mass flow, pressure ratio, superheat "
            "and subcooling. Every state is solved with CoolProp equations of state."
        ),
        facts=MODULE_FACTS,
    )

    connected_kw, connected_source = _connected_load()
    left, right = st.columns([0.95, 1.55], gap="medium")
    with left:
        with st.container(border=True):
            ui.panel_title("Cycle specification", "Design point")
            refrigerant = ui.selectbox(
                "Refrigerant",
                options=list(REFRIGERANTS),
                index=0,
                key="m3_refrigerant",
                help="R134a is the classroom baseline; R410A and R32 are common in modern packaged equipment.",
            )
            t1, t2 = st.columns(2)
            with t1:
                evaporating_c = ui.number_input(
                    "Evaporating temperature (°C)",
                    min_value=-30.0,
                    max_value=20.0,
                    value=2.0,
                    step=1.0,
                    key="m3_evap",
                    help="Saturation temperature in the evaporator. Lower values increase the temperature lift.",
                )
            with t2:
                condensing_c = ui.number_input(
                    "Condensing temperature (°C)",
                    min_value=10.0,
                    max_value=70.0,
                    value=45.0,
                    step=1.0,
                    key="m3_cond",
                    help="Saturation temperature in the condenser. Must stay above the evaporating temperature.",
                )
            s1, s2 = st.columns(2)
            with s1:
                superheat_k = ui.number_input(
                    "Suction superheat (K)",
                    min_value=0.0,
                    max_value=30.0,
                    value=5.0,
                    step=1.0,
                    key="m3_superheat",
                    help="Temperature rise above the evaporating saturation temperature at compressor suction.",
                )
            with s2:
                subcooling_k = ui.number_input(
                    "Liquid subcooling (K)",
                    min_value=0.0,
                    max_value=30.0,
                    value=5.0,
                    step=1.0,
                    key="m3_subcooling",
                    help="Liquid temperature drop below condensing saturation before the expansion valve.",
                )
            isentropic = ui.slider(
                "Isentropic efficiency (–)",
                min_value=0.40,
                max_value=0.95,
                value=0.75,
                step=0.01,
                key="m3_eta",
                help="Ratio of isentropic compression work to actual compressor work.",
            )
            use_connected = ui.toggle(
                "Size cycle from connected system load",
                value=True,
                key="m3_use_connected",
                help="Imports the current coil load from Module 2, or the Module 1 design load if no AHU result exists.",
            )
            if use_connected:
                cooling_load_kw = connected_kw
                ui.number_input(
                    "Cooling capacity (kW)",
                    min_value=1.0,
                    max_value=200.0,
                    value=float(round(connected_kw, 2)),
                    step=0.5,
                    disabled=True,
                    help=f"Source: {connected_source}.",
                )
                st.caption(f"Connected to **{connected_source}**.")
            else:
                cooling_load_kw = ui.number_input(
                    "Cooling capacity (kW)",
                    min_value=1.0,
                    max_value=200.0,
                    value=float(round(connected_kw, 2)),
                    step=0.5,
                    key="m3_manual_load",
                    help="Independent refrigeration capacity for cycle studies.",
                )

    ui.remember_inputs("m3_")
    cycle = None
    error = None
    try:
        cycle = compute_cycle(
            CycleInputs(
                refrigerant=refrigerant,
                evaporating_c=evaporating_c,
                condensing_c=condensing_c,
                superheat_k=superheat_k,
                subcooling_k=subcooling_k,
                isentropic_efficiency=isentropic,
                cooling_load_kw=cooling_load_kw,
            )
        )
        st.session_state["cycle_result"] = cycle
    except Exception as exc:  # pragma: no cover - UI validation path
        error = exc
        # Keep the control dashboard from importing a stale COP.
        st.session_state["cycle_result"] = None

    with right:
        if cycle is not None:
            ui.metric_grid(
                [
                    {
                        "label": "Cooling capacity",
                        "value": f"{cycle.cooling_kw:.2f}",
                        "unit": "kW",
                        "foot": f"{cycle.cooling_tr:.2f} tons of refrigeration",
                        "tone": "teal",
                        "help": "Cooling delivered at the evaporator. One ton of refrigeration equals 3.5169 kW.",
                    },
                    {
                        "label": "Coefficient of performance",
                        "value": f"{cycle.cop:.3f}",
                        "unit": "–",
                        "foot": f"Carnot limit {cycle.carnot_cop:.3f}",
                        "tone": "ochre",
                        "help": "COP = refrigeration effect ÷ compressor work for the real cycle with isentropic efficiency.",
                    },
                    {
                        "label": "Compressor power",
                        "value": f"{cycle.compressor_kw:.2f}",
                        "unit": "kW",
                        "foot": f"Pressure ratio {cycle.pressure_ratio:.2f}",
                        "tone": "terra",
                        "help": "Actual electrical-equivalent shaft power implied by the isentropic efficiency.",
                    },
                    {
                        "label": "Refrigerant mass flow",
                        "value": f"{cycle.mass_flow_kg_s:.4f}",
                        "unit": "kg/s",
                        "foot": f"Specific effect {cycle.specific_refrigeration_kj_kg:.1f} kJ/kg",
                        "tone": "blue",
                        "help": "Mass flow needed to deliver the stated capacity with the computed enthalpy difference.",
                    },
                ]
            )
            ui.chip_row(
                [
                    ("Fluid", cycle.fluid, "teal"),
                    ("Evaporator", f"{cycle.inputs.evaporating_c:.1f} °C · {cycle.evaporator_pressure_kpa:.0f} kPa"),
                    ("Condenser", f"{cycle.inputs.condensing_c:.1f} °C · {cycle.condenser_pressure_kpa:.0f} kPa"),
                    ("Superheat", f"{cycle.inputs.superheat_k:.1f} K"),
                    ("Subcooling", f"{cycle.inputs.subcooling_k:.1f} K"),
                    ("η isentropic", f"{100 * cycle.inputs.isentropic_efficiency:.0f}%"),
                ]
            )
        else:
            ui.error_block(
                error,
                "Keep the condensing temperature at least 3 K above evaporating, stay "
                "below the refrigerant critical temperature, and use a valid capacity.",
            )

    if cycle is None:
        ui.page_footer()
        return

    ui.metric_grid(
        [
            {
                "label": "Condenser rejection",
                "value": f"{cycle.condenser_kw:.2f}",
                "unit": "kW",
                "foot": "Cooling load + compressor work",
                "tone": "blue",
                "help": "Heat rejected at the condenser, equal to evaporator duty plus compressor power in steady state.",
            },
            {
                "label": "Discharge temperature",
                "value": f"{cycle.discharge.temperature_c:.1f}",
                "unit": "°C",
                "foot": f"Isentropic discharge {cycle.discharge_isentropic_c:.1f} °C",
                "tone": "terra",
                "help": "Real compressor discharge temperature after applying the isentropic efficiency.",
            },
            {
                "label": "Second-law efficiency",
                "value": f"{100 * cycle.second_law_efficiency:.1f}",
                "unit": "%",
                "foot": "Real COP ÷ Carnot COP at the same temperatures",
                "tone": "ochre",
                "help": "How closely the real cycle approaches the reversible Carnot limit between the saturation temperatures.",
            },
            {
                "label": "Volumetric capacity",
                "value": f"{cycle.volumetric_refrigeration_kj_m3:.0f}",
                "unit": "kJ/m³",
                "foot": f"Suction density {cycle.suction_density_kg_m3:.2f} kg/m³",
                "tone": "teal",
                "help": "Refrigeration effect per cubic metre of suction vapour; it links capacity to compressor displacement.",
            },
        ]
    )

    ui.section_heading(
        "Pressure–enthalpy cycle",
        kicker="Real-fluid diagram",
        description=(
            "The subcritical saturation dome is drawn from CoolProp saturation data. "
            "State 2 is the actual discharge; 2s is the ideal isentropic endpoint."
        ),
    )
    ui.plot(refrigeration_ph_chart(cycle), key="m3_ph_chart")

    t1, t2 = st.columns([1.45, 1], gap="medium")
    states = cycle.states_table()
    performance = _summary_frame(cycle)
    with t1:
        ui.panel_title("Cycle state points", "1 → 2 → 3 → 4")
        ui.show_table(
            states,
            height=300,
            formats={
                "T (degC)": "%.2f",
                "P (bar)": "%.3f",
                "h (kJ/kg)": "%.2f",
                "s (kJ/kg.K)": "%.4f",
                "Quality": "%.3f",
            },
        )
        ui.download_csv(
            states,
            filename="hvac_module3_cycle_states.csv",
            label="Download cycle states (CSV)",
            key="m3_download_states",
        )
    with t2:
        ui.panel_title("Performance summary", "At design capacity")
        ui.show_table(
            performance,
            height=470,
            formats={"Value": "%.3f"},
        )
        ui.download_csv(
            performance,
            filename="hvac_module3_cycle_performance.csv",
            label="Download cycle performance (CSV)",
            key="m3_download_summary",
        )

    sh_effect = cycle.suction.temperature_c - cycle.inputs.evaporating_c
    sc_effect = cycle.inputs.condensing_c - cycle.condenser_exit.temperature_c
    ui.callout(
        "Engineering reading",
        (
            f"At {cycle.inputs.evaporating_c:.1f} °C evaporating and "
            f"{cycle.inputs.condensing_c:.1f} °C condensing, the cycle reaches COP "
            f"{cycle.cop:.3f} against a Carnot ceiling of {cycle.carnot_cop:.3f}. "
            f"The compressor rejects {cycle.condenser_kw:.2f} kW at the condenser and "
            f"requires {cycle.mass_flow_kg_s:.4f} kg/s of {cycle.fluid}."
            f"\n\nMeasured model superheat is {sh_effect:.1f} K and subcooling is "
            f"{sc_effect:.1f} K. Subcooling buys refrigeration effect after the condenser; "
            "suction superheat protects the compressor but lowers suction density and raises "
            "discharge temperature."
        ),
        tone="ochre",
    )

    _sensitivity_panel(cycle)

    with st.expander("Screen all refrigerants at this operating point"):
        st.caption(
            "Same saturation temperatures, superheat, subcooling and isentropic efficiency. "
            "This screening compares thermodynamics only; flammability, GWP, lubricant and "
            "safety classification must be assessed separately."
        )
        compare = ui.toggle(
            "Run the six-fluid comparison",
            value=False,
            key="m3_compare",
            help="Computes each supported refrigerant at the current evaporating and condensing temperatures.",
        )
        if compare:
            comparison = _comparison_frame(cycle.inputs)
            ui.show_table(
                comparison,
                height=280,
                formats={
                    "COP (–)": "%.3f",
                    "Compressor (kW)": "%.3f",
                    "Mass flow (kg/s)": "%.4f",
                    "Discharge (°C)": "%.2f",
                    "Pressure ratio": "%.2f",
                },
            )
            ui.download_csv(
                comparison,
                filename="hvac_module3_refrigerant_screen.csv",
                label="Download refrigerant screening (CSV)",
                key="m3_download_compare",
            )

    ui.remember_inputs("m3_")
    with st.expander("Cycle equations and modelling assumptions"):
        st.markdown(
            "State 1 is superheated suction vapour, 2 is actual discharge, 3 is subcooled "
            "liquid at condenser pressure, and 4 is the isenthalpic expansion outlet."
        )
        st.latex(r"q_{evap} = h_1 - h_4")
        st.latex(r"w_{comp} = h_2 - h_1")
        st.latex(r"COP = \frac{q_{evap}}{w_{comp}}")
        st.latex(r"COP_{Carnot} = \frac{T_{evap}}{T_{cond} - T_{evap}}")
        st.caption(
            "Temperatures in the Carnot expression are absolute. Compressor, piping and "
            "motor losses beyond the entered isentropic efficiency are not modelled. "
            "Heat rejection assumes steady state with no ambient losses."
        )
    ui.page_footer()
