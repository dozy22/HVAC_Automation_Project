"""Plotly chart builders for the HVAC design studio.

All figures use a consistent visual language: white plotting surfaces, soft
sage gridlines, deep-teal primary process lines, and terracotta for outdoor /
solar quantities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .ahu import AhuDesignResult, HeatingHumidificationResult
from .controls import SimulationResult, ACTUATOR_VALVE
from .psychrometrics import (
    P_ATM_STD_KPA,
    PsychrometricState,
    humidity_ratio_from_rh,
    relative_humidity_curve,
    saturation_curve,
    wet_bulb_curve_arrays,
)
from .refrigeration import CycleResult, saturation_dome
from .thermal_loads import LoadResult
from .day_sim import DayResult

INK = "#132A27"
MUTED = "#667A75"
GRID = "#E4EBE8"
TEAL = "#0F766E"
TEAL_DARK = "#0B5751"
MINT = "#DDF1EA"
AMBER = "#D99A2B"
AMBER_LIGHT = "#F5E5C6"
TERRACOTTA = "#C96A48"
BLUE = "#2E6F9E"
VIOLET = "#7A5AA6"
GREEN = "#3E8E61"
FONT = "Segoe UI, Inter, Arial, sans-serif"


def _configure(
    figure: go.Figure,
    *,
    height: int = 520,
    legend: bool = True,
    margin: dict[str, int] | None = None,
) -> go.Figure:
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family=FONT, size=13, color=INK),
        margin=margin or dict(l=64, r=28, t=44, b=52),
        hoverlabel=dict(
            bgcolor="#0F2825",
            bordercolor="#0F2825",
            font=dict(color="#FFFFFF", family=FONT, size=12),
        ),
        showlegend=legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11, color=MUTED),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    figure.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
        linecolor=GRID,
    )
    figure.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
        linecolor=GRID,
    )
    return figure


def _comfort_polygon(pressure: float, db_min: float = 23.0, db_max: float = 26.0):
    temps = np.linspace(db_min, db_max, 50)
    low = [humidity_ratio_from_rh(float(t), 30.0, pressure) * 1000.0 for t in temps]
    high = [humidity_ratio_from_rh(float(t), 70.0, pressure) * 1000.0 for t in temps]
    x = list(temps) + list(temps[::-1])
    y = low + high[::-1]
    return x, y


def psychrometric_base(
    pressure_kpa: float = P_ATM_STD_KPA,
    *,
    show_comfort: bool = True,
    show_wet_bulb: bool = True,
    height: int = 560,
) -> go.Figure:
    """Construct the shared ASHRAE-style psychrometric background."""
    temp_min, temp_max = 0.0, 50.0
    w_max_g = 30.0

    fig = go.Figure()
    temps, ws = saturation_curve(temp_min, temp_max, pressure_kpa, 300)
    w_g = ws * 1000.0
    mask = w_g <= w_max_g * 1.05
    fig.add_trace(
        go.Scatter(
            x=temps[mask],
            y=w_g[mask],
            mode="lines",
            name="Saturation",
            line=dict(color=TEAL, width=2.8),
            fill="tozeroy",
            fillcolor="rgba(15,118,110,0.045)",
            hovertemplate="Saturation<br>T=%{x:.1f} degC<br>W=%{y:.2f} g/kg<extra></extra>",
        )
    )

    label_rh = {30, 50, 70}
    for rh in (10, 20, 30, 40, 50, 60, 70, 80, 90):
        t_curve, w_curve = relative_humidity_curve(temp_min, temp_max, rh, pressure_kpa, 240)
        values = w_curve * 1000.0
        keep = (values >= 0) & (values <= w_max_g * 1.015)
        if not np.any(keep):
            continue
        fig.add_trace(
            go.Scatter(
                x=t_curve[keep],
                y=values[keep],
                mode="lines",
                name=f"{rh}% RH",
                line=dict(
                    color="#B5C6C1" if rh not in label_rh else "#8BA49D",
                    width=1.0 if rh not in label_rh else 1.4,
                    dash="dot" if rh not in label_rh else "solid",
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        valid_indices = np.flatnonzero(keep)
        if label_rh and rh in label_rh and len(valid_indices):
            endpoint = valid_indices[-1]
            if t_curve[endpoint] > 2.0:
                fig.add_annotation(
                    x=float(t_curve[endpoint]),
                    y=float(values[endpoint]),
                    text=f"{rh}%",
                    showarrow=False,
                    xshift=6,
                    font=dict(size=10, color=MUTED),
                )

    if show_wet_bulb:
        for wb in (10, 15, 20, 25, 30):
            try:
                t_line, w_line = wet_bulb_curve_arrays(
                    wb, 5.0, 48.0, pressure_kpa, 80
                )
            except ValueError:
                continue
            values = w_line * 1000.0
            keep = (values > 0) & (values <= w_max_g)
            if np.any(keep):
                fig.add_trace(
                    go.Scatter(
                        x=t_line[keep],
                        y=values[keep],
                        mode="lines",
                        name=f"{wb} degC WB",
                        line=dict(color="#CBD6D2", width=0.9, dash="dash"),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

    if show_comfort:
        cx, cy = _comfort_polygon(pressure_kpa)
        fig.add_trace(
            go.Scatter(
                x=cx,
                y=cy,
                mode="lines",
                name="Comfort zone",
                line=dict(color=GREEN, width=1.2, dash="dot"),
                fill="toself",
                fillcolor="rgba(119,183,143,0.22)",
                hovertemplate="Indicative summer comfort zone<br>23-26 degC, 30-70% RH<extra></extra>",
            )
        )

    _configure(fig, height=height)
    fig.update_xaxes(
        title_text="Dry-bulb temperature (degC)",
        range=[temp_min, temp_max],
        dtick=5,
    )
    fig.update_yaxes(
        title_text="Humidity ratio (g water / kg dry air)",
        range=[0, w_max_g],
        dtick=5,
        ticksuffix=" ",
    )
    fig.update_layout(legend=dict(traceorder="normal"))
    return fig


def _add_patient_point(
    fig: go.Figure,
    state: PsychrometricState,
    label: str,
    color: str,
    symbol: str = "circle",
    size: int = 13,
    label_shift: tuple[int, int] = (12, 10),
    name: str | None = None,
) -> None:
    x = state.dry_bulb_c
    y = state.humidity_ratio_g_kg
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            name=name or label,
            showlegend=False,
            marker=dict(
                size=size,
                color=color,
                symbol=symbol,
                line=dict(color="#FFFFFF", width=2),
            ),
            customdata=[[state.relative_humidity_pct, state.enthalpy_kj_kg, state.wet_bulb_c]],
            hovertemplate=(
                f"<b>{label}</b><br>"
                "DBT %{x:.1f} degC<br>"
                "W %{y:.2f} g/kg<br>"
                "RH %{customdata[0]:.1f}%<br>"
                "h %{customdata[1]:.1f} kJ/kg<br>"
                "WBT %{customdata[2]:.1f} degC<extra></extra>"
            ),
        )
    )
    fig.add_annotation(
        x=x,
        y=y,
        text=label,
        showarrow=False,
        xshift=label_shift[0],
        yshift=label_shift[1],
        font=dict(size=12, color=color, family=FONT),
        bgcolor="rgba(255,255,255,0.82)",
        borderpad=2,
    )


def ahu_psychrometric_chart(result: AhuDesignResult, height: int = 585) -> go.Figure:
    """Plot OA/RA mixing, cooling coil, ADP/BPF and room-load line."""
    fig = psychrometric_base(result.room.pressure_kpa, height=height)

    fig.add_trace(
        go.Scatter(
            x=[result.outdoor.dry_bulb_c, result.room.dry_bulb_c],
            y=[result.outdoor.humidity_ratio_g_kg, result.room.humidity_ratio_g_kg],
            mode="lines",
            name="Mixing line",
            line=dict(color="#97AAA5", width=1.4, dash="dot"),
            hovertemplate="Outdoor-to-return mixing locus<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[result.mixed.dry_bulb_c, result.apparatus_dew_point.dry_bulb_c],
            y=[result.mixed.humidity_ratio_g_kg, result.apparatus_dew_point.humidity_ratio_g_kg],
            mode="lines",
            name="Coil process / ADP",
            line=dict(color=BLUE, width=3.0),
            hovertemplate="Cooling and dehumidification<br>T=%{x:.1f} degC<br>W=%{y:.2f} g/kg<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[result.supply.dry_bulb_c, result.room.dry_bulb_c],
            y=[result.supply.humidity_ratio_g_kg, result.room.humidity_ratio_g_kg],
            mode="lines",
            name="Space load (RSHF)",
            line=dict(color=AMBER, width=1.8, dash="dash"),
            hovertemplate="Room sensible-heat-factor line<extra></extra>",
        )
    )

    _add_patient_point(fig, result.outdoor, "OA", TERRACOTTA, "circle", label_shift=(12, 12), name="Outdoor air")
    _add_patient_point(fig, result.room, "RA", TEAL_DARK, "circle", label_shift=(-36, 12), name="Return air")
    _add_patient_point(fig, result.mixed, "MA", AMBER, "diamond", label_shift=(-38, -20), name="Mixed air")
    _add_patient_point(fig, result.supply, "SA", BLUE, "circle", label_shift=(-34, 14), name="Supply air")
    _add_patient_point(
        fig,
        result.apparatus_dew_point,
        "ADP",
        MUTED,
        "circle-open",
        size=15,
        label_shift=(-16, -26),
        name="Apparatus dew point",
    )

    # Direction cues without swallowing the data.
    fig.add_annotation(
        x=result.apparatus_dew_point.dry_bulb_c + 0.2,
        y=result.apparatus_dew_point.humidity_ratio_g_kg + 0.15,
        ax=45,
        ay=45,
        xref="x",
        yref="y",
        axref="pixel",
        ayref="pixel",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.0,
        arrowcolor=BLUE,
        text="",
    )
    fig.add_annotation(
        x=(result.supply.dry_bulb_c + result.room.dry_bulb_c) / 2.0 - 1.3,
        y=(result.supply.humidity_ratio_g_kg + result.room.humidity_ratio_g_kg) / 2.0 + 0.5,
        ax=0,
        ay=-42,
        xref="x",
        yref="y",
        axref="pixel",
        ayref="pixel",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.0,
        arrowcolor=AMBER,
        text="",
    )
    fig.add_annotation(
        x=result.mixed.dry_bulb_c - 1.2,
        y=(result.mixed.humidity_ratio_g_kg + result.supply.humidity_ratio_g_kg) / 2.0,
        text="coil",
        showarrow=False,
        textangle=-65,
        font=dict(size=10, color=BLUE),
    )
    fig.add_annotation(
        x=(result.supply.dry_bulb_c + result.room.dry_bulb_c) / 2.0 + 0.6,
        y=(result.supply.humidity_ratio_g_kg + result.room.humidity_ratio_g_kg) / 2.0 + 0.9,
        text="room load",
        showarrow=False,
        font=dict(size=10, color=AMBER),
    )
    _configure(fig, height=height)
    fig.update_xaxes(title_text="Dry-bulb temperature (degC)", range=[5, 50])
    fig.update_yaxes(title_text="Humidity ratio (g water / kg dry air)", range=[0, 30])
    return fig


def single_state_chart(
    state: PsychrometricState,
    label: str = "Calculated state",
    height: int = 490,
) -> go.Figure:
    fig = psychrometric_base(state.pressure_kpa, show_comfort=True, height=height)
    _add_patient_point(fig, state, label, BLUE, "circle", size=15, label_shift=(14, 10))
    _configure(fig, height=height)
    fig.update_xaxes(title_text="Dry-bulb temperature (degC)", range=[5, 50])
    fig.update_yaxes(title_text="Humidity ratio (g water / kg dry air)", range=[0, 30])
    return fig


def heating_process_chart(
    result: HeatingHumidificationResult,
    height: int = 540,
) -> go.Figure:
    pressure = result.entering.pressure_kpa
    fig = psychrometric_base(pressure, height=height)
    fig.add_trace(
        go.Scatter(
            x=[result.entering.dry_bulb_c, result.heated.dry_bulb_c],
            y=[result.entering.humidity_ratio_g_kg, result.heated.humidity_ratio_g_kg],
            mode="lines",
            name="Sensible heating",
            line=dict(color=TERRACOTTA, width=3.0),
            hovertemplate="Sensible heating (constant W)<br>T=%{x:.1f} degC<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[result.heated.dry_bulb_c, result.leaving.dry_bulb_c],
            y=[result.heated.humidity_ratio_g_kg, result.leaving.humidity_ratio_g_kg],
            mode="lines",
            name="Steam humidification",
            line=dict(color=BLUE, width=3.0, dash="dash"),
            hovertemplate="Controlled humidification<br>W=%{y:.2f} g/kg<extra></extra>",
        )
    )
    _add_patient_point(fig, result.entering, "IN", MUTED, "circle", label_shift=(-34, 12))
    _add_patient_point(fig, result.heated, "HT", TERRACOTTA, "diamond", label_shift=(12, -18))
    _add_patient_point(fig, result.leaving, "OUT", BLUE, "circle", label_shift=(12, 12))
    _configure(fig, height=height)
    fig.update_xaxes(title_text="Dry-bulb temperature (degC)", range=[5, 50])
    fig.update_yaxes(title_text="Humidity ratio (g water / kg dry air)", range=[0, 30])
    return fig


def load_breakdown_chart(result: LoadResult, height: int = 515) -> go.Figure:
    frame = result.component_frame(include_ventilation=True)
    frame = frame[frame["Total (kW)"].abs() > 1e-6].copy()
    frame["Display"] = frame["Item"].where(
        frame["Scope"] == "Room", frame["Item"].str.replace("Outdoor ventilation, ", "OA ", regex=False)
    )
    frame = frame.sort_values("Total (kW)", ascending=True)
    ordered = frame["Display"].tolist()
    colors_scope = {"Room": TEAL, "Outdoor air": AMBER}

    fig = go.Figure()
    for scope in ("Room", "Outdoor air"):
        subset = frame[frame["Scope"] == scope]
        if subset.empty:
            continue
        fig.add_trace(
            go.Bar(
                y=subset["Display"],
                x=subset["Sensible (kW)"],
                orientation="h",
                name=f"{scope} sensible",
                marker=dict(
                    color=colors_scope[scope],
                    line=dict(color="#FFFFFF", width=0),
                ),
                hovertemplate="%{y}<br>Sensible %{x:.2f} kW<extra></extra>",
            )
        )
        fig.add_trace(
            go.Bar(
                y=subset["Display"],
                x=subset["Latent (kW)"],
                orientation="h",
                name=f"{scope} latent",
                marker=dict(
                    color=AMBER_LIGHT if scope == "Outdoor air" else "#9CCFC5",
                    pattern=dict(shape=".", fgcolor="#FFFFFF", fillmode="overlay", size=3),
                ),
                hovertemplate="%{y}<br>Latent %{x:.2f} kW<extra></extra>",
            )
        )
    _configure(fig, height=height)
    fig.update_layout(
        barmode="stack",
        bargap=0.35,
        xaxis_title="Heat gain (kW)",
        legend=dict(traceorder="normal"),
        margin=dict(l=190, r=28, t=44, b=48),
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=ordered,
        tickfont=dict(size=11, color=INK),
        gridcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title_text="Heat gain (kW)")
    return fig


def refrigeration_ph_chart(result: CycleResult, height: int = 560) -> go.Figure:
    states = [result.suction, result.discharge, result.condenser_exit, result.evaporator_inlet]
    pressures = [s.pressure_bar for s in states]
    p_min_plot = max(0.35, min(pressures) * 0.65)
    p_max_plot = max(pressures) * 1.6
    temp_min = max(-35.0, np.log(p_min_plot) * 8 - 25)
    try:
        hf, hg, p_dome = saturation_dome(
            result.fluid,
            temperature_min_c=max(-35.0, temp_min),
            temperature_max_c=min(result.inputs.condensing_c + 25.0, 70.0),
            points=120,
        )
        dome_x = hf + hg[::-1]
        dome_y = p_dome + p_dome[::-1]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dome_x,
                y=dome_y,
                mode="lines",
                fill="toself",
                fillcolor="rgba(197,214,208,0.32)",
                line=dict(color="#9DB5AE", width=1.0),
                name="Saturation dome",
                hoverinfo="skip",
            )
        )
    except ValueError:
        fig = go.Figure()

    point_x = [s.enthalpy_kj_kg for s in states]
    point_y = [s.pressure_bar for s in states]
    fig.add_trace(
        go.Scatter(
            x=point_x + [point_x[0]],
            y=point_y + [point_y[0]],
            mode="lines+markers",
            name="Refrigeration cycle",
            line=dict(color=TEAL, width=3.0),
            marker=dict(
                size=11,
                color=TEAL,
                line=dict(color="#FFFFFF", width=2),
            ),
            customdata=[
                [f"{s.number}", s.temperature_c, s.enthalpy_kj_kg, s.quality]
                for s in states + [states[0]]
            ],
            hovertemplate=(
                "State %{customdata[0]}<br>"
                "T %{customdata[1]:.1f} degC<br>"
                "P %{y:.2f} bar<br>"
                "h %{x:.1f} kJ/kg<extra></extra>"
            ),
        )
    )
    for state, shift in zip(states, [(0, -24), (16, 4), (15, 10), (-22, 10)]):
        fig.add_annotation(
            x=state.enthalpy_kj_kg,
            y=state.pressure_bar,
            text=f"{state.number}",
            showarrow=False,
            xshift=shift[0],
            yshift=shift[1],
            font=dict(size=12, color=TEAL_DARK),
            bgcolor="rgba(255,255,255,0.8)",
            borderpad=2,
        )
    fig.add_trace(
        go.Scatter(
            x=[result.discharge.enthalpy_kj_kg],
            y=[result.discharge.pressure_bar],
            mode="markers",
            name="2s isentropic",
            marker=dict(
                size=9,
                symbol="star",
                color="#FFFFFF",
                line=dict(color=BLUE, width=1.5),
            ),
            hovertemplate="Isentropic discharge<br>T=%{text} degC<extra></extra>",
            text=[f"{result.discharge_isentropic_c:.1f}"],
        )
    )

    _configure(fig, height=height)
    fig.update_yaxes(
        title_text="Pressure (bar, logarithmic)",
        type="log",
        range=[np.log10(p_min_plot), np.log10(p_max_plot)],
        tickformat=".1f",
    )
    fig.update_xaxes(title_text="Refrigerant enthalpy (kJ/kg)")
    fig.update_layout(hovermode="closest")
    return fig


def cycle_sensitivity_chart(
    frame: pd.DataFrame,
    variable: str,
    current_value: float,
    height: int = 430,
) -> go.Figure:
    label = "Superheat (K)" if variable == "superheat_k" else "Subcooling (K)"
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.18,
        row_heights=[0.58, 0.42],
        subplot_titles=("Coefficient of performance", "Compressor discharge temperature"),
    )
    fig.add_trace(
        go.Scatter(
            x=frame[variable],
            y=frame["COP"],
            mode="lines+markers",
            name="COP",
            line=dict(color=TEAL, width=2.5),
            marker=dict(size=6),
            hovertemplate=f"{label} %{{x:.1f}}<br>COP %{{y:.3f}}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=frame[variable],
            y=frame["Discharge temperature C"],
            mode="lines+markers",
            name="Discharge temperature",
            line=dict(color=TERRACOTTA, width=2.3),
            marker=dict(size=6),
            hovertemplate=f"{label} %{{x:.1f}}<br>Discharge T %{{y:.1f}} degC<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_vline(
        x=current_value,
        line=dict(color=AMBER, width=1.4, dash="dash"),
        row=1,
        col=1,
    )
    fig.add_vline(
        x=current_value,
        line=dict(color=AMBER, width=1.4, dash="dash"),
        row=2,
        col=1,
    )
    _configure(fig, height=height, legend=False)
    fig.update_xaxes(title_text=label, row=2, col=1)
    fig.update_yaxes(title_text="COP (-)", row=1, col=1)
    fig.update_yaxes(title_text="degC", row=2, col=1)
    for annotation in fig.layout.annotations:
        annotation.font = dict(size=11, color=MUTED, family=FONT)
    return fig


def _simulation_time_ticks(result: SimulationResult):
    duration = float(result.inputs.duration_h)
    values = np.arange(0.0, duration + 1e-9, 1.0)
    labels = [f"{int((result.inputs.start_hour + v) % 24):02d}:00" for v in values]
    return values, labels


def control_timeline_chart(result: SimulationResult, height: int = 625) -> go.Figure:
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.085,
        row_heights=[0.36, 0.32, 0.32],
        subplot_titles=("Zone temperature", "Relative humidity", "Effective temperature"),
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.outdoor_db_c,
            mode="lines",
            name="Outdoor",
            line=dict(color=TERRACOTTA, width=1.3, dash="dot"),
            hovertemplate="%{y:.1f} degC outdoor<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.room_db_c,
            mode="lines",
            name="Room",
            line=dict(color=TEAL, width=2.8),
            hovertemplate="Room %{y:.2f} degC<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=[result.time_h[0], result.time_h[-1]],
            y=[result.inputs.setpoint_c, result.inputs.setpoint_c],
            mode="lines",
            name="Setpoint",
            line=dict(color=INK, width=1.2, dash="dash"),
            hoverinfo="skip",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.room_rh_pct,
            mode="lines",
            name="Room RH",
            line=dict(color=BLUE, width=2.5),
            hovertemplate="RH %{y:.1f}%<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=result.inputs.comfort.rh_min_pct,
        y1=result.inputs.comfort.rh_max_pct,
        fillcolor="rgba(169,211,186,0.18)",
        line_width=0,
        row=2,
        col=1,
    )
    fig.add_hline(
        y=result.inputs.comfort.rh_min_pct,
        line=dict(color=GREEN, width=0.9, dash="dot"),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=result.inputs.comfort.rh_max_pct,
        line=dict(color=GREEN, width=0.9, dash="dot"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.room_et_c,
            mode="lines",
            name="ET* proxy",
            line=dict(color=VIOLET, width=2.4),
            hovertemplate="ET* %{y:.2f} degC<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_hrect(
        y0=result.inputs.comfort.et_min_c,
        y1=result.inputs.comfort.et_max_c,
        fillcolor="rgba(169,211,186,0.18)",
        line_width=0,
        row=3,
        col=1,
    )
    fig.add_hline(
        y=result.inputs.comfort.et_min_c,
        line=dict(color=GREEN, width=0.9, dash="dot"),
        row=3,
        col=1,
    )
    fig.add_hline(
        y=result.inputs.comfort.et_max_c,
        line=dict(color=GREEN, width=0.9, dash="dot"),
        row=3,
        col=1,
    )

    _configure(fig, height=height, legend=True)
    tick_vals, tick_text = _simulation_time_ticks(result)
    fig.update_xaxes(tickvals=tick_vals, ticktext=tick_text, range=[0, result.inputs.duration_h])
    fig.update_xaxes(title_text="Time of day", row=3, col=1)
    fig.update_yaxes(title_text="degC", row=1, col=1)
    fig.update_yaxes(title_text="%", row=2, col=1, range=[15, 80])
    fig.update_yaxes(title_text="degC", row=3, col=1)
    for annotation in fig.layout.annotations:
        annotation.font = dict(size=11, color=MUTED, family=FONT)
        annotation.x = 0.0
        annotation.xanchor = "left"
    return fig


def control_action_chart(result: SimulationResult, height: int = 320) -> go.Figure:
    is_valve = result.inputs.actuator == ACTUATOR_VALVE
    fig = go.Figure()
    if is_valve:
        fig.add_trace(
            go.Scatter(
                x=result.time_h,
                y=result.valve_pct,
                mode="lines",
                name="Chilled-water valve",
                line=dict(color=AMBER, width=2.2, shape="hv"),
                fill="tozeroy",
                fillcolor="rgba(217,154,43,0.13)",
                hovertemplate="Valve %{y:.0f}%<extra></extra>",
            )
        )
        fig.update_yaxes(title_text="Valve position (%)", range=[-2, 102])
    else:
        fig.add_trace(
            go.Scatter(
                x=result.time_h,
                y=result.supply_db_c,
                mode="lines",
                name="Supply air",
                line=dict(color=AMBER, width=2.2, shape="hv"),
                connectgaps=False,
                hovertemplate="Supply %{y:.1f} degC<extra></extra>",
            )
        )
        fig.update_yaxes(title_text="Supply-air temperature (degC)")
    _configure(fig, height=height, legend=False)
    tick_vals, tick_text = _simulation_time_ticks(result)
    fig.update_xaxes(
        title_text="Time of day",
        tickvals=tick_vals,
        ticktext=tick_text,
        range=[0, result.inputs.duration_h],
    )
    fig.update_layout(margin=dict(l=64, r=28, t=26, b=48))
    return fig


def comfort_map_chart(result: SimulationResult, height: int = 350) -> go.Figure:
    limits = result.inputs.comfort
    fig = go.Figure()
    fig.add_shape(
        type="rect",
        x0=limits.et_min_c,
        x1=limits.et_max_c,
        y0=limits.rh_min_pct,
        y1=limits.rh_max_pct,
        fillcolor="rgba(169,211,186,0.24)",
        line=dict(color=GREEN, width=1.1, dash="dot"),
        layer="below",
    )
    fig.add_trace(
        go.Scatter(
            x=result.room_et_c,
            y=result.room_rh_pct,
            mode="markers",
            name="Comfort trajectory",
            marker=dict(
                size=6,
                color=result.time_h,
                colorscale=[[0, "#B9D8CE"], [0.55, TEAL], [1, "#0B3B35"]],
                colorbar=dict(
                    title=dict(text="Elapsed h", font=dict(size=10)),
                    thickness=9,
                    len=0.72,
                    tickfont=dict(size=9),
                ),
                line=dict(width=0),
            ),
            customdata=np.column_stack([result.room_db_c, result.time_h]),
            hovertemplate=(
                "ET %{x:.2f} degC<br>RH %{y:.1f}%<br>"
                "DBT %{customdata[0]:.1f} degC<br>Hour %{customdata[1]:.1f}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[result.room_et_c[0]],
            y=[result.room_rh_pct[0]],
            mode="markers",
            name="Start",
            marker=dict(size=11, symbol="square", color=TERRACOTTA, line=dict(color="#FFFFFF", width=2)),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[result.room_et_c[-1]],
            y=[result.room_rh_pct[-1]],
            mode="markers+text",
            name="End",
            text=["END"],
            textposition="top center",
            marker=dict(size=12, color=TEAL_DARK, line=dict(color="#FFFFFF", width=2)),
            hoverinfo="skip",
        )
    )
    _configure(fig, height=height, legend=False)
    et_values = np.asarray(result.room_et_c, dtype=float)
    rh_values = np.asarray(result.room_rh_pct, dtype=float)
    x_min = min(limits.et_min_c - 1.0, float(np.nanmin(et_values)) - 0.5)
    x_max = max(limits.et_max_c + 0.8, float(np.nanmax(et_values)) + 0.5)
    y_min = min(limits.rh_min_pct - 10.0, float(np.nanmin(rh_values)) - 4.0)
    y_max = max(limits.rh_max_pct + 8.0, float(np.nanmax(rh_values)) + 4.0)
    fig.update_xaxes(
        title_text="Effective temperature ET* (degC)",
        range=[x_min, x_max],
    )
    fig.update_yaxes(
        title_text="Relative humidity (%)",
        range=[max(5.0, y_min), min(98.0, y_max)],
    )
    fig.update_layout(margin=dict(l=58, r=24, t=20, b=48))
    return fig


# ---------------------------------------------------------------------------
# Quick-design design-day charts
# ---------------------------------------------------------------------------

def _day_ticks() -> tuple[list[float], list[str]]:
    values = list(range(0, 25, 3))
    return [float(value) for value in values], [f"{value:02d}:00" for value in values]


def _shade_system_blocks(figure: go.Figure, result: DayResult) -> None:
    """Shade contiguous system-on blocks behind the data."""
    active = np.asarray(result.available) > 0.5
    start = None
    for index, flag in enumerate(active):
        if flag and start is None:
            start = float(result.time_h[index])
        if start is not None and (not flag or index == len(active) - 1):
            end = float(result.time_h[index])
            if end - start >= 0.1:
                figure.add_vrect(
                    x0=start,
                    x1=end,
                    fillcolor="rgba(15, 118, 110, 0.055)",
                    line_width=0,
                    layer="below",
                )
            start = None


def _peak_marker(figure: go.Figure, result: DayResult, *, y_max: float) -> None:
    figure.add_vline(
        x=result.peak_hour,
        line=dict(color=AMBER, width=1.2, dash="dot"),
    )
    hour = int(round(result.peak_hour))
    figure.add_annotation(
        x=result.peak_hour,
        y=y_max,
        text=f"Peak {hour:02d}:00",
        showarrow=False,
        xshift=10,
        yshift=-3,
        font=dict(size=10, color=AMBER, family=FONT),
        bgcolor="rgba(255,255,255,0.84)",
        borderpad=2,
    )


def day_temperature_chart(result: DayResult, height: int = 420) -> go.Figure:
    fig = go.Figure()
    _shade_system_blocks(fig, result)
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.outdoor_db_c,
            mode="lines",
            name="Outdoor",
            line=dict(color=TERRACOTTA, width=1.5, dash="dot"),
            hovertemplate="Outdoor %{y:.1f} degC<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.room_db_c,
            mode="lines",
            name="Room",
            line=dict(color=TEAL, width=3.0),
            hovertemplate="Room %{y:.2f} degC<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.setpoint_c,
            mode="lines",
            name="Setpoint",
            line=dict(color=INK, width=1.3, dash="dash"),
            hovertemplate="Setpoint %{y:.1f} degC<extra></extra>",
        )
    )
    _configure(fig, height=height)
    tick_values, tick_text = _day_ticks()
    fig.update_xaxes(title_text="Time of day", tickvals=tick_values, ticktext=tick_text, range=[0, 24])
    fig.update_yaxes(title_text="Dry-bulb temperature (degC)")
    y_max = float(np.nanmax(result.outdoor_db_c)) + 1.0
    fig.update_yaxes(range=[18.0, max(31.0, y_max + 1.0)])
    _peak_marker(fig, result, y_max=y_max)
    return fig


def _pull_down_marker(figure: go.Figure, result: DayResult) -> None:
    """Label the morning pre-cool surge when it runs above the load peak."""
    if result.peak_delivered_kw <= result.peak_cooling_kw + 0.5:
        return
    index = int(np.argmax(result.cooling_total_kw))
    hour = float(result.time_h[index])
    if hour >= 12.0:
        return
    figure.add_annotation(
        x=hour,
        y=float(result.cooling_total_kw[index]),
        text="Pre-cool pull-down",
        showarrow=True,
        arrowhead=2,
        arrowwidth=1.1,
        arrowcolor=AMBER,
        ax=64,
        ay=26,
        font=dict(size=10, color=AMBER, family=FONT),
        bgcolor="rgba(255,255,255,0.84)",
        borderpad=2,
    )


def day_cooling_chart(result: DayResult, height: int = 360) -> go.Figure:
    sensible = np.asarray(result.cooling_sensible_kw)
    total = np.asarray(result.cooling_total_kw)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=sensible,
            mode="lines",
            name="Sensible cooling",
            line=dict(color=TEAL, width=1.6),
            fill="tozeroy",
            fillcolor="rgba(15, 118, 110, 0.18)",
            hovertemplate="Sensible %{y:.2f} kW<extra></extra>",
        )
    )
    # The second trace closes the area to the sensible curve.  The amber band
    # between them is the latent share, while the top edge is the total duty.
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=total,
            mode="lines",
            name="Total cooling",
            line=dict(color=AMBER, width=1.4),
            fill="tonexty",
            fillcolor="rgba(217, 154, 43, 0.22)",
            hovertemplate="Total %{y:.2f} kW<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.capacity_kw,
            mode="lines",
            name="Installed capacity",
            line=dict(color=INK, width=1.3, dash="dash"),
            hovertemplate="Capacity %{y:.1f} kW<extra></extra>",
        )
    )
    _configure(fig, height=height)
    tick_values, tick_text = _day_ticks()
    fig.update_xaxes(title_text="Time of day", tickvals=tick_values, ticktext=tick_text, range=[0, 24])
    fig.update_yaxes(title_text="Cooling (kW)", rangemode="tozero")
    _pull_down_marker(fig, result)
    return fig


def day_gain_chart(result: DayResult, height: int = 360) -> go.Figure:
    """Hourly solar, envelope, internal and ventilation sensible gains."""
    hours = np.arange(0, 24, dtype=float)
    step = int(round(len(result.time_h) / 24))
    indices = np.clip((hours * step).astype(int), 0, len(result.time_h) - 1)
    envelope = np.maximum(0.0, result.envelope_kw[indices])
    solar = np.maximum(0.0, result.solar_kw[indices])
    internal = np.maximum(0.0, result.internal_kw[indices])
    ventilation = result.ventilation_kw[indices]

    fig = go.Figure()
    for values, label, color, fill in (
        (envelope, "Envelope", TEAL, "rgba(15, 118, 110, 0.22)"),
        (solar, "Solar through glass", AMBER, "rgba(217, 154, 43, 0.26)"),
        (internal, "People, lighting, equipment", BLUE, "rgba(46, 111, 158, 0.20)"),
    ):
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=values,
                mode="lines",
                name=label,
                stackgroup="gains",
                line=dict(color=color, width=1.1),
                fillcolor=fill,
                hovertemplate=f"{label} %{{y:.2f}} kW<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=ventilation,
            mode="lines",
            name="Outdoor-air ventilation",
            line=dict(color=TERRACOTTA, width=1.6, dash="dot"),
            hovertemplate="Ventilation %{y:.2f} kW<extra></extra>",
        )
    )
    _configure(fig, height=height)
    tick_values, tick_text = _day_ticks()
    fig.update_xaxes(title_text="Hour", tickvals=tick_values, ticktext=tick_text, range=[0, 23])
    fig.update_yaxes(title_text="Sensible gain (kW)", rangemode="tozero")
    return fig


def day_humidity_chart(result: DayResult, height: int = 360) -> go.Figure:
    fig = go.Figure()
    fig.add_hrect(
        y0=30.0,
        y1=70.0,
        fillcolor="rgba(169, 211, 186, 0.20)",
        line_width=0,
        layer="below",
    )
    fig.add_trace(
        go.Scatter(
            x=result.time_h,
            y=result.room_rh_pct,
            mode="lines",
            name="Room RH",
            line=dict(color=BLUE, width=2.5),
            hovertemplate="RH %{y:.1f}%<extra></extra>",
        )
    )
    fig.add_hline(y=30.0, line=dict(color=GREEN, width=0.9, dash="dot"))
    fig.add_hline(y=70.0, line=dict(color=GREEN, width=0.9, dash="dot"))
    fig.add_annotation(
        x=0.4,
        y=66.0,
        text="30-70% comfort band",
        showarrow=False,
        font=dict(size=10, color=GREEN, family=FONT),
    )
    _configure(fig, height=height, legend=False)
    tick_values, tick_text = _day_ticks()
    fig.update_xaxes(title_text="Time of day", tickvals=tick_values, ticktext=tick_text, range=[0, 24])
    fig.update_yaxes(title_text="Relative humidity (%)", range=[20, 85])
    return fig


def day_energy_chart(result: DayResult, height: int = 340) -> go.Figure:
    hours = np.arange(0, 24, dtype=float)
    step = int(round(len(result.time_h) / 24))
    indices = np.clip((hours * step).astype(int), 0, len(result.time_h) - 1)
    electric = result.electric_kw[indices]
    cop = result.design.recommendation.cop_rated
    cop_hours = np.full(24, cop)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=hours,
            y=electric,
            name="Electric demand",
            marker=dict(color="rgba(217, 154, 43, 0.72)", line=dict(width=0)),
            hovertemplate="%{x:.0f}:00 · %{y:.2f} kW<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=cop_hours,
            mode="lines",
            name="Rated COP",
            line=dict(color=TEAL, width=1.4, dash="dot"),
            hovertemplate="Rated COP %{y:.2f}<extra></extra>",
        ),
        secondary_y=True,
    )
    _configure(fig, height=height)
    tick_values, tick_text = _day_ticks()
    fig.update_xaxes(title_text="Hour", tickvals=tick_values, ticktext=tick_text, range=[-0.5, 23.5])
    fig.update_yaxes(title_text="Electric demand (kW)", rangemode="tozero", secondary_y=False)
    fig.update_yaxes(
        title_text="COP (-)",
        range=[0, max(4.5, cop + 0.8)],
        showgrid=False,
        secondary_y=True,
    )
    fig.add_annotation(
        x=23.4,
        y=float(np.max(electric)) * 0.92,
        text=f"{result.electric_energy_kwh:.1f} kWh/day",
        showarrow=False,
        xanchor="right",
        font=dict(size=10, color=MUTED, family=FONT),
    )
    return fig
