"""End-to-end checks for loads, AHU, refrigeration and control modules."""

from __future__ import annotations

import pytest

from hvac.ahu import (
    design_ahu,
    heating_and_steam_humidification,
    mix_air,
    supply_state_from_space_loads,
)
from hvac.controls import (
    CONTROLLER_PID,
    CONTROLLER_THRESHOLD,
    ComfortLimits,
    SimulationInputs,
    controller_comparison,
    effective_temperature_c,
    simulate_control,
)
from hvac.psychrometrics import (
    H_FG_0,
    moist_air_specific_heat,
    psychrometric_state,
)
from hvac.refrigeration import (
    REFRIGERANTS,
    CycleInputs,
    compute_cycle,
    sensitivity_sweep,
)
from hvac.thermal_loads import (
    TR_KW,
    calculate_thermal_load,
    default_load_inputs,
)


@pytest.fixture()
def load_case():
    return calculate_thermal_load(default_load_inputs())


@pytest.fixture()
def ahu_case(load_case):
    cp = moist_air_specific_heat(load_case.indoor_state.humidity_ratio)
    supply_c = 13.0
    mass = load_case.room_sensible_kw / (
        cp * (load_case.indoor_state.dry_bulb_c - supply_c)
    )
    fraction = load_case.ventilation_mass_kg_s / mass
    return design_ahu(
        load_case.indoor_state,
        load_case.outdoor_state,
        load_case.room_sensible_kw,
        load_case.room_latent_kw,
        supply_c,
        fraction,
    )


def test_default_load_balances(load_case):
    assert load_case.room_sensible_kw == pytest.approx(12.8315, rel=1e-4)
    assert load_case.room_latent_kw == pytest.approx(1.1909, rel=1e-3)
    assert load_case.room_total_kw == pytest.approx(14.0224, rel=1e-4)
    assert load_case.room_rshf == pytest.approx(0.91507, abs=1e-5)
    assert load_case.ventilation_total_kw == pytest.approx(5.1327, rel=1e-4)
    assert load_case.design_total_kw == pytest.approx(19.1551, rel=1e-4)
    assert load_case.design_tr == pytest.approx(load_case.design_total_kw / TR_KW)
    assert load_case.design_tr == pytest.approx(5.4467, rel=1e-4)
    assert load_case.floor_area_m2 == pytest.approx(96.0)
    assert load_case.volume_m3 == pytest.approx(307.2)


def test_load_components_reconcile(load_case):
    frame = load_case.component_frame(include_ventilation=True)
    assert frame["Sensible (kW)"].sum() == pytest.approx(
        load_case.design_sensible_kw, rel=1e-9
    )
    assert frame["Latent (kW)"].sum() == pytest.approx(
        load_case.design_latent_kw, rel=1e-9
    )
    assert frame["Total (kW)"].sum() == pytest.approx(
        load_case.design_total_kw, rel=1e-9
    )
    room = frame[frame["Scope"] == "Room"]
    assert room["Total (kW)"].sum() == pytest.approx(load_case.room_total_kw)
    assert load_case.summary_frame().shape[0] == 10


def test_window_area_must_fit_exposed_wall():
    inputs = default_load_inputs()
    bad = inputs.__class__(**{**inputs.__dict__, "window_area_m2": 500.0})
    with pytest.raises(ValueError, match="Window area exceeds"):
        calculate_thermal_load(bad)


def test_ahu_mixing_conserves_water_and_enthalpy(load_case):
    fraction = 0.25
    mixed = mix_air(
        load_case.indoor_state,
        load_case.outdoor_state,
        fraction,
        load_case.indoor_state.pressure_kpa,
    )
    expected_w = (
        fraction * load_case.outdoor_state.humidity_ratio
        + (1 - fraction) * load_case.indoor_state.humidity_ratio
    )
    expected_h = (
        fraction * load_case.outdoor_state.enthalpy_kj_kg
        + (1 - fraction) * load_case.indoor_state.enthalpy_kj_kg
    )
    assert mixed.humidity_ratio == pytest.approx(expected_w, abs=1e-12)
    assert mixed.enthalpy_kj_kg == pytest.approx(expected_h, abs=1e-9)


def test_default_ahu_process_is_consistent(ahu_case, load_case):
    assert ahu_case.outdoor_air_fraction == pytest.approx(0.19156, abs=1e-4)
    assert ahu_case.supply.dry_bulb_c == pytest.approx(13.0)
    assert ahu_case.coil_total_kw == pytest.approx(19.1666, rel=1e-4)
    assert ahu_case.coil_total_kw == pytest.approx(
        ahu_case.coil_sensible_kw + ahu_case.coil_latent_kw
    )
    assert ahu_case.coil_shr == pytest.approx(
        ahu_case.coil_sensible_kw / ahu_case.coil_total_kw
    )
    assert 0.0 < ahu_case.bypass_factor <= 1.0
    assert ahu_case.apparatus_dew_point_c < ahu_case.supply.dry_bulb_c
    assert ahu_case.apparatus_dew_point.relative_humidity_pct == pytest.approx(
        100.0, abs=1e-3
    )
    assert ahu_case.mixed.dry_bulb_c > ahu_case.supply.dry_bulb_c

    cp = moist_air_specific_heat(load_case.indoor_state.humidity_ratio)
    sensible = (
        ahu_case.supply_mass_flow_kg_s
        * cp
        * (load_case.indoor_state.dry_bulb_c - ahu_case.supply.dry_bulb_c)
    )
    latent = (
        ahu_case.supply_mass_flow_kg_s
        * H_FG_0
        * (
            load_case.indoor_state.humidity_ratio
            - ahu_case.supply.humidity_ratio
        )
    )
    assert sensible == pytest.approx(load_case.room_sensible_kw, rel=1e-9)
    assert latent == pytest.approx(load_case.room_latent_kw, rel=1e-9)


def test_supply_state_rejects_supersaturation(load_case):
    with pytest.raises(ValueError, match="supersaturated"):
        supply_state_from_space_loads(
            load_case.indoor_state,
            load_case.room_sensible_kw,
            load_case.room_latent_kw,
            supply_db_c=10.0,
        )


def test_heating_and_humidification(load_case):
    entering = psychrometric_state(12.0, relative_humidity_pct=60.0)
    result = heating_and_steam_humidification(
        entering, target_db_c=22.0, target_rh_pct=55.0, mass_flow_kg_s=0.5
    )
    assert result.heated.humidity_ratio == pytest.approx(entering.humidity_ratio)
    assert result.heated.dry_bulb_c == pytest.approx(22.0)
    assert result.leaving.relative_humidity_pct == pytest.approx(55.0, abs=1e-9)
    assert result.heating_kw == pytest.approx(5.0784, rel=1e-4)
    assert result.humidification_kg_h == pytest.approx(6.9297, rel=1e-4)
    assert result.leaving.enthalpy_kj_kg > result.heated.enthalpy_kj_kg


def test_refrigeration_cycle_reference():
    cycle = compute_cycle(CycleInputs())
    assert cycle.cooling_kw == pytest.approx(12.0)
    assert cycle.cooling_tr == pytest.approx(12.0 / TR_KW)
    assert cycle.cop == pytest.approx(3.9762, rel=1e-4)
    assert cycle.carnot_cop == pytest.approx(6.3988, rel=1e-4)
    assert cycle.second_law_efficiency == pytest.approx(0.6214, rel=1e-3)
    assert cycle.compressor_kw == pytest.approx(3.0179, rel=1e-3)
    assert cycle.condenser_kw == pytest.approx(
        cycle.cooling_kw + cycle.compressor_kw, rel=1e-9
    )
    assert cycle.mass_flow_kg_s == pytest.approx(0.081139, rel=1e-3)
    assert cycle.pressure_ratio == pytest.approx(3.6868, rel=1e-3)
    assert cycle.discharge.temperature_c > 45.0
    assert cycle.discharge.temperature_c > cycle.discharge_isentropic_c


def test_cycle_state_energy_balances():
    cycle = compute_cycle(CycleInputs())
    states = [
        cycle.suction,
        cycle.discharge,
        cycle.condenser_exit,
        cycle.evaporator_inlet,
    ]
    assert cycle.evaporator_inlet.enthalpy_kj_kg == pytest.approx(
        cycle.condenser_exit.enthalpy_kj_kg, abs=1e-9
    )
    assert cycle.suction.pressure_bar == pytest.approx(
        cycle.evaporator_inlet.pressure_bar
    )
    assert cycle.discharge.pressure_bar == pytest.approx(
        cycle.condenser_exit.pressure_bar
    )
    table = cycle.states_table()
    assert list(table["State"]) == [f"{s.number} - {s.label}" for s in states]


@pytest.mark.parametrize("refrigerant", list(REFRIGERANTS))
def test_every_supported_refrigerant(refrigerant):
    cycle = compute_cycle(CycleInputs(refrigerant=refrigerant))
    assert cycle.cop > 1.0
    assert cycle.mass_flow_kg_s > 0.0
    assert cycle.compressor_kw > 0.0
    assert cycle.cooling_tr > 0.0


def test_zero_superheat_and_subcooling_are_supported():
    cycle = compute_cycle(CycleInputs(superheat_k=0.0, subcooling_k=0.0))
    assert cycle.suction.quality == pytest.approx(1.0)
    assert cycle.suction.temperature_c == pytest.approx(2.0, abs=1e-6)
    assert cycle.condenser_exit.temperature_c == pytest.approx(45.0, abs=1e-6)
    assert cycle.cop > 1.0


def test_subcooling_improves_cop_but_does_not_change_pressure_ratio():
    frame = sensitivity_sweep(CycleInputs(), "subcooling_k", [0, 5, 10, 15, 20])
    assert frame["COP"].is_monotonic_increasing
    assert frame["Discharge temperature C"].iloc[0] == pytest.approx(
        frame["Discharge temperature C"].iloc[-1], abs=1e-6
    )


def test_superheat_raises_discharge_temperature():
    frame = sensitivity_sweep(CycleInputs(), "superheat_k", [0, 5, 10, 15, 20])
    assert frame["Discharge temperature C"].iloc[-1] > frame["Discharge temperature C"].iloc[0]
    assert frame["Mass flow kg/s"].iloc[-1] < frame["Mass flow kg/s"].iloc[0]


def test_invalid_cycle_conditions_are_rejected():
    with pytest.raises(ValueError):
        compute_cycle(CycleInputs(evaporating_c=10.0, condensing_c=12.0))
    with pytest.raises(ValueError):
        compute_cycle(CycleInputs(refrigerant="R999"))


def test_effective_temperature_proxy():
    et, wb = effective_temperature_c(24.5, 50.0)
    assert et == pytest.approx(24.5)
    assert wb < 24.5
    et_warm, _ = effective_temperature_c(24.5, 70.0)
    assert et_warm > et
    assert ComfortLimits().contains(24.0, 45.0) == (True, True, True)
    assert ComfortLimits().contains(24.0, 25.0) == (False, True, False)


def test_default_pid_control_meets_comfort():
    result = simulate_control(SimulationInputs())
    assert result.comfort_last_half_pct == pytest.approx(100.0)
    assert result.comfort_pct > 90.0
    assert result.humidity_pct == pytest.approx(100.0)
    assert abs(result.final_db_c - 24.5) <= 0.1
    assert 30.0 <= result.final_rh_pct <= 70.0
    assert result.switching_count == 0
    assert result.delivered_cooling_kwh > 0.0
    assert result.estimated_electricity_kwh == pytest.approx(
        result.delivered_cooling_kwh / 3.2
    )


def test_threshold_control_cycles_but_holds_comfort():
    base = SimulationInputs()
    threshold = SimulationInputs(
        **{**base.__dict__, "controller": CONTROLLER_THRESHOLD}
    )
    result = simulate_control(threshold)
    assert result.switching_count > 10
    assert result.comfort_last_half_pct >= 95.0
    comparison = controller_comparison(base)
    assert list(comparison["Controller"]) == [CONTROLLER_PID, CONTROLLER_THRESHOLD]
    assert comparison.loc[0, "Switch changes"] == 0
    assert comparison.loc[1, "Switch changes"] > 0


def test_supply_temperature_actuator_runs():
    from hvac.controls import ACTUATOR_SUPPLY

    base = SimulationInputs()
    inputs = SimulationInputs(
        **{**base.__dict__, "actuator": ACTUATOR_SUPPLY}
    )
    result = simulate_control(inputs)
    assert result.final_db_c < inputs.initial_db_c
    assert result.comfort_last_half_pct >= 90.0
    assert result.actuator_label.startswith("Supply-air")


def test_invalid_comfort_limits_are_rejected():
    with pytest.raises(ValueError):
        SimulationInputs(
            comfort=ComfortLimits(et_min_c=27.0, et_max_c=24.0)
        ).validate()
