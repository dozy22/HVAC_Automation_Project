"""Application entry point for the HVAC & Psychrometric Automation System.

Run with:
    streamlit run main.py
or double-click run_app.bat on Windows.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import i18n
import ui
from views import ahu, comfort, design, loads, overview, refrigeration

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="HVAC Design Studio",
    page_icon=str(ROOT / "assets" / "favicon.svg"),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": (
            "**HVAC Design Studio** — an educational HVAC and psychrometric "
            "automation system built with Streamlit, Plotly and CoolProp.\n\n"
            "**صمم بواسطة (HALF ENGINEERS)**"
        )
    },
)

ui.init_state()
ui.load_css()

page = ui.sidebar()

renderers = {
    ui.PAGE_OVERVIEW: overview.render,
    ui.PAGE_DESIGN: design.render,
    ui.PAGE_LOADS: loads.render,
    ui.PAGE_AHU: ahu.render,
    ui.PAGE_REFRIGERATION: refrigeration.render,
    ui.PAGE_COMFORT: comfort.render,
}

try:
    renderers[page]()
except Exception as exc:  # pragma: no cover - last-resort UI guard
    st.error(
        i18n.translate_text(
            "This module could not finish the current calculation. The input state is "
            "preserved; reset the workspace if the error repeats."
        )
    )
    st.caption(f"{exc.__class__.__name__}: {exc}")
    with st.expander(i18n.translate_text("Technical details")):
        st.exception(exc)
