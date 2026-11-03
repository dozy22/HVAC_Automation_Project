"""Engine-level tests for the quick design studio and the design-day simulation."""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pytest

from hvac.charts import day_cooling_chart
from hvac.day_sim import simulate_design_day
from hvac.quick_design import (
    AUTO_SYSTEM,
    CITIES,
    ENVELOPE_QUALITY,
    ORIENTATIONS,
    SPACE_TYPES,
    SYSTEM_LABELS,
    QuickInputs,
    auto_occupants,
    build_quick_design,
    quick_summary_payload,
    to_load_inputs,
)
from hvac.thermal_loads import calculate_thermal_load
from locales.ar import TRANSLATIONS


def _norm(text: str) -> str:
    return " ".join(text.split())


@pytest.fixture(scope="module")
def default_design():
    return build_quick_design(QuickInputs())


def test_default_case_sizes_a_covering_system(default_design):
    design = default_design
    load = design.load
    rec = design.recommendation

    assert 15.0 < load.design_total_kw < 23.0
    assert rec.capacity_kw >= rec.capacity_target_kw - 1e-9
    assert rec.capacity_target_kw == pytest.approx(load.design_total_kw * 1.12)
    assert rec.key == "vrf"
    assert rec.outdoor_units == 2
    assert rec.unit_size_kw == pytest.approx(12.5)
    assert rec.airflow_m3h >= 200.0
    assert rec.fresh_air_m3h == pytest.approx(load.ventilation_m3_s * 3600.0)
    assert design.occupants == 11
    assert design.occupants == auto_occupants(QuickInputs())


def test_quick_path_reuses_the_detailed_load_engine(default_design):
    recomputed = calculate_thermal_load(default_design.load_inputs)
    assert recomputed.design_total_kw == pytest.approx(
        default_design.load.design_total_kw
    )
    assert recomputed.room_sensible_kw == pytest.approx(
        default_design.load.room_sensible_kw
    )


def test_apartment_uses_a_small_split():
    design = build_quick_design(
        QuickInputs(
            space_type="Apartment living room",
            floor_area_m2=24.0,
            city="Erbil",
            orientation="North",
            envelope_quality="High performance",
        )
    )
    rec = design.recommendation
    assert rec.key == "split"
    assert rec.outdoor_units == 1
    assert rec.capacity_kw <= 5.3
    assert rec.capacity_kw >= design.load.design_total_kw


@pytest.mark.parametrize(
    ("space_type", "area", "expected"),
    [
        ("Mosque / assembly hall", 300.0, {"chiller", "ducted"}),
        ("Retail shop", 120.0, {"ducted"}),
        ("Office", 1500.0, {"chiller"}),
    ],
)
def test_open_plan_and_large_spaces_switch_family(space_type, area, expected):
    design = build_quick_design(
        QuickInputs(space_type=space_type, floor_area_m2=area)
    )
    assert design.recommendation.key in expected


def test_manual_choice_overrides_the_rule_and_banks_units():
    design = build_quick_design(
        QuickInputs(
            space_type="Office",
            floor_area_m2=300.0,
            system_preference=SYSTEM_LABELS["split"]["name"],
        )
    )
    rec = design.recommendation
    assert rec.key == "split"
    assert rec.outdoor_units >= 2
    assert rec.capacity_kw >= rec.capacity_target_kw


def test_auto_preference_is_the_default():
    design = build_quick_design(QuickInputs(system_preference=AUTO_SYSTEM))
    assert design.inputs.system_preference == AUTO_SYSTEM
    assert design.recommendation.key in SYSTEM_LABELS


def test_larger_floor_area_and_glazing_raise_the_load():
    base = build_quick_design(QuickInputs())
    bigger = build_quick_design(QuickInputs(floor_area_m2=220.0))
    glazed = build_quick_design(QuickInputs(glazing_ratio=0.55))
    assert bigger.load.design_total_kw > base.load.design_total_kw
    assert glazed.load.design_total_kw > base.load.design_total_kw


def test_better_envelope_lowers_the_load_and_the_u_values():
    standard = build_quick_design(QuickInputs(envelope_quality="Standard"))
    high = build_quick_design(QuickInputs(envelope_quality="High performance"))
    assert high.load.design_total_kw < standard.load.design_total_kw
    assert high.load_inputs.wall_u_w_m2k == pytest.approx(
        ENVELOPE_QUALITY["High performance"].wall_u
    )
    assert high.load_inputs.infiltration_ach < standard.load_inputs.infiltration_ach


def test_safety_margin_changes_the_selected_capacity():
    lean = build_quick_design(QuickInputs(safety_margin=0.05))
    generous = build_quick_design(QuickInputs(safety_margin=0.30))
    assert lean.recommendation.capacity_target_kw < generous.recommendation.capacity_target_kw
    assert lean.recommendation.capacity_kw <= generous.recommendation.capacity_kw


def test_manual_occupants_override_the_preset():
    design = build_quick_design(QuickInputs(occupants=45))
    assert design.occupants == 45
    assert design.load_inputs.occupants == 45
    auto = build_quick_design(QuickInputs(space_type="Classroom", floor_area_m2=60.0))
    assert auto.occupants == auto_occupants(
        QuickInputs(space_type="Classroom", floor_area_m2=60.0)
    )
    assert auto.occupants == 24


def test_custom_weather_and_city_presets():
    baghdad = build_quick_design(QuickInputs(city="Baghdad"))
    assert baghdad.load.outdoor_state.dry_bulb_c == pytest.approx(CITIES["Baghdad"].db_c)
    custom = build_quick_design(
        QuickInputs(city="Other / custom", outdoor_db_c=50.0, outdoor_wb_c=22.0)
    )
    assert custom.load.outdoor_state.dry_bulb_c == pytest.approx(50.0)
    # The custom day is hotter but much drier, so the sensible room gain rises
    # while the outdoor latent component falls.
    assert custom.load.room_sensible_kw > baghdad.load.room_sensible_kw
    humid = build_quick_design(
        QuickInputs(city="Other / custom", outdoor_db_c=50.0, outdoor_wb_c=29.0)
    )
    assert humid.load.design_total_kw > custom.load.design_total_kw


def test_orientation_changes_the_west_facade_peak():
    west = build_quick_design(QuickInputs(orientation="West"))
    north = build_quick_design(QuickInputs(orientation="North"))
    assert west.load_inputs.wall_solar_w_m2 == pytest.approx(
        ORIENTATIONS["West"].wall_solar_w_m2
    )
    assert west.load.design_total_kw > north.load.design_total_kw


@pytest.mark.parametrize(
    "inputs",
    [
        QuickInputs(floor_area_m2=5.0),
        QuickInputs(floor_area_m2=5000.0),
        QuickInputs(glazing_ratio=0.9),
        QuickInputs(space_type="Submarine"),
        QuickInputs(city="Atlantis"),
        QuickInputs(orientation="Up"),
        QuickInputs(envelope_quality="Cardboard"),
        QuickInputs(indoor_db_c=35.0),
        QuickInputs(safety_margin=0.8),
        QuickInputs(occupants=-2),
        QuickInputs(city="Other / custom"),
        QuickInputs(city="Other / custom", outdoor_db_c=44.0, outdoor_wb_c=44.0),
    ],
)
def test_invalid_inputs_are_rejected(inputs):
    with pytest.raises(ValueError):
        to_load_inputs(inputs)


def test_summary_payload_matches_the_design(default_design):
    payload = quick_summary_payload(default_design)
    assert payload["space_type"] == "Office"
    assert payload["system"] == default_design.recommendation.key
    assert payload["capacity_kw"] == pytest.approx(default_design.recommendation.capacity_kw)
    assert payload["design_total_kw"] == pytest.approx(default_design.load.design_total_kw)


def test_recommendation_sentences_are_translated_and_format_cleanly(default_design):
    points = default_design.recommendation.reasons + default_design.recommendation.cautions
    assert len(points) >= 4
    for point in points:
        key = _norm(point.template)
        assert key in TRANSLATIONS, point.template
        rendered = TRANSLATIONS[key].format(**point.values)
        assert "{" not in rendered and "}" not in rendered
        assert "None" not in rendered


def test_design_day_matches_the_sized_capacity(default_design):
    day = simulate_design_day(default_design)
    assert len(day.time_h) == 24 * 6 + 1
    assert day.time_h[0] == 0.0 and day.time_h[-1] == pytest.approx(24.0)
    assert len(day.room_db_c) == len(day.time_h)
    assert day.capacity_kw.min() == pytest.approx(day.capacity_kw.max())
    assert day.capacity_kw[0] == pytest.approx(default_design.recommendation.capacity_kw)
    assert 12.0 <= day.peak_hour <= 18.5
    assert 0.0 < day.peak_cooling_kw <= default_design.recommendation.capacity_kw * 1.02
    assert day.cooling_energy_kwh > 0.0
    assert day.electric_energy_kwh > 0.0
    assert 1.5 < day.day_cop < 6.0
    assert 0.0 <= day.occupied_comfort_pct <= 100.0
    assert max(day.room_db_c) <= 30.5
    assert min(day.room_db_c) >= 20.0
    assert day.system_on_hours > 8.0


def test_controller_modulates_smoothly_instead_of_chattering(default_design):
    """A high-gain P loop used to alternate full/off between ten-minute steps."""
    day = simulate_design_day(default_design)
    occupied_day = slice(8 * 6, 18 * 6)
    steps = np.abs(np.diff(day.cooling_total_kw[occupied_day]))
    assert steps.max() < 5.0
    assert np.count_nonzero(steps > 2.0) <= 2
    # The room must not oscillate around the setpoint either.
    error = np.abs(day.room_db_c[occupied_day] - day.setpoint_c[occupied_day])
    assert error.max() < 0.6


def test_at_hour_and_hourly_frame_shapes(default_design):
    day = simulate_design_day(default_design)
    sample = day.at_hour(15.0)
    assert sample["system_on"] is True
    assert 0.0 <= sample["part_load_pct"] <= 100.0
    assert sample["room_c"] == pytest.approx(day.room_db_c[15 * 6])
    frame = day.hourly_frame()
    assert len(frame) == 24
    assert list(frame.columns)[:3] == ["Hour", "Outdoor DB (degC)", "Room DB (degC)"]
    assert frame["Hour"].iloc[0] == "00:00"
    assert frame["Hour"].iloc[-1] == "23:00"
    assert frame["Cooling (kW)"].max() <= default_design.recommendation.capacity_kw + 1e-6


def test_an_undersized_plant_fails_to_hold_the_setpoint(default_design):
    weak = simulate_design_day(default_design, capacity_kw=default_design.load.design_total_kw * 0.6)
    assert weak.unmet_hours > 1.0
    assert weak.occupied_comfort_pct < 90.0
    full = simulate_design_day(default_design)
    assert full.occupied_comfort_pct > weak.occupied_comfort_pct


def test_simulation_rejects_a_non_positive_capacity(default_design):
    with pytest.raises(ValueError):
        simulate_design_day(default_design, capacity_kw=0.0)


def test_every_preset_can_be_sized_and_simulated():
    for space_type in SPACE_TYPES:
        design = build_quick_design(
            QuickInputs(space_type=space_type, floor_area_m2=120.0)
        )
        rec = design.recommendation
        assert rec.capacity_kw > 0.0
        assert math.isfinite(rec.airflow_m3h)
        day = simulate_design_day(design)
        assert len(day.time_h) == 145
        assert day.cooling_energy_kwh > 0.0


def test_cooling_chart_labels_the_morning_pull_down(default_design):
    """The pre-cool surge outranks the load peak, so the chart must name it."""
    day = simulate_design_day(default_design)
    figure = day_cooling_chart(day)
    annotations = list(figure.layout.annotations or ())
    labels = [annotation.text for annotation in annotations]
    assert "Pre-cool pull-down" in labels
    assert "Pre-cool pull-down" in TRANSLATIONS
    surge = annotations[labels.index("Pre-cool pull-down")]
    assert surge.x < 12.0
    assert surge.x == pytest.approx(day.time_h[int(np.argmax(day.cooling_total_kw))])


def test_a_flat_day_needs_no_pull_down_label(default_design):
    """Without a surge above the load peak the chart stays uncluttered."""
    day = simulate_design_day(default_design)
    flat = dataclasses.replace(day, peak_delivered_kw=day.peak_cooling_kw)
    labels = [a.text for a in day_cooling_chart(flat).layout.annotations or ()]
    assert "Pre-cool pull-down" not in labels
