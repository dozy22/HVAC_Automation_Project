"""Landing page — system overview and the four-module presentation route."""

from __future__ import annotations

import html

import pandas as pd
from i18n import st_ar as st

import i18n
import ui
from hvac.ahu import AhuDesignResult
from hvac.controls import SimulationResult
from hvac.refrigeration import CycleResult
from hvac.thermal_loads import LoadResult


def _open(page: str) -> None:
    st.session_state["page"] = page


def _module_cards() -> None:
    load = st.session_state.get("load_result")
    ahu = st.session_state.get("ahu_result")
    cycle = st.session_state.get("cycle_result")
    simulation = st.session_state.get("simulation_result")

    if isinstance(load, LoadResult):
        load_result = f"{load.design_total_kw:.1f} kW · {load.design_tr:.2f} TR"
    else:
        load_result = "Awaiting valid inputs"
    if isinstance(ahu, AhuDesignResult):
        ahu_result = f"BPF {ahu.bypass_factor:.2f} · {ahu.coil_total_kw:.1f} kW coil"
    else:
        ahu_result = "Awaiting valid inputs"
    if isinstance(cycle, CycleResult):
        cycle_result = f"COP {cycle.cop:.3f} · {cycle.fluid}"
    else:
        cycle_result = "Awaiting valid inputs"
    if isinstance(simulation, SimulationResult):
        control_result = (
            f"{simulation.comfort_last_half_pct:.0f}% comfort · "
            f"{simulation.switching_count} switches"
        )
    else:
        control_result = "Ready to simulate"

    cards = [
        (
            "01",
            "Chapter 4",
            "Cooling load calculation",
            "Peak envelope, solar, occupancy, lighting and ventilation loads with room sensible heat factor.",
            load_result,
            ui.PAGE_LOADS,
            "loads_open",
        ),
        (
            "02",
            "Chapters 2 & 3",
            "Psychrometrics & AHU",
            "Every moist-air property, adiabatic mixing, coil ADP and bypass factor, heating and humidification.",
            ahu_result,
            ui.PAGE_AHU,
            "ahu_open",
        ),
        (
            "03",
            "Chapter 8",
            "Vapour-compression cycle",
            "Real-fluid P–h cycle, kW and tons, COP, mass flow, superheat and subcooling sensitivity.",
            cycle_result,
            ui.PAGE_REFRIGERATION,
            "refrigeration_open",
        ),
        (
            "04",
            "Chapters 3 & 11",
            "Comfort & automatic control",
            "PID or threshold control of valve position or supply temperature against an ET* and RH comfort gate.",
            control_result,
            ui.PAGE_COMFORT,
            "comfort_open",
        ),
    ]

    columns = st.columns(4, gap="small")
    for column, card in zip(columns, cards):
        index, chapter, title, description, result, page, key = card
        with column:
            st.markdown(
                f"""
<div class="module-card">
<div class="card-top">
<span class="card-number">{index}</span>
<span class="card-chapter">{html.escape(chapter)}</span>
</div>
<h3>{html.escape(title)}</h3>
<p>{html.escape(description)}</p>
<div class="card-result"><span>Last result</span> · {html.escape(result)}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            st.button(
                "Open module",
                key=key,
                on_click=_open,
                args=(page,),
                width="stretch",
                help=f"{i18n.translate_text('Go to')} {i18n.translate_text(title)}.",
            )


def render() -> None:
    load = st.session_state.get("load_result")
    ahu = st.session_state.get("ahu_result")
    cycle = st.session_state.get("cycle_result")
    simulation = st.session_state.get("simulation_result")

    if isinstance(load, LoadResult):
        project = html.escape(load.inputs.project_name)
        load_value = f"{load.design_total_kw:.2f}"
        load_unit = "kW"
        load_foot = f"{load.design_tr:.2f} TR · includes outdoor-air ventilation"
        floor_area = f"{load.floor_area_m2:.0f} m²"
        occupants = f"{load.inputs.occupants} people"
        outdoor = f"{load.outdoor_state.dry_bulb_c:.0f}/{load.outdoor_state.wet_bulb_c:.0f} °C"
        rshf = f"{100 * load.room_rshf:.1f}%"
    else:
        project = "HVAC design studio"
        load_value, load_unit = "—", ""
        load_foot = "Open Module 1 to resolve the design case"
        floor_area = "—"
        occupants = "—"
        outdoor = "—"
        rshf = "—"

    st.markdown(
        f"""
<section class="overview-hero">
<div class="overview-copy">
<div class="eyebrow">Advanced HVAC &amp; Psychrometric Automation</div>
<h1>Air, heat and control<br><em>designed as one system.</em></h1>
<p class="lede">A four-part engineering studio that carries one classroom design case from
cooling load to psychrometric coil, refrigeration plant and closed-loop comfort control.
Every number is calculated live, and every module explains the physics behind it.
A quick studio at the front turns six simple answers into a sized system and a full design day.</p>
<div class="hero-facts">
<span class="hero-fact">Quick studio + 4 modules</span>
<span class="hero-fact">ASHRAE-based moist air</span>
<span class="hero-fact">CoolProp real fluids</span>
<span class="hero-fact">Presentation-ready</span>
</div>
</div>
<div class="overview-aside">
<div class="aside-label">Current design case</div>
<div class="aside-project">{project}</div>
<div class="aside-load"><b>{load_value}</b><span>{load_unit}</span><small>{load_foot}</small></div>
<div class="aside-meta">
<div><span>Floor area</span><b>{floor_area}</b></div>
<div><span>Occupancy</span><b>{occupants}</b></div>
<div><span>Outdoor design</span><b>{outdoor}</b></div>
<div><span>Room RSHF</span><b>{rshf}</b></div>
</div>
</div>
</section>
""",
        unsafe_allow_html=True,
    )

    cycle_cop = cycle.cop if isinstance(cycle, CycleResult) else None
    quick_lead, quick_action = st.columns([3.4, 1], gap="medium")
    with quick_lead:
        ui.callout(
            "New: quick design & simulation",
            (
                "Only know the space, the city and the build quality? Six answers are enough. "
                "The quick studio sizes the cooling, recommends the system and plays the hottest "
                "day back hour by hour."
            ),
            tone="teal",
        )
    with quick_action:
        st.write("")
        st.button(
            "Open the quick studio",
            on_click=_open,
            args=(ui.PAGE_DESIGN,),
            width="stretch",
            help="Start from six simple questions instead of the full engineering input set.",
        )

    air_coil = ahu.coil_total_kw if isinstance(ahu, AhuDesignResult) else None
    comfort = (
        f"{simulation.comfort_last_half_pct:.0f}"
        if isinstance(simulation, SimulationResult)
        else "—"
    )
    comfort_foot = (
        f"{simulation.inputs.controller} · maintained in final half"
        if isinstance(simulation, SimulationResult)
        else "Run Module 4 to populate"
    )
    ui.metric_grid(
        [
            {
                "label": "Peak design load",
                "value": load_value,
                "unit": "kW" if load_unit else "",
                "foot": load_foot if load_unit else "Awaiting a valid Module 1 case",
                "tone": "terra",
                "help": "Room gains plus outdoor-air ventilation at the design condition.",
            },
            {
                "label": "Coil load",
                "value": f"{air_coil:.2f}" if air_coil is not None else "—",
                "unit": "kW" if air_coil is not None else "",
                "foot": (
                    f"ADP {ahu.apparatus_dew_point_c:.1f} °C · BPF {ahu.bypass_factor:.2f}"
                    if isinstance(ahu, AhuDesignResult)
                    else "Open the AHU module"
                ),
                "tone": "teal",
                "help": "Mixing and coil design from Module 2. Can differ from the Module 1 design load when the mixing fraction changes.",
            },
            {
                "label": "Plant COP",
                "value": f"{cycle_cop:.3f}" if cycle_cop is not None else "—",
                "unit": "–" if cycle_cop is not None else "",
                "foot": (
                    f"{cycle.fluid} · η_II {100 * cycle.second_law_efficiency:.1f}%"
                    if isinstance(cycle, CycleResult)
                    else "Open the refrigeration module"
                ),
                "tone": "ochre",
                "help": "Real-fluid vapour-compression cycle coefficient of performance.",
            },
            {
                "label": "Comfort maintained",
                "value": comfort,
                "unit": "%" if comfort != "—" else "",
                "foot": comfort_foot,
                "tone": "green",
                "help": "Percentage of final-half control samples inside both the ET* and 30–70% RH acceptance criteria.",
            },
        ]
    )

    ui.section_heading(
        "The presentation route",
        kicker="Four speakers · one connected case",
        description=(
            "Each speaker owns one calculation layer, but the output of each module becomes "
            "the input of the next. Open any module to recalculate live."
        ),
    )
    _module_cards()

    ui.section_heading(
        "One calculation chain",
        kicker="System architecture",
        description=(
            "The hand-off is deliberately explicit: room states and loads feed the AHU; "
            "the coil duty sizes the refrigeration cycle; the cycle COP informs the "
            "control dashboard."
        ),
    )
    st.markdown(
        """
<div class="process-rail">
<div class="process-step">
<div class="step-index">01 · LOADS</div>
<h4>Room demand</h4>
<p>Envelope, solar, people, lighting, equipment and outdoor air establish sensible and latent load.</p>
</div>
<span class="process-arrow">→</span>
<div class="process-step">
<div class="step-index">02 · AIR</div>
<h4>Coil duty</h4>
<p>Mixing, supply state, ADP and BPF locate the process and establish the coil load.</p>
</div>
<span class="process-arrow">→</span>
<div class="process-step">
<div class="step-index">03 · PLANT</div>
<h4>Refrigeration</h4>
<p>Real-fluid cycle converts coil duty into compressor power, mass flow and COP.</p>
</div>
<span class="process-arrow">→</span>
<div class="process-step">
<div class="step-index">04 · CONTROL</div>
<h4>Comfort loop</h4>
<p>PID or threshold action modulates capacity and holds ET* and RH inside the band.</p>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    ui.section_heading(
        "The design case",
        kicker="Common assumptions",
        description=(
            "A single 96 m² classroom case anchors the presentation. Every module can be "
            "changed independently, and all downstream calculations follow."
        ),
    )
    if isinstance(load, LoadResult):
        case = pd.DataFrame(
            {
                "Parameter": [
                    "Project",
                    "Geometry",
                    "Wall / roof",
                    "Glazing",
                    "Outdoor design",
                    "Indoor design",
                    "Occupancy",
                    "Ventilation",
                    "Internal gains",
                ],
                "Value": [
                    load.inputs.project_name,
                    f"{load.inputs.length_m:.1f} × {load.inputs.width_m:.1f} × {load.inputs.height_m:.1f} m "
                    f"({load.floor_area_m2:.0f} m², {load.volume_m3:.0f} m³)",
                    f"U {load.inputs.wall_u_w_m2k:.2f} / {load.inputs.roof_u_w_m2k:.2f} W/m²·K",
                    f"{load.inputs.window_area_m2:.1f} m², U {load.inputs.window_u_w_m2k:.2f}, "
                    f"SHGC {load.inputs.window_shgc:.2f}",
                    f"{load.inputs.outdoor_db_c:.1f} °C DB / {load.inputs.outdoor_wb_c:.1f} °C WB",
                    f"{load.inputs.indoor_db_c:.1f} °C / {load.inputs.indoor_rh_pct:.0f}% RH",
                    f"{load.inputs.occupants} people · {i18n.option_label(load.inputs.activity_key)}",
                    f"{load.inputs.ventilation_l_s_person:.0f} L/s·person · "
                    f"{load.inputs.infiltration_ach:.2f} ACH infiltration",
                    f"{load.inputs.lighting_w_m2:.1f} W/m² lighting · "
                    f"{load.inputs.equipment_w:.0f} W equipment",
                ],
            }
        )
        c1, c2 = st.columns([1.35, 1], gap="medium")
        with c1:
            ui.show_table(case, height=345)
        with c2:
            ui.callout(
                "How to read the number",
                (
                    f"The room load is {load.room_total_kw:.2f} kW with RSHF "
                    f"{100 * load.room_rshf:.1f}%. The design coil load rises to "
                    f"{load.design_total_kw:.2f} kW ({load.design_tr:.2f} TR) once "
                    f"{load.ventilation_m3_s * 3600:.0f} m³/h of outdoor ventilation air "
                    "is conditioned."
                    "\n\nThe result is a peak steady-state estimate. It is appropriate for "
                    "teaching equipment sizing logic, not for a construction issue without "
                    "hourly load analysis, duct gains and fan heat."
                ),
                tone="ochre",
            )
            brief = ui.design_brief(load, ahu, cycle, simulation)
            ui.download_text(
                brief,
                filename="hvac_design_record.md",
                label="Download live design record (.md)",
                key="overview_download_brief",
                help_text="Current results from every module in one Markdown record.",
            )
    else:
        st.info("Resolve the Module 1 input case to populate the project record.")

    ui.section_heading(
        "Built for a live demonstration",
        kicker="What is under the hood",
        description="",
        rule=False,
    )
    st.markdown(
        """
<div class="info-grid">
<div class="info-tile">
<div class="tile-label">Thermodynamic core</div>
<h4>Properties that close</h4>
<p>Saturation pressure, humidity ratio, enthalpy, specific volume, dew point and wet bulb are mutually consistent at the stated pressure.</p>
</div>
<div class="info-tile">
<div class="tile-label">Plant physics</div>
<h4>Real refrigerant states</h4>
<p>CoolProp resolves every cycle state. Coil ADP is found from the actual saturation-line intersection, not a table lookup.</p>
</div>
<div class="info-tile">
<div class="tile-label">Honest scope</div>
<h4>Teaching model, clear limits</h4>
<p>Steady peak loads and a reduced-order control zone. The comfort proxy and 30–70% RH gate are labelled as project criteria.</p>
</div>
</div>
""",
        unsafe_allow_html=True,
    )
    ui.page_footer()
