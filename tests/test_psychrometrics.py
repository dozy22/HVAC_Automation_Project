"""Reference checks for the moist-air property engine."""

from __future__ import annotations

import math

import pytest

from hvac.psychrometrics import (
    P_ATM_STD_KPA,
    dew_point_from_rh,
    humidity_ratio_from_rh,
    humidity_ratio_from_wet_bulb,
    psychrometric_state,
    relative_humidity_from_ratio,
    saturation_humidity_ratio,
    saturation_pressure_kpa,
    specific_volume,
    wet_bulb_from_rh,
)


def test_saturation_pressure_reference_point():
    # ASHRAE Hyland–Wexler reference values (tabulated 3.169 kPa at 25 degC).
    assert saturation_pressure_kpa(25.0) == pytest.approx(3.1692, abs=2e-4)
    assert saturation_pressure_kpa(0.0) == pytest.approx(0.6112, abs=2e-4)


def test_standard_state_matches_reference_properties():
    state = psychrometric_state(25.0, P_ATM_STD_KPA, relative_humidity_pct=50.0)
    assert state.dry_bulb_c == pytest.approx(25.0)
    assert state.wet_bulb_c == pytest.approx(17.889, abs=2e-3)
    assert state.dew_point_c == pytest.approx(13.864, abs=2e-3)
    assert state.humidity_ratio_g_kg == pytest.approx(9.881, abs=2e-3)
    assert state.enthalpy_kj_kg == pytest.approx(50.322, abs=3e-3)
    assert state.specific_volume_m3_kg == pytest.approx(0.8580, abs=2e-4)
    assert state.vapor_pressure_kpa == pytest.approx(1.5846, abs=2e-4)
    assert 0.0 < state.relative_humidity_pct <= 100.0


def test_wet_bulb_defines_the_same_state_as_relative_humidity():
    for dry_bulb, rh in ((10.0, 30.0), (25.0, 50.0), (40.0, 20.0), (45.0, 10.0)):
        wet_bulb = wet_bulb_from_rh(dry_bulb, rh)
        state = psychrometric_state(dry_bulb, wet_bulb_c=wet_bulb)
        assert state.wet_bulb_c == pytest.approx(wet_bulb, abs=1e-6)
        assert state.relative_humidity_pct == pytest.approx(rh, abs=0.01)
        assert state.humidity_ratio == pytest.approx(
            humidity_ratio_from_wet_bulb(dry_bulb, wet_bulb), rel=1e-9
        )


def test_humidity_ratio_round_trip():
    w = humidity_ratio_from_rh(30.0, 65.0, P_ATM_STD_KPA)
    rh = relative_humidity_from_ratio(30.0, w, P_ATM_STD_KPA)
    assert rh == pytest.approx(65.0, abs=1e-9)


def test_properties_are_physically_ordered():
    state = psychrometric_state(24.0, relative_humidity_pct=50.0)
    assert state.dew_point_c < state.wet_bulb_c < state.dry_bulb_c
    assert 0.0 < state.humidity_ratio < saturation_humidity_ratio(24.0)
    assert state.density_kg_m3 < 1.25
    assert state.moisture_content_g_m3 > 0.0


def test_dew_point_matches_vapour_pressure():
    state = psychrometric_state(30.0, relative_humidity_pct=40.0)
    assert saturation_pressure_kpa(state.dew_point_c) == pytest.approx(
        state.vapor_pressure_kpa, rel=2e-4
    )
    assert state.wet_bulb_c == pytest.approx(wet_bulb_from_rh(30.0, 40.0), abs=1e-6)
    assert state.dew_point_c == pytest.approx(
        dew_point_from_rh(30.0, 40.0), abs=1e-6
    )


def test_specific_volume_dry_air_reference():
    # Dry air near 20 degC at standard pressure is close to 0.83 m3/kg.
    assert specific_volume(20.0, 0.0) == pytest.approx(0.830, abs=0.002)


def test_very_dry_air_has_low_wet_bulb():
    state = psychrometric_state(45.0, relative_humidity_pct=5.0)
    assert state.relative_humidity_pct == pytest.approx(5.0, abs=1e-6)
    assert state.wet_bulb_c < 20.0
    assert state.humidity_ratio_g_kg < 4.0
    assert not math.isnan(state.enthalpy_kj_kg)


def test_negative_or_excessive_humidity_is_rejected():
    with pytest.raises(ValueError):
        psychrometric_state(25.0, humidity_ratio=-0.001)
    with pytest.raises(ValueError):
        psychrometric_state(25.0, humidity_ratio=0.03)
    with pytest.raises(ValueError):
        psychrometric_state(25.0, relative_humidity_pct=120.0)


def test_pressure_changes_humidity_ratio_at_fixed_rh():
    sea_level = psychrometric_state(25.0, 101.325, relative_humidity_pct=50.0)
    high_altitude = psychrometric_state(25.0, 85.0, relative_humidity_pct=50.0)
    assert high_altitude.humidity_ratio > sea_level.humidity_ratio
    assert high_altitude.specific_volume_m3_kg > sea_level.specific_volume_m3_kg
