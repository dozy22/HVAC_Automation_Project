"""Browser-level smoke tests through Streamlit's AppTest harness."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ui

APP = Path(__file__).resolve().parents[1] / "main.py"


@pytest.fixture()
def app() -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=120.0)
    # The live studio opens in Arabic; the behavioural suite exercises the
    # canonical English interface, while dedicated tests cover Arabic/RTL.
    at.session_state["language"] = "en"
    at.run()
    assert not at.exception, at.exception
    return at


def _page_radio(at: AppTest):
    return next(widget for widget in at.radio if widget.key == "page")


def _goto(at: AppTest, page: str) -> AppTest:
    _page_radio(at).set_value(page).run()
    assert not at.exception, at.exception
    assert at.session_state["page"] == page
    return at


def _markdown_text(at: AppTest) -> str:
    return "\n".join(str(block.value) for block in at.markdown)


def test_overview_loads_with_the_default_case(app: AppTest):
    text = _markdown_text(app)
    assert "Advanced HVAC &amp; Psychrometric Automation" in text
    assert "Quick studio + 4 modules" in text
    assert "The presentation route" in text
    assert app.session_state["load_result"] is not None
    assert app.session_state["ahu_result"] is not None
    assert app.session_state["cycle_result"] is not None
    assert not app.error


def test_module_card_navigates_to_cooling_load(app: AppTest):
    buttons = {button.key: button for button in app.button if button.key}
    buttons["loads_open"].click().run()
    assert not app.exception, app.exception
    assert app.session_state["page"] == ui.PAGE_LOADS
    assert "Peak cooling load" in _markdown_text(app) or "Cooling load" in _markdown_text(app)


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        (ui.PAGE_LOADS, "Where the heat comes from"),
        (ui.PAGE_AHU, "The process, drawn to scale"),
        (ui.PAGE_REFRIGERATION, "Pressure–enthalpy cycle"),
        (ui.PAGE_COMFORT, "A day under closed-loop control"),
    ],
)
def test_every_module_renders(app: AppTest, page: str, expected: str):
    _goto(app, page)
    assert expected in _markdown_text(app)
    assert not app.exception, app.exception
    assert not app.error


def test_module1_material_callback_and_live_load(app: AppTest):
    _goto(app, ui.PAGE_LOADS)
    baseline = app.session_state["load_result"]

    select = next(widget for widget in app.selectbox if widget.key == "m1_wall_material")
    select.select("Brick wall, 200 mm, uninsulated").run()
    assert not app.exception, app.exception
    assert app.session_state["m1_wall_u"] == pytest.approx(1.70)
    assert app.session_state["m1_wall_abs"] == pytest.approx(0.65)
    updated = app.session_state["load_result"]
    assert updated.room_sensible_kw > baseline.room_sensible_kw
    assert updated.inputs.wall_u_w_m2k == pytest.approx(1.70)

    outdoor_db = next(widget for widget in app.number_input if widget.key == "m1_outdoor_db")
    outdoor_db.set_value(50.0).run()
    assert not app.exception, app.exception
    hotter = app.session_state["load_result"]
    assert hotter.design_total_kw > updated.design_total_kw


def test_module2_supply_air_and_outdoor_fraction(app: AppTest):
    _goto(app, ui.PAGE_AHU)

    supply = next(widget for widget in app.slider if widget.key == "m2_supply")
    supply.set_value(15.0).run()
    assert not app.exception, app.exception
    ahu = app.session_state["ahu_result"]
    assert ahu.supply.dry_bulb_c == pytest.approx(15.0)
    assert ahu.bypass_factor > 0.0

    auto_oa = next(widget for widget in app.toggle if widget.key == "m2_auto_oa")
    auto_oa.set_value(False).run()
    assert not app.exception, app.exception
    manual = next(widget for widget in app.slider if widget.key == "m2_oa_manual")
    manual.set_value(25.0).run()
    assert not app.exception, app.exception
    assert app.session_state["ahu_result"].outdoor_air_fraction == pytest.approx(0.25)


def test_module2_rejected_coil_clears_downstream_result(app: AppTest):
    _goto(app, ui.PAGE_AHU)
    supply = next(widget for widget in app.slider if widget.key == "m2_supply")
    supply.set_value(11.0).run()
    assert not app.exception, app.exception
    assert app.error
    assert app.session_state["ahu_result"] is None

    supply = next(widget for widget in app.slider if widget.key == "m2_supply")
    supply.set_value(15.0).run()
    assert not app.exception, app.exception
    assert not app.error
    assert app.session_state["ahu_result"] is not None


def test_module2_property_explorer_accepts_wet_bulb(app: AppTest):
    _goto(app, ui.PAGE_AHU)
    basis = next(widget for widget in app.radio if widget.key == "m2_prop_basis")
    basis.set_value("Wet bulb").run()
    assert not app.exception, app.exception
    wet_bulb = next(widget for widget in app.number_input if widget.key == "m2_prop_wb")
    wet_bulb.set_value(20.0).run()
    assert not app.exception, app.exception
    assert not app.error


def test_module3_refrigerant_load_and_sweep(app: AppTest):
    _goto(app, ui.PAGE_REFRIGERATION)
    connected = app.session_state["cycle_result"]
    assert connected.cooling_kw > 15.0

    refrigerant = next(widget for widget in app.selectbox if widget.key == "m3_refrigerant")
    refrigerant.select("R32").run()
    assert not app.exception, app.exception
    assert app.session_state["cycle_result"].fluid == "R32"

    use_connected = next(
        widget for widget in app.toggle if widget.key == "m3_use_connected"
    )
    use_connected.set_value(False).run()
    assert not app.exception, app.exception
    manual_load = next(
        widget for widget in app.number_input if widget.key == "m3_manual_load"
    )
    manual_load.set_value(20.0).run()
    assert not app.exception, app.exception
    assert app.session_state["cycle_result"].cooling_kw == pytest.approx(20.0)

    sweep = next(widget for widget in app.radio if widget.key == "m3_sweep_mode")
    sweep.set_value("Superheat").run()
    assert not app.exception, app.exception
    compare = next(widget for widget in app.toggle if widget.key == "m3_compare")
    compare.set_value(True).run()
    assert not app.exception, app.exception
    tables = _markdown_text(app).count('<table class="data-table">')
    assert tables >= 4


def test_module4_threshold_supply_actuator_and_weather(app: AppTest):
    _goto(app, ui.PAGE_COMFORT)
    simulation = app.session_state["simulation_result"]
    assert simulation is not None
    assert simulation.inputs.controller == "PID"
    assert simulation.comfort_last_half_pct >= 95.0

    controller = next(widget for widget in app.radio if widget.key == "m4_controller")
    controller.set_value("Threshold (on/off)").run()
    assert not app.exception, app.exception
    threshold = app.session_state["simulation_result"]
    assert threshold.inputs.controller == "Threshold (on/off)"
    assert threshold.switching_count > 10

    weather = next(widget for widget in app.selectbox if widget.key == "m4_weather")
    weather.select("Mild day").run()
    assert not app.exception, app.exception
    assert app.session_state["m4_out_mean"] == pytest.approx(29.0)
    mild = app.session_state["simulation_result"]
    assert mild.inputs.outdoor_mean_c == pytest.approx(29.0)

    actuator = next(widget for widget in app.selectbox if widget.key == "m4_actuator")
    actuator.select("Supply-air temperature").run()
    assert not app.exception, app.exception
    supply_mode = app.session_state["simulation_result"]
    assert supply_mode.inputs.actuator == "Supply-air temperature"
    assert supply_mode.actuator_label.startswith("Supply-air")


def test_reset_workspace_returns_to_overview(app: AppTest):
    _goto(app, ui.PAGE_REFRIGERATION)
    refrigerant = next(widget for widget in app.selectbox if widget.key == "m3_refrigerant")
    refrigerant.select("R290 (propane)").run()
    assert app.session_state["cycle_result"].fluid == "R290"

    _goto(app, ui.PAGE_DESIGN)
    area = next(widget for widget in app.number_input if widget.key == "qd_area")
    area.set_value(180.0).run()
    assert app.session_state["quick_design"] is not None

    reset = next(button for button in app.button if button.label == "Reset workspace")
    reset.click().run()
    assert not app.exception, app.exception
    assert app.session_state["page"] == ui.PAGE_OVERVIEW
    assert "m3_refrigerant" not in app.session_state
    assert "qd_area" not in app.session_state
    assert app.session_state["quick_design"] is None
    assert app.session_state["day_result"] is None
    assert app.session_state["load_result"] is not None
    assert "The presentation route" in _markdown_text(app)


def test_quick_design_page_sizes_and_simulates(app: AppTest):
    _goto(app, ui.PAGE_DESIGN)
    text = _markdown_text(app)
    assert "Six answers." in text
    assert "What the space needs" in text
    assert "The hottest day, hour by hour" in text
    assert "recommend-card" in text
    assert "day-scene" in text

    design = app.session_state["quick_design"]
    day = app.session_state["day_result"]
    assert design is not None and day is not None
    assert design.load.design_total_kw > 10.0
    assert design.recommendation.capacity_kw >= design.load.design_total_kw
    assert len(day.time_h) == 24 * 6 + 1
    assert 12.0 <= day.peak_hour <= 18.0
    assert day.electric_energy_kwh > 0.0
    assert not app.exception, app.exception


def test_quick_design_inputs_update_load_and_system(app: AppTest):
    _goto(app, ui.PAGE_DESIGN)
    baseline = app.session_state["quick_design"]

    area = next(widget for widget in app.number_input if widget.key == "qd_area")
    area.set_value(320.0).run()
    assert not app.exception, app.exception
    larger = app.session_state["quick_design"]
    assert larger.load.design_total_kw > baseline.load.design_total_kw

    envelope = next(widget for widget in app.selectbox if widget.key == "qd_envelope")
    envelope.select("High performance").run()
    assert not app.exception, app.exception
    efficient = app.session_state["quick_design"]
    assert efficient.load.design_total_kw < larger.load.design_total_kw
    assert efficient.load.inputs.wall_u_w_m2k == pytest.approx(0.30)

    # A large open-plan space should not stay on a small split.
    space = next(widget for widget in app.selectbox if widget.key == "qd_space")
    space.select("Mosque / assembly hall").run()
    assert not app.exception, app.exception
    mosque = app.session_state["quick_design"]
    assert mosque.recommendation.key in {"ducted", "chiller"}


def test_quick_design_hour_scrubber_and_manual_occupancy(app: AppTest):
    _goto(app, ui.PAGE_DESIGN)
    manual = next(widget for widget in app.toggle if widget.key == "qd_manual_occ")
    manual.set_value(True).run()
    assert not app.exception, app.exception
    occupants = next(widget for widget in app.number_input if widget.key == "qd_occupants")
    occupants.set_value(45).run()
    assert not app.exception, app.exception
    assert app.session_state["quick_design"].occupants == 45

    hour = next(widget for widget in app.select_slider if widget.key == "qd_hour")
    hour.set_value(3).run()
    assert not app.exception, app.exception
    assert "03:00" in _markdown_text(app)


def test_quick_design_page_is_arabic():
    at = _fresh_app()
    _page_radio(at).set_value(ui.PAGE_DESIGN).run()
    assert not at.exception, at.exception
    text = _markdown_text(at)
    assert "ست إجابات." in text
    assert "ما تحتاجه المساحة" in text
    assert "أحر يوم، ساعةً بساعة" in text
    assert "Recommended system" not in text
    assert at.session_state["quick_design"] is not None


def _fresh_app() -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=120.0)
    at.run()
    assert not at.exception, at.exception
    return at


def test_live_app_opens_in_arabic_with_rtl_and_credit():
    at = _fresh_app()
    assert at.session_state["language"] == "ar"
    assert at.session_state["dark_mode"] is False
    text = _markdown_text(at)
    assert "right-to-left Arabic layer" in text
    assert "مسار العرض" in text
    assert "صمم بواسطة (HALF ENGINEERS)" in text
    assert "Designed by (HALF ENGINEERS)" not in text


def test_language_switch_returns_to_english_and_back():
    at = _fresh_app()
    language = next(widget for widget in at.selectbox if widget.key == "language")
    language.select("en").run()
    assert not at.exception, at.exception
    assert at.session_state["language"] == "en"
    english = _markdown_text(at)
    assert "right-to-left Arabic layer" not in english
    assert "The presentation route" in english
    assert "Designed by (HALF ENGINEERS)" in english

    language = next(widget for widget in at.selectbox if widget.key == "language")
    language.select("ar").run()
    assert not at.exception, at.exception
    assert at.session_state["language"] == "ar"
    assert "صمم بواسطة (HALF ENGINEERS)" in _markdown_text(at)


def test_dark_mode_layers_theme_and_survives_navigation(app: AppTest):
    toggle = next(widget for widget in app.toggle if widget.key == "dark_mode")
    toggle.set_value(True).run()
    assert not app.exception, app.exception
    assert app.session_state["dark_mode"] is True
    text = _markdown_text(app)
    assert "dark drawing-board theme" in text
    assert "#0b1614" in text

    _goto(app, ui.PAGE_AHU)
    assert app.session_state["dark_mode"] is True
    assert "dark drawing-board theme" in _markdown_text(app)

    toggle = next(widget for widget in app.toggle if widget.key == "dark_mode")
    toggle.set_value(False).run()
    assert not app.exception, app.exception
    assert "dark drawing-board theme" not in _markdown_text(app)


def test_arabic_module_notes_and_tables_are_localised():
    at = _fresh_app()
    _page_radio(at).set_value(ui.PAGE_LOADS).run()
    assert not at.exception, at.exception
    text = _markdown_text(at)

    assert "**الغلاف المعتم.**" in text
    assert "Opaque envelope" not in text
    assert "التوصيل عبر الجدار" in text
    assert "Wall conduction" not in text
    assert "عامل الحرارة المحسوسة للغرفة (RSHF)" in text
    assert "Hand-off" not in text


def test_reset_keeps_language_and_theme_choice():
    at = _fresh_app()
    language = next(widget for widget in at.selectbox if widget.key == "language")
    language.select("en").run()
    toggle = next(widget for widget in at.toggle if widget.key == "dark_mode")
    toggle.set_value(True).run()

    reset = next(button for button in at.button if button.label == "Reset workspace")
    reset.click().run()
    assert not at.exception, at.exception
    assert at.session_state["page"] == ui.PAGE_OVERVIEW
    assert at.session_state["language"] == "en"
    assert at.session_state["dark_mode"] is True

