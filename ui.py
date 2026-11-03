"""Shared UI primitives, navigation and session-state helpers."""

from __future__ import annotations

from datetime import datetime
from functools import partial
import html
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import i18n
from hvac.ahu import AhuDesignResult, design_ahu
from hvac.controls import SimulationResult
from hvac.psychrometrics import PsychrometricState, moist_air_specific_heat
from hvac.quick_design import QuickInputs, build_quick_design
from hvac.refrigeration import CycleInputs, CycleResult, compute_cycle
from hvac.thermal_loads import LoadResult, calculate_thermal_load, default_load_inputs

PROJECT_ROOT = Path(__file__).resolve().parent
CSS_PATH = PROJECT_ROOT / "assets" / "style.css"
DESIGN_CSS_PATH = PROJECT_ROOT / "assets" / "design.css"
DARK_CSS_PATH = PROJECT_ROOT / "assets" / "theme_dark.css"
RTL_CSS_PATH = PROJECT_ROOT / "assets" / "rtl.css"

PAGE_OVERVIEW = "Overview"
PAGE_DESIGN = "Design & simulation"
PAGE_LOADS = "01 - Cooling load"
PAGE_AHU = "02 - Psychrometrics & AHU"
PAGE_REFRIGERATION = "03 - Refrigeration cycle"
PAGE_COMFORT = "04 - Comfort control"

NAV_PAGES = (
    PAGE_OVERVIEW,
    PAGE_DESIGN,
    PAGE_LOADS,
    PAGE_AHU,
    PAGE_REFRIGERATION,
    PAGE_COMFORT,
)

PLOT_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": [
        "lasso2d",
        "select2d",
        "autoScale2d",
        "toggleSpikelines",
    ],
}


def load_css() -> None:
    """Load the paper theme, then the optional dark and RTL layers.

    Streamlit's own theme is fixed when the server starts.  The studio therefore
    treats the base stylesheet as the light theme and layers a matching dark
    stylesheet on top, which keeps the switch instantaneous and testable.
    """
    layers = [CSS_PATH, DESIGN_CSS_PATH]
    if i18n.dark_mode():
        layers.append(DARK_CSS_PATH)
    if i18n.is_arabic():
        layers.append(RTL_CSS_PATH)
    for path in layers:
        if path.exists():
            st.markdown(f"<style>{path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


INPUT_PREFS_KEY = "input_prefs"
_MISSING = object()
_MANAGED_INPUTS: set[str] = set()


def _input_prefs() -> dict:
    return st.session_state.setdefault(INPUT_PREFS_KEY, {})


def _widget_default(key: str | None, default):
    """Default for a widget that must survive page switches.

    Streamlit keeps a widget's value only while that widget is rendered.  When
    another page runs, the widget key is pruned.  A separate preference map
    lets the next visit rebuild the widget with the value the user last chose,
    in the front end and the back end alike.
    """
    if not key:
        return default
    _MANAGED_INPUTS.add(key)
    if key in st.session_state:
        return st.session_state[key]
    return _input_prefs().get(key, default)


def remember_inputs(prefix: str) -> None:
    """Snapshot the live widget values for one module into durable preferences."""
    prefs = _input_prefs()
    for key in _MANAGED_INPUTS:
        if key.startswith(prefix) and key in st.session_state:
            prefs[key] = st.session_state[key]


def _tr(text):
    return i18n.translate_text(text) if isinstance(text, str) else text


def _translate_kwargs(kwargs: dict) -> dict:
    if isinstance(kwargs.get("help"), str):
        kwargs["help"] = _tr(kwargs["help"])
    return kwargs


def _choice_format(existing=None):
    """Compose the Arabic option label with any caller-supplied formatter."""
    if not i18n.is_arabic():
        return existing
    if existing is None:
        return i18n.option_label

    def combined(value):
        rendered = existing(value)
        return _tr(rendered) if isinstance(rendered, str) else str(rendered)

    return combined


def number_input(label: str, *, key: str | None = None, value=_MISSING, **kwargs):
    if value is _MISSING:
        raise TypeError(f"ui.number_input needs an explicit default for {label!r}")
    return st.number_input(
        _tr(label),
        value=_widget_default(key, value),
        key=key,
        **_translate_kwargs(kwargs),
    )


def slider(label: str, *, key: str | None = None, value=_MISSING, **kwargs):
    if value is _MISSING:
        raise TypeError(f"ui.slider needs an explicit default for {label!r}")
    return st.slider(
        _tr(label),
        value=_widget_default(key, value),
        key=key,
        **_translate_kwargs(kwargs),
    )


def selectbox(label: str, options, *, key: str | None = None, index: int = 0, **kwargs):
    choices = list(options)
    if key:
        fallback = choices[index] if 0 <= index < len(choices) else choices[0]
        current = _widget_default(key, fallback)
        index = choices.index(current) if current in choices else index
    format_func = _choice_format(kwargs.pop("format_func", None))
    if format_func is not None:
        kwargs["format_func"] = format_func
    return st.selectbox(
        _tr(label),
        choices,
        index=index,
        key=key,
        **_translate_kwargs(kwargs),
    )


def radio(label: str, options, *, key: str | None = None, index: int = 0, **kwargs):
    choices = list(options)
    if key:
        fallback = choices[index] if 0 <= index < len(choices) else choices[0]
        current = _widget_default(key, fallback)
        index = choices.index(current) if current in choices else index
    format_func = _choice_format(kwargs.pop("format_func", None))
    if format_func is not None:
        kwargs["format_func"] = format_func
    return st.radio(
        _tr(label),
        choices,
        index=index,
        key=key,
        **_translate_kwargs(kwargs),
    )


def toggle(label: str, *, key: str | None = None, value: bool = False, **kwargs):
    return st.toggle(
        _tr(label),
        value=bool(_widget_default(key, value)),
        key=key,
        **_translate_kwargs(kwargs),
    )


def text_input(label: str, *, key: str | None = None, value: str = "", **kwargs):
    return st.text_input(
        _tr(label),
        value=_widget_default(key, value),
        key=key,
        **_translate_kwargs(kwargs),
    )


def init_state() -> None:
    """Seed a complete demonstration case on the first application load."""
    st.session_state.setdefault(i18n.LANGUAGE_KEY, i18n.DEFAULT_LANGUAGE)
    st.session_state.setdefault(i18n.THEME_KEY, False)
    st.session_state.setdefault("page", PAGE_OVERVIEW)
    if "load_result" not in st.session_state:
        result = calculate_thermal_load(default_load_inputs())
        st.session_state["load_result"] = result
    load = st.session_state.get("load_result")
    if "ahu_result" not in st.session_state and isinstance(load, LoadResult):
        try:
            cp = moist_air_specific_heat(load.indoor_state.humidity_ratio)
            supply_c = 13.0
            mass = load.room_sensible_kw / (
                cp * max(0.5, load.indoor_state.dry_bulb_c - supply_c)
            )
            fraction = load.ventilation_mass_kg_s / mass if mass > 0 else 0.20
            fraction = min(0.90, max(0.02, fraction))
            st.session_state["ahu_result"] = design_ahu(
                load.indoor_state,
                load.outdoor_state,
                load.room_sensible_kw,
                load.room_latent_kw,
                supply_c,
                fraction,
            )
        except Exception:
            st.session_state["ahu_result"] = None
    if "cycle_result" not in st.session_state:
        try:
            load_kw = (
                load.design_total_kw if isinstance(load, LoadResult) else 12.0
            )
            st.session_state["cycle_result"] = compute_cycle(
                CycleInputs(cooling_load_kw=load_kw)
            )
        except Exception:
            st.session_state["cycle_result"] = None
    st.session_state.setdefault("simulation_result", None)
    st.session_state.setdefault("quick_design", None)
    st.session_state.setdefault("day_result", None)


def _go_to(page: str) -> None:
    st.session_state["page"] = page


def sidebar() -> str:
    with st.sidebar:
        st.markdown(
            f"""
<div class="side-brand">
<div class="side-mark">H</div>
<div>
<div class="side-title">{_tr("HVAC Design Studio")}</div>
<div class="side-sub">{_tr("Psychrometrics · Loads")}<br>{_tr("Control &amp; Comfort")}</div>
</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="side-label">{_tr("Language")} · {_tr("Appearance")}</div>',
            unsafe_allow_html=True,
        )
        st.selectbox(
            _tr("Language"),
            options=[i18n.LANG_AR, i18n.LANG_EN],
            format_func=lambda code: i18n.LANGUAGE_LABELS.get(code, code),
            key=i18n.LANGUAGE_KEY,
            label_visibility="collapsed",
            help=_tr("Choose the language of the interface. Calculations are unchanged."),
        )
        st.toggle(
            _tr("Dark mode"),
            key=i18n.THEME_KEY,
            help=_tr(
                "Switch between the warm paper theme and a low-light drawing-board theme."
            ),
        )
        st.markdown(
            f'<div class="side-label">{_tr("Workspace")}</div>',
            unsafe_allow_html=True,
        )
        # Bind the language now: format_func may also be evaluated outside the
        # script run, where reading session state would fall back to Arabic.
        page_label = partial(i18n.page_label, arabic=i18n.is_arabic())
        page = st.radio(
            _tr("Workspace page"),
            NAV_PAGES,
            key="page",
            format_func=page_label,
            label_visibility="collapsed",
        )

        load = st.session_state.get("load_result")
        snapshot_label = _tr("Live design case")
        if page == PAGE_DESIGN:
            # The quick studio has its own case.  Rebuild it from the current
            # widget state so the sidebar never shows the detailed Module 1
            # numbers beside a different quick answer.
            try:
                quick = build_quick_design(QuickInputs.from_state(st.session_state))
            except (ValueError, KeyError):
                quick = None
            if quick is not None:
                load = quick.load
                snapshot_label = _tr("Quick design case")
        if isinstance(load, LoadResult):
            project = html.escape(load.inputs.project_name)
            if len(project) > 26:
                project = project[:23] + "..."
            snapshot = f"""
<div class="side-snapshot">
<div class="snap-label">{snapshot_label}</div>
<div class="snap-value">{load.design_total_kw:.1f} {_tr("kW")} <small>{load.design_tr:.2f} {_tr("TR")}</small></div>
<div class="snap-grid">
<div><span>{_tr("Space")}</span><b>{load.floor_area_m2:.0f} {_tr("m²")}</b></div>
<div><span>RSHF</span><b>{100 * load.room_rshf:.1f}%</b></div>
<div><span>{_tr("OA flow")}</span><b>{load.ventilation_m3_s * 3600:.0f} m³/h</b></div>
<div class="snap-case"><span>{_tr("Case")}</span><b title="{project}">{project}</b></div>
</div>
</div>
"""
            st.markdown(snapshot, unsafe_allow_html=True)

        st.markdown(
            f'<div class="side-label" style="margin-top:1.3rem;">{_tr("Session")}</div>',
            unsafe_allow_html=True,
        )
        st.button(
            _tr("Reset workspace"),
            on_click=_reset_workspace,
            help=_tr("Return every module to the prepared classroom demonstration case."),
            width="stretch",
        )
        st.markdown(
            f"""
<div class="side-footer">
{_tr("Advanced HVAC &amp; Psychrometric Automation")}<br>
{_tr("B.Sc. Mechanical Engineering · 2026")}<br>
{_tr("Built with Python · Streamlit · CoolProp")}
<div class="side-credit">{_tr("Designed by (HALF ENGINEERS)")}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    return page


def _reset_workspace() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(("m1_", "m2_", "m3_", "m4_", "qd_")):
            del st.session_state[key]
    for key in (
        "load_result",
        "ahu_result",
        "cycle_result",
        "simulation_result",
        "quick_design",
        "day_result",
        INPUT_PREFS_KEY,
    ):
        st.session_state.pop(key, None)
    st.session_state["page"] = PAGE_OVERVIEW


def page_header(
    *,
    index: str,
    module_label: str,
    chapter: str,
    title: str,
    accent: str = "",
    description: str = "",
    facts: Sequence[tuple[str, str]] = (),
) -> None:
    fact_html = "".join(
        f'<span class="hero-fact">{html.escape(_tr(label))} <b>{html.escape(_tr(value))}</b></span>'
        for label, value in facts
    )
    accent_html = f" <em>{html.escape(_tr(accent))}</em>" if accent else ""
    st.markdown(
        f"""
<section class="module-hero" data-index="{html.escape(index)}">
<div class="hero-kicker">
<span class="module-label">{_tr("Module")} {html.escape(index)}</span>
<span class="chapter">{html.escape(_tr(chapter))}</span>
</div>
<h1>{html.escape(_tr(title))}{accent_html}</h1>
<p class="hero-description">{html.escape(_tr(description))}</p>
<div class="hero-facts">{fact_html}</div>
</section>
""",
        unsafe_allow_html=True,
    )


def section_heading(
    title: str,
    *,
    kicker: str = "",
    description: str = "",
    rule: bool = True,
) -> None:
    kicker_html = f'<div class="section-kicker">{html.escape(_tr(kicker))}</div>' if kicker else ""
    description_html = f"<p>{html.escape(_tr(description))}</p>" if description else ""
    rule_html = '<div class="section-rule"></div>' if rule else ""
    st.markdown(
        f"""
<div class="section-head">
{kicker_html}
<h2>{html.escape(_tr(title))}</h2>
{description_html}
{rule_html}
</div>
""",
        unsafe_allow_html=True,
    )


def panel_title(title: str, aside: str = "") -> None:
    st.markdown(
        f"""
<div class="panel-title"><b>{html.escape(_tr(title))}</b><span>{html.escape(_tr(aside))}</span></div>
""",
        unsafe_allow_html=True,
    )


def metric_grid(
    items: Sequence[dict],
    *,
    columns: int = 4,
    gap: str = "0.75rem",
) -> None:
    cards = []
    for item in items:
        tone = item.get("tone", "teal")
        help_text = item.get("help", "")
        info = (
            f'<span class="info-dot" title="{html.escape(_tr(help_text), quote=True)}">i</span>'
            if help_text
            else ""
        )
        value = html.escape(str(item.get("value", "-")))
        unit = html.escape(str(_tr(item.get("unit", ""))))
        unit_html = f'<span class="kpi-unit">{unit}</span>' if unit else ""
        foot = html.escape(str(_tr(item.get("foot", ""))))
        cards.append(
            f"""
<div class="kpi kpi--{tone}">
<div class="kpi-top"><span class="kpi-label">{html.escape(_tr(str(item.get("label", ""))))}</span>{info}</div>
<div class="kpi-value">{value}{unit_html}</div>
<div class="kpi-foot">{foot}</div>
</div>
"""
        )
    st.markdown(
        f'<div class="kpi-grid" style="grid-template-columns:repeat({int(columns)},minmax(0,1fr));gap:{gap};">'
        + "".join(cards)
        + "</div>",
        unsafe_allow_html=True,
    )


def chip_row(items: Iterable[tuple[str, str] | tuple[str, str, str]]) -> None:
    chips = []
    for item in items:
        label, value = item[0], item[1]
        tone = item[2] if len(item) > 2 else ""
        tone_class = f" chip--{tone}" if tone else ""
        value_html = f" <b>{html.escape(_tr(str(value)))}</b>" if value else ""
        chips.append(
            f'<span class="chip{tone_class}">{html.escape(_tr(str(label)))}{value_html}</span>'
        )
    st.markdown('<div class="chip-row">' + "".join(chips) + "</div>", unsafe_allow_html=True)


def callout(title: str, body: str, *, tone: str = "") -> None:
    tone_class = f" {tone}" if tone else ""
    paragraphs = "".join(
        f"<p>{_tr(part)}</p>" for part in body.split("\n\n") if part.strip()
    )
    st.markdown(
        f"""
<div class="callout{tone_class}">
<div>
<h4>{html.escape(_tr(title))}</h4>
{paragraphs}
</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _apply_dark_chart(figure: go.Figure) -> go.Figure:
    """Repaint a light drawing-board figure for the dark studio theme."""
    dark_text = "#DCE8E3"
    dark_muted = "#9DB4AC"
    dark_grid = "rgba(196, 222, 213, 0.14)"
    dark_surface = "#12201E"
    light_inks = {"#132a27", "#294640", "#667a75", "#e4ebe8"}

    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=dark_surface,
        font=dict(color=dark_text),
        hoverlabel=dict(
            bgcolor="#E9F1ED",
            bordercolor="#E9F1ED",
            font=dict(color="#132A27"),
        ),
        legend=dict(font=dict(color=dark_muted)),
    )
    if getattr(figure.layout, "title", None) is not None:
        figure.layout.title.font = dict(color=dark_text)
    figure.update_xaxes(
        gridcolor=dark_grid,
        linecolor=dark_grid,
        tickfont=dict(color=dark_muted),
        title_font=dict(color=dark_muted),
    )
    figure.update_yaxes(
        gridcolor=dark_grid,
        linecolor=dark_grid,
        tickfont=dict(color=dark_muted),
        title_font=dict(color=dark_muted),
    )

    for trace in figure.data:
        line = getattr(trace, "line", None)
        if line is not None and isinstance(getattr(line, "color", None), str):
            if line.color.lower() in light_inks:
                line.color = dark_muted
        textfont = getattr(trace, "textfont", None)
        if textfont is not None and isinstance(getattr(textfont, "color", None), str):
            if textfont.color.lower() in light_inks:
                textfont.color = dark_text
        marker = getattr(trace, "marker", None)
        if marker is not None:
            if isinstance(getattr(marker, "color", None), str) and marker.color.lower() in light_inks:
                marker.color = dark_text
            marker_line = getattr(marker, "line", None)
            if marker_line is not None and isinstance(getattr(marker_line, "color", None), str):
                if marker_line.color.lower() in light_inks:
                    marker_line.color = dark_surface

    for annotation in getattr(figure.layout, "annotations", ()) or ():
        if annotation.font is not None and isinstance(annotation.font.color, str):
            if annotation.font.color.lower() in light_inks:
                annotation.font.color = dark_muted
        if isinstance(annotation.bgcolor, str):
            lowered = annotation.bgcolor.lower().replace(" ", "")
            if lowered.startswith("rgba(255,255,255") or lowered in {"#fff", "#ffffff"}:
                annotation.bgcolor = "rgba(18, 32, 30, 0.88)"
        if isinstance(getattr(annotation, "bordercolor", None), str):
            if annotation.bordercolor.lower() in light_inks:
                annotation.bordercolor = dark_grid
    return figure


def plot(figure: go.Figure, *, key: str | None = None) -> None:
    local = i18n.localise_figure(figure)
    if i18n.dark_mode():
        local = _apply_dark_chart(local)
    st.plotly_chart(
        local,
        theme=None,
        config=PLOT_CONFIG,
        key=key,
    )


def _formatted_cell(value, fmt: str | None):
    if fmt and isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return fmt % value
        except (TypeError, ValueError):
            return value
    return value


def show_table(
    frame: pd.DataFrame,
    *,
    height: int | str = "auto",
    formats: dict[str, str] | None = None,
    hide_index: bool = True,
) -> None:
    """Render a themed, bilingual table that follows dark mode and RTL.

    Streamlit's dataframe uses its own fixed light grid, so the studio draws a
    compact HTML table instead.  This keeps the engineering values selectable
    and lets Arabic headers and dark surfaces match the rest of the page.
    """
    display = frame.copy()
    if formats:
        for column, fmt in formats.items():
            if column in display.columns:
                display[column] = display[column].map(lambda value, f=fmt: _formatted_cell(value, f))
    display = i18n.localise_frame(display)

    numeric_columns = [
        pd.api.types.is_numeric_dtype(frame.iloc[:, index])
        and not pd.api.types.is_bool_dtype(frame.iloc[:, index])
        for index in range(len(frame.columns))
    ]
    head = "".join(f"<th scope=\"col\">{html.escape(str(column))}</th>" for column in display.columns)
    body_rows = []
    for _, row in display.iterrows():
        cells = []
        for index, value in enumerate(row):
            empty = value is None or (isinstance(value, float) and pd.isna(value))
            rendered = "—" if empty else html.escape(str(value))
            numeric = numeric_columns[index] if index < len(numeric_columns) else False
            css = ' class="num"' if numeric else ""
            direction = ' dir="ltr"' if numeric else ""
            cells.append(f"<td{css}{direction}>{rendered}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    style = f' style="max-height:{int(height)}px;"' if isinstance(height, (int, float)) else ""
    table_html = (
        f'<div class="data-table-wrap"{style}>'
        f'<table class="data-table"><thead><tr>{head}</tr></thead>'
        f"<tbody>{''.join(body_rows)}</tbody></table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


def download_csv(
    frame: pd.DataFrame,
    *,
    filename: str,
    label: str,
    key: str,
    help_text: str = "",
) -> None:
    export = i18n.localise_frame(frame)
    st.download_button(
        _tr(label),
        data=export.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv",
        key=key,
        help=_tr(help_text) or None,
        width="stretch",
    )


def download_text(
    text: str,
    *,
    filename: str,
    label: str,
    key: str,
    help_text: str = "",
) -> None:
    st.download_button(
        _tr(label),
        data=text.encode("utf-8"),
        file_name=filename,
        mime="text/markdown",
        key=key,
        help=_tr(help_text) or None,
        width="stretch",
    )


def error_block(error: Exception, hint: str = "") -> None:
    message = str(error) or error.__class__.__name__
    st.error(f"{_tr('Design check')}: {_tr(message)}")
    if hint:
        st.caption(_tr(hint))


def state_chip_items(state: PsychrometricState) -> list[tuple[str, str, str]]:
    return [
        ("DBT", f"{state.dry_bulb_c:.1f} °C", "teal"),
        ("WBT", f"{state.wet_bulb_c:.1f} °C", ""),
        ("RH", f"{state.relative_humidity_pct:.1f} %", ""),
        ("W", f"{state.humidity_ratio_g_kg:.2f} g/kg", ""),
        ("h", f"{state.enthalpy_kj_kg:.1f} kJ/kg", "ochre"),
        ("v", f"{state.specific_volume_m3_kg:.3f} m³/kg", ""),
    ]


def page_footer() -> None:
    st.markdown(
        f"""
<div class="page-footer">
<span>{_tr("Advanced HVAC & Psychrometric Automation System")}</span>
<span>{_tr("Educational design tool · Verify final equipment selections against project standards")}</span>
<span class="footer-credit">{_tr("Designed by (HALF ENGINEERS)")}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def design_brief(
    load: LoadResult | None,
    ahu: AhuDesignResult | None,
    cycle: CycleResult | None,
    simulation: SimulationResult | None,
) -> str:
    """Generate a compact, presentation-ready Markdown design record."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if i18n.is_arabic():
        lines = [
            "# استوديو تصميم HVAC — سجل الحسابات",
            "",
            f"أُنشئ في: {stamp}",
            "",
            "هذا السجل ملخص تعليمي. يجب التحقق من اختيار المعدات النهائي بواسطة",
            "مهندس مؤهل وفق الكود المعمول به وموجز المشروع.",
            "",
        ]
        if isinstance(load, LoadResult):
            lines += [
                "## 1. حمل التبريد الأقصى (طريقة الفصل 4)",
                "",
                f"- المشروع: {load.inputs.project_name}",
                f"- المساحة: {load.floor_area_m2:.1f} م²، الحجم {load.volume_m3:.1f} م³",
                f"- ظرف التصميم الخارجي: {load.inputs.outdoor_db_c:.1f} °C جافة / "
                f"{load.inputs.outdoor_wb_c:.1f} °C رطبة",
                f"- الظرف الداخلي: {load.inputs.indoor_db_c:.1f} °C / "
                f"{load.inputs.indoor_rh_pct:.1f}% رطوبة نسبية",
                f"- الحمل المحسوس للغرفة: {load.room_sensible_kw:.2f} kW",
                f"- الحمل الكامن للغرفة: {load.room_latent_kw:.2f} kW",
                f"- عامل الحرارة المحسوسة للغرفة (RSHF): {100 * load.room_rshf:.1f}%",
                f"- حمل تهوية الهواء الخارجي: {load.ventilation_total_kw:.2f} kW",
                f"- حمل ملف التبريد التصميمي شامل الهواء الخارجي: {load.design_total_kw:.2f} kW "
                f"({load.design_tr:.2f} TR)",
                "",
            ]
        if isinstance(ahu, AhuDesignResult):
            lines += [
                "## 2. العملية السيكرومترية ووحدة مناولة الهواء (الفصلان 2–3)",
                "",
                f"- نسبة كتلة الهواء الخارجي: {100 * ahu.outdoor_air_fraction:.1f}%",
                f"- الهواء المخلوط: {ahu.mixed.dry_bulb_c:.2f} °C جافة، "
                f"{ahu.mixed.relative_humidity_pct:.1f}% رطوبة نسبية",
                f"- هواء الإمداد: {ahu.supply.dry_bulb_c:.2f} °C جافة، "
                f"{ahu.supply.relative_humidity_pct:.1f}% رطوبة نسبية",
                f"- التدفق الكتلي للهواء الجاف المورد: {ahu.supply_mass_flow_kg_s:.3f} kg/s",
                f"- نقطة الندى الظاهرية للملف: {ahu.apparatus_dew_point_c:.2f} °C",
                f"- عامل التجاوز: {ahu.bypass_factor:.3f}",
                f"- حمل الملف: {ahu.coil_total_kw:.2f} kW إجمالي، "
                f"SHR {100 * ahu.coil_shr:.1f}%",
                "",
            ]
        if isinstance(cycle, CycleResult):
            lines += [
                "## 3. دورة الانضغاط البخاري (الفصل 8)",
                "",
                f"- المبرد: {cycle.fluid}",
                f"- التبخير / التكثيف: {cycle.inputs.evaporating_c:.1f} °C / "
                f"{cycle.inputs.condensing_c:.1f} °C",
                f"- سعة التبريد: {cycle.cooling_kw:.2f} kW ({cycle.cooling_tr:.2f} TR)",
                f"- COP: {cycle.cop:.3f}؛ COP كارنو: {cycle.carnot_cop:.3f}",
                f"- كفاءة القانون الثاني: {100 * cycle.second_law_efficiency:.1f}%",
                f"- قدرة الضاغط: {cycle.compressor_kw:.2f} kW",
                f"- التدفق الكتلي للمبرد: {cycle.mass_flow_kg_s:.4f} kg/s",
                "",
            ]
        if isinstance(simulation, SimulationResult):
            controller = i18n.option_label(simulation.inputs.controller)
            actuator = i18n.option_label(simulation.inputs.actuator)
            lines += [
                "## 4. التحكم الآلي والراحة (الفصلان 3 و11)",
                "",
                f"- المتحكم / المشغل: {controller} / {actuator}",
                f"- الراحة المحققة في النصف الأخير: {simulation.comfort_last_half_pct:.1f}%",
                f"- حالة الغرفة النهائية: {simulation.final_db_c:.2f} °C، "
                f"{simulation.final_rh_pct:.1f}% رطوبة نسبية، ET* {simulation.final_et_c:.2f} °C",
                f"- التبريد المسلّم: {simulation.delivered_cooling_kwh:.2f} kWh",
                f"- الكهرباء المقدّرة: {simulation.estimated_electricity_kwh:.2f} kWh",
                f"- مرات تبديل المشغل: {simulation.switching_count}",
                "",
            ]
        lines += [
            "## المنهج والحدود",
            "",
            "- تُحسب خصائص الهواء الرطب من علاقات ضغط التشبع Hyland–Wexler",
            "  عند الضغط الجوي المحدد.",
            "- تقدير الأحمال هو حساب تصميمي لذروة مستقرة يستخدم حرارة الهواء",
            "  الشمسية للأسطح المعتمة، ويستبعد التأخر الحراري ومكاسب القنوات وقدرة المراوح.",
            "- يستخدم ملف التبريد امتداد خط العملية المستقيم إلى منحنى التشبع",
            "  لتحديد ADP وBPF.",
            "- تُحسب حالات المبرد باستخدام CoolProp، ويُستخدم في أداء الضاغط",
            "  الكفاءة الأيزونتروبية المدخلة.",
            "- يستخدم فحص الراحة بديلًا تعليميًا لدرجة الحرارة الفعالة معدّلًا بالرطوبة",
            "  مع معيار مشروع للرطوبة النسبية 30–70%. وهو ليس تقييم امتثال كاملًا",
            "  لـ ASHRAE Standard 55 بطريقة PMV/PPD.",
            "",
        ]
        return "\n".join(lines)

    lines = [
        "# HVAC Design Studio — calculation record",
        "",
        f"Generated: {stamp}",
        "",
        "This record is an educational summary. Final equipment selection must be",
        "verified by a qualified engineer against the applicable code and project brief.",
        "",
    ]
    if isinstance(load, LoadResult):
        lines += [
            "## 1. Peak cooling load (Chapter 4 method)",
            "",
            f"- Project: {load.inputs.project_name}",
            f"- Space: {load.floor_area_m2:.1f} m², volume {load.volume_m3:.1f} m³",
            f"- Design outdoor condition: {load.inputs.outdoor_db_c:.1f} °C DB / "
            f"{load.inputs.outdoor_wb_c:.1f} °C WB",
            f"- Indoor condition: {load.inputs.indoor_db_c:.1f} °C / "
            f"{load.inputs.indoor_rh_pct:.1f}% RH",
            f"- Room sensible heat: {load.room_sensible_kw:.2f} kW",
            f"- Room latent heat: {load.room_latent_kw:.2f} kW",
            f"- Room sensible heat factor (RSHF): {100 * load.room_rshf:.1f}%",
            f"- Outdoor-air ventilation load: {load.ventilation_total_kw:.2f} kW",
            f"- Design coil load incl. outdoor air: {load.design_total_kw:.2f} kW "
            f"({load.design_tr:.2f} TR)",
            "",
        ]
    if isinstance(ahu, AhuDesignResult):
        lines += [
            "## 2. Psychrometric process and AHU (Chapters 2–3)",
            "",
            f"- Outdoor-air mass fraction: {100 * ahu.outdoor_air_fraction:.1f}%",
            f"- Mixed air: {ahu.mixed.dry_bulb_c:.2f} °C DB, "
            f"{ahu.mixed.relative_humidity_pct:.1f}% RH",
            f"- Supply air: {ahu.supply.dry_bulb_c:.2f} °C DB, "
            f"{ahu.supply.relative_humidity_pct:.1f}% RH",
            f"- Supply dry-air mass flow: {ahu.supply_mass_flow_kg_s:.3f} kg/s",
            f"- Apparatus dew point: {ahu.apparatus_dew_point_c:.2f} °C",
            f"- Bypass factor: {ahu.bypass_factor:.3f}",
            f"- Coil load: {ahu.coil_total_kw:.2f} kW total, "
            f"SHR {100 * ahu.coil_shr:.1f}%",
            "",
        ]
    if isinstance(cycle, CycleResult):
        lines += [
            "## 3. Vapour-compression cycle (Chapter 8)",
            "",
            f"- Refrigerant: {cycle.fluid}",
            f"- Evaporating / condensing: {cycle.inputs.evaporating_c:.1f} °C / "
            f"{cycle.inputs.condensing_c:.1f} °C",
            f"- Cooling capacity: {cycle.cooling_kw:.2f} kW ({cycle.cooling_tr:.2f} TR)",
            f"- COP: {cycle.cop:.3f}; Carnot COP: {cycle.carnot_cop:.3f}",
            f"- Second-law efficiency: {100 * cycle.second_law_efficiency:.1f}%",
            f"- Compressor power: {cycle.compressor_kw:.2f} kW",
            f"- Refrigerant mass flow: {cycle.mass_flow_kg_s:.4f} kg/s",
            "",
        ]
    if isinstance(simulation, SimulationResult):
        lines += [
            "## 4. Automatic control and comfort (Chapters 3 & 11)",
            "",
            f"- Controller / actuator: {simulation.inputs.controller} / "
            f"{simulation.inputs.actuator}",
            f"- Comfort maintained in final half: {simulation.comfort_last_half_pct:.1f}%",
            f"- Final room condition: {simulation.final_db_c:.2f} °C, "
            f"{simulation.final_rh_pct:.1f}% RH, ET* {simulation.final_et_c:.2f} °C",
            f"- Delivered cooling: {simulation.delivered_cooling_kwh:.2f} kWh",
            f"- Estimated electricity: {simulation.estimated_electricity_kwh:.2f} kWh",
            f"- Actuator switch changes: {simulation.switching_count}",
            "",
        ]
    lines += [
        "## Method and limits",
        "",
        "- Psychrometric properties use ASHRAE Hyland–Wexler saturation pressure",
        "  correlations at the stated atmospheric pressure.",
        "- The load estimate is a steady peak design calculation using sol-air",
        "  temperature for opaque surfaces. It excludes thermal lag, duct gain and fan power.",
        "- The cooling coil uses an extended straight process line to the saturation",
        "  curve to determine ADP and BPF.",
        "- Refrigerant states are computed with CoolProp; compressor performance uses",
        "  the entered isentropic efficiency.",
        "- The comfort check uses a humidity-adjusted effective-temperature teaching",
        "  proxy with a 30–70% RH project criterion. It is not a full ASHRAE",
        "  Standard 55 PMV/PPD compliance assessment.",
        "",
    ]
    return "\n".join(lines)
