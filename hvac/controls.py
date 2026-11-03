"""Reduced-order room model, ASHRAE-style comfort check, and HVAC controllers.

The comfort test uses an ASHRAE-style effective-temperature proxy together
with relative humidity:
    ET* proxy = Tdb + 0.04 (RH - 50)
so that the 50% RH reference case is close to operative temperature.  Full
Standard 55 compliance still requires PMV/PPD, clothing, metabolic rate and
air-speed inputs; this is a transparent teaching approximation.  The project
brief's 30-70% relative-humidity band is used as an additional acceptance gate.

The plant is a deliberately compact, physically bounded zone model:
    C dT/dt = Q_internal + UA(T_out - T_room) + Q_vent - Q_cool
The cooling coil is represented with sensible capacity and a simplified
wet-coil moisture-removal effectiveness.  It is suitable for controls teaching
and demonstration, not for equipment selection.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
import pandas as pd

from .psychrometrics import (
    H_FG_0,
    P_ATM_STD_KPA,
    humidity_ratio_from_rh,
    moist_air_specific_heat,
    relative_humidity_from_ratio,
    saturation_humidity_ratio,
    wet_bulb_from_rh,
)

CONTROLLER_PID = "PID"
CONTROLLER_THRESHOLD = "Threshold (on/off)"
CONTROLLERS = (CONTROLLER_PID, CONTROLLER_THRESHOLD)

ACTUATOR_VALVE = "Chilled-water valve"
ACTUATOR_SUPPLY = "Supply-air temperature"
ACTUATORS = (ACTUATOR_VALVE, ACTUATOR_SUPPLY)

WEATHER_SCENARIOS: dict[str, dict[str, float]] = {
    "Hot afternoon": {"mean_c": 36.0, "amplitude_c": 4.5, "rh_pct": 25.0},
    "Peak summer": {"mean_c": 39.0, "amplitude_c": 4.0, "rh_pct": 22.0},
    "Hot humid": {"mean_c": 34.0, "amplitude_c": 3.0, "rh_pct": 55.0},
    "Mild day": {"mean_c": 29.0, "amplitude_c": 4.0, "rh_pct": 40.0},
}


@dataclass(frozen=True)
class ComfortLimits:
    et_min_c: float = 23.0
    et_max_c: float = 26.0
    rh_min_pct: float = 30.0
    rh_max_pct: float = 70.0

    def validate(self) -> None:
        if self.et_min_c >= self.et_max_c:
            raise ValueError("Effective-temperature lower limit must be below the upper limit.")
        if self.rh_min_pct >= self.rh_max_pct:
            raise ValueError("Relative-humidity lower limit must be below the upper limit.")

    def contains(self, et_c: float, rh_pct: float) -> tuple[bool, bool, bool]:
        thermal_ok = self.et_min_c <= et_c <= self.et_max_c
        humidity_ok = self.rh_min_pct <= rh_pct <= self.rh_max_pct
        return thermal_ok and humidity_ok, thermal_ok, humidity_ok


@dataclass(frozen=True)
class SimulationInputs:
    controller: str = CONTROLLER_PID
    actuator: str = ACTUATOR_VALVE

    duration_h: float = 8.0
    timestep_s: int = 60
    start_hour: float = 8.0

    setpoint_c: float = 24.5
    initial_db_c: float = 28.8
    initial_rh_pct: float = 55.0
    pressure_kpa: float = P_ATM_STD_KPA

    outdoor_mean_c: float = 36.0
    outdoor_amplitude_c: float = 4.5
    outdoor_rh_pct: float = 25.0

    zone_ua_kw_per_k: float = 0.15
    thermal_capacity_kj_per_k: float = 2600.0
    room_volume_m3: float = 307.0
    infiltration_ach: float = 0.50

    internal_sensible_kw: float = 4.5
    internal_latent_kw: float = 0.90

    cooling_capacity_kw: float = 10.0
    supply_min_c: float = 12.5
    supply_max_c: float = 22.0
    compressor_cop: float = 3.20

    kp: float = 22.0  # percent per K
    ki: float = 0.070  # percent per (K.s)
    kd: float = 25.0  # percent per (K/min); derivative on measurement
    threshold_band_k: float = 0.6

    comfort: ComfortLimits = ComfortLimits()

    def validate(self) -> None:
        if self.controller not in CONTROLLERS:
            raise ValueError("Unknown controller.")
        if self.actuator not in ACTUATORS:
            raise ValueError("Unknown actuator.")
        if not 0.05 <= self.duration_h <= 24.0:
            raise ValueError("Simulation duration must be between 0.05 and 24 hours.")
        if self.timestep_s not in (30, 60, 120):
            raise ValueError("Time step must be 30, 60 or 120 seconds.")
        if not 0.0 <= self.start_hour < 24.0:
            raise ValueError("Start hour must be within a 24-hour clock.")
        if not 16.0 <= self.setpoint_c <= 30.0:
            raise ValueError("Cooling setpoint must be between 16 and 30 degC.")
        if self.supply_min_c >= self.setpoint_c or self.supply_max_c <= self.supply_min_c:
            raise ValueError("Check the minimum and maximum supply-air temperatures.")
        if self.cooling_capacity_kw <= 0.0:
            raise ValueError("Cooling capacity must be positive.")
        if self.thermal_capacity_kj_per_k <= 0.0:
            raise ValueError("Thermal capacitance must be positive.")
        if self.room_volume_m3 <= 0.0 or self.zone_ua_kw_per_k < 0.0:
            raise ValueError("Zone geometry and conductance must be physically valid.")
        if self.infiltration_ach < 0.0:
            raise ValueError("Infiltration cannot be negative.")
        if self.internal_sensible_kw < 0.0 or self.internal_latent_kw < 0.0:
            raise ValueError("Internal gains cannot be negative.")
        if self.compressor_cop <= 0.0:
            raise ValueError("COP must be positive.")
        if max(self.kp, self.ki, self.kd) < 0.0:
            raise ValueError("PID gains cannot be negative.")
        if self.threshold_band_k <= 0.0:
            raise ValueError("Threshold deadband must be positive.")
        if not 0.0 <= self.initial_rh_pct <= 100.0:
            raise ValueError("Initial relative humidity must be between 0 and 100 percent.")
        if not 0.0 <= self.outdoor_rh_pct <= 100.0:
            raise ValueError("Outdoor relative humidity must be between 0 and 100 percent.")
        self.comfort.validate()


@dataclass(frozen=True)
class SimulationResult:
    inputs: SimulationInputs
    time_h: np.ndarray
    clock_hour: np.ndarray
    room_db_c: np.ndarray
    room_rh_pct: np.ndarray
    room_w: np.ndarray
    room_et_c: np.ndarray
    outdoor_db_c: np.ndarray
    supply_db_c: np.ndarray
    valve_pct: np.ndarray
    cooling_kw: np.ndarray
    sensible_cooling_kw: np.ndarray
    latent_cooling_kw: np.ndarray
    comfort_ok: np.ndarray
    thermal_ok: np.ndarray
    humidity_ok: np.ndarray
    comfort_pct: float
    comfort_last_half_pct: float
    thermal_pct: float
    humidity_pct: float
    delivered_cooling_kwh: float
    estimated_electricity_kwh: float
    peak_cooling_kw: float
    final_db_c: float
    final_rh_pct: float
    final_et_c: float
    switching_count: int
    actuator_label: str

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Time (h)": self.time_h,
                "Clock hour": self.clock_hour,
                "Room dry-bulb (degC)": self.room_db_c,
                "Room RH (%)": self.room_rh_pct,
                "Effective temperature (degC)": self.room_et_c,
                "Outdoor dry-bulb (degC)": self.outdoor_db_c,
                "Supply air (degC)": self.supply_db_c,
                "Valve / cooling demand (%)": self.valve_pct,
                "Sensible cooling (kW)": self.sensible_cooling_kw,
                "Latent cooling (kW)": self.latent_cooling_kw,
                "Total cooling (kW)": self.cooling_kw,
                "Comfortable": self.comfort_ok.astype(int),
            }
        )


def effective_temperature_c(
    dry_bulb_c: float,
    relative_humidity_pct: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> tuple[float, float]:
    """Humidity-adjusted ET* teaching proxy and wet-bulb reference.

    ET* is anchored to dry-bulb at 50% RH.  The small linear humidity correction
    captures the direction and approximate magnitude of the ASHRAE effective
    temperature while remaining easy to explain in a student presentation.
    """
    if not 0.0 <= relative_humidity_pct <= 100.0:
        raise ValueError("Relative humidity must be between 0 and 100 percent.")
    wb = wet_bulb_from_rh(dry_bulb_c, relative_humidity_pct, pressure_kpa)
    et = dry_bulb_c + 0.04 * (relative_humidity_pct - 50.0)
    return et, wb


def _validate_time_step(inputs: SimulationInputs) -> tuple[int, float]:
    total_seconds = inputs.duration_h * 3600.0
    steps = int(round(total_seconds / inputs.timestep_s))
    if steps < 2:
        raise ValueError("Simulation is too short for the selected time step.")
    return steps, total_seconds / steps


def _pid_demand(
    error_k: float,
    integral: float,
    derivative_k_per_min: float,
    inputs: SimulationInputs,
) -> float:
    raw = (
        inputs.kp * error_k
        + inputs.ki * integral
        + inputs.kd * derivative_k_per_min
    )
    return min(100.0, max(0.0, raw))


def simulate_control(inputs: SimulationInputs) -> SimulationResult:
    """Run a fixed-step closed-loop zone simulation."""
    inputs.validate()
    steps, dt = _validate_time_step(inputs)
    duration_seconds = inputs.duration_h * 3600.0
    time_s = np.linspace(0.0, duration_seconds, steps + 1)
    time_h = time_s / 3600.0
    clock_hour = (inputs.start_hour + time_h) % 24.0

    room_t = float(inputs.initial_db_c)
    room_w = humidity_ratio_from_rh(
        room_t, inputs.initial_rh_pct, inputs.pressure_kpa
    )
    room_rh = float(inputs.initial_rh_pct)

    m_inf = (
        inputs.room_volume_m3
        * inputs.infiltration_ach
        / 3600.0
        / 0.87  # approximate dry-air density in this temperature band
    )
    cp_room = moist_air_specific_heat(room_w)
    # Size the supply airflow so that rated capacity is delivered at the design
    # temperature difference between setpoint and minimum supply temperature.
    design_dt = max(0.5, inputs.setpoint_c - inputs.supply_min_c)
    m_supply = inputs.cooling_capacity_kw / (cp_room * design_dt)

    room_t_hist = np.empty(steps + 1)
    room_rh_hist = np.empty(steps + 1)
    room_w_hist = np.empty(steps + 1)
    et_hist = np.empty(steps + 1)
    outdoor_t_hist = np.empty(steps + 1)
    supply_t_hist = np.empty(steps + 1)
    valve_hist = np.empty(steps + 1)
    cooling_hist = np.empty(steps + 1)
    sensible_hist = np.empty(steps + 1)
    latent_hist = np.empty(steps + 1)
    comfort_hist = np.ones(steps + 1, dtype=bool)
    thermal_hist = np.ones(steps + 1, dtype=bool)
    humidity_hist = np.ones(steps + 1, dtype=bool)

    integral = 0.0
    output = 0.0
    previous_t = room_t
    threshold_on = False
    switches = 0
    previous_on_state = False
    q_cool_previous = 0.0
    q_lat_previous = 0.0

    def record(index: int) -> None:
        nonlocal room_rh
        room_t_hist[index] = room_t
        room_w_hist[index] = room_w
        room_rh = relative_humidity_from_ratio(room_t, room_w, inputs.pressure_kpa)
        room_rh_hist[index] = room_rh
        et, _ = effective_temperature_c(room_t, room_rh, inputs.pressure_kpa)
        et_hist[index] = et
        outdoor_t_hist[index] = (
            inputs.outdoor_mean_c
            + inputs.outdoor_amplitude_c
            * math.cos(2.0 * math.pi * (clock_hour[index] - 15.0) / 24.0)
        )
        supply_t_hist[index] = (
            room_t - q_cool_previous / (m_supply * cp_room)
            if q_cool_previous > 1e-6
            else float("nan")
        )
        valve_hist[index] = output
        sensible_hist[index] = q_cool_previous
        latent_hist[index] = q_lat_previous
        cooling_hist[index] = q_cool_previous + q_lat_previous
        comfortable, thermo, humid = inputs.comfort.contains(et, room_rh)
        comfort_hist[index] = comfortable
        thermal_hist[index] = thermo
        humidity_hist[index] = humid

    record(0)

    for index in range(steps):
        hour_now = clock_hour[index]
        outdoor_t = (
            inputs.outdoor_mean_c
            + inputs.outdoor_amplitude_c
            * math.cos(2.0 * math.pi * (hour_now - 15.0) / 24.0)
        )
        outdoor_w = humidity_ratio_from_rh(
            outdoor_t, inputs.outdoor_rh_pct, inputs.pressure_kpa
        )

        room_rh = relative_humidity_from_ratio(
            room_t, room_w, inputs.pressure_kpa
        )

        if inputs.controller == CONTROLLER_PID:
            error = room_t - inputs.setpoint_c
            derivative = (room_t - previous_t) / (dt / 60.0)
            unsaturated = _pid_demand(error, integral, derivative, inputs)
            # Conditional integration anti-windup.
            if (0.0 < unsaturated < 100.0) or (
                unsaturated >= 100.0 and error < 0.0
            ) or (unsaturated <= 0.0 and error > 0.0):
                integral += error * dt
                unsaturated = _pid_demand(error, integral, derivative, inputs)
            output = min(100.0, max(0.0, unsaturated))
        else:
            if room_t > inputs.setpoint_c + inputs.threshold_band_k / 2.0:
                threshold_on = True
            elif room_t < inputs.setpoint_c - inputs.threshold_band_k / 2.0:
                threshold_on = False
            output = 100.0 if threshold_on else 0.0
            on_state = output > 50.0
            if on_state != previous_on_state:
                switches += 1
                previous_on_state = on_state

        # Sensible cooling delivered by the selected actuator model.
        if inputs.actuator == ACTUATOR_VALVE:
            q_sensible = inputs.cooling_capacity_kw * output / 100.0
        else:
            if output <= 0.25:
                q_sensible = 0.0
            else:
                sat_target = inputs.supply_max_c - (
                    inputs.supply_max_c - inputs.supply_min_c
                ) * output / 100.0
                available = m_supply * cp_room * max(0.0, room_t - sat_target)
                q_sensible = min(inputs.cooling_capacity_kw, available)
        q_sensible = max(0.0, min(inputs.cooling_capacity_kw, q_sensible))

        # Simplified wet-coil latent removal.  The coil surface remains cold at
        # part load, so a fraction of the moisture difference is removed even
        # when the sensible valve is only partly open.
        load_fraction = q_sensible / inputs.cooling_capacity_kw
        if load_fraction > 0.02:
            bpf_effective = 0.18 + 0.72 * (1.0 - load_fraction)
            w_adp = 0.92 * saturation_humidity_ratio(9.0, inputs.pressure_kpa)
            supply_w = room_w - (1.0 - bpf_effective) * max(0.0, room_w - w_adp)
            supply_w = max(0.0, min(room_w, supply_w))
            q_latent = max(0.0, m_supply * H_FG_0 * (room_w - supply_w))
        else:
            supply_w = room_w
            q_latent = 0.0

        q_ext_sensible = (
            inputs.zone_ua_kw_per_k * (outdoor_t - room_t)
            + m_inf * cp_room * (outdoor_t - room_t)
        )
        # Euler integration of the zone energy balance (kW = kJ/s).
        d_t = (
            inputs.internal_sensible_kw + q_ext_sensible - q_sensible
        ) / inputs.thermal_capacity_kj_per_k
        room_t = room_t + d_t * dt

        latent_gain_kg_s = inputs.internal_latent_kw / H_FG_0
        moisture_balance = (
            m_inf * (outdoor_w - room_w)
            + latent_gain_kg_s
            - m_supply * (room_w - supply_w)
        )
        moisture_capacity = max(60.0, inputs.room_volume_m3 * 1.18)
        room_w = room_w + moisture_balance * dt / moisture_capacity
        room_w = max(0.0, room_w)
        w_sat = saturation_humidity_ratio(room_t, inputs.pressure_kpa)
        if room_w > 0.999 * w_sat:
            room_w = 0.999 * w_sat

        previous_t = room_t_hist[index]
        q_cool_previous = q_sensible
        q_lat_previous = q_latent
        record(index + 1)

    # Replace NaN in supply-temperature record where the coil is off.
    supply_plot = supply_t_hist.copy()

    comfort_ok = comfort_hist
    # The first control period is treated as pull-down; last half is used for the
    # "maintained comfort" KPI shown on the dashboard.
    half_index = max(1, steps // 2)
    comfort_pct = 100.0 * float(np.mean(comfort_ok))
    comfort_last_half = 100.0 * float(np.mean(comfort_ok[half_index:]))
    thermal_pct = 100.0 * float(np.mean(thermal_hist))
    humidity_pct = 100.0 * float(np.mean(humidity_hist))
    delivered_kwh = float(np.sum(cooling_hist[1:]) * dt / 3600.0)
    electric_kwh = delivered_kwh / inputs.compressor_cop

    return SimulationResult(
        inputs=inputs,
        time_h=time_h,
        clock_hour=clock_hour,
        room_db_c=room_t_hist,
        room_rh_pct=room_rh_hist,
        room_w=room_w_hist,
        room_et_c=et_hist,
        outdoor_db_c=outdoor_t_hist,
        supply_db_c=supply_plot,
        valve_pct=valve_hist,
        cooling_kw=cooling_hist,
        sensible_cooling_kw=sensible_hist,
        latent_cooling_kw=latent_hist,
        comfort_ok=comfort_ok,
        thermal_ok=thermal_hist,
        humidity_ok=humidity_hist,
        comfort_pct=comfort_pct,
        comfort_last_half_pct=comfort_last_half,
        thermal_pct=thermal_pct,
        humidity_pct=humidity_pct,
        delivered_cooling_kwh=delivered_kwh,
        estimated_electricity_kwh=electric_kwh,
        peak_cooling_kw=float(np.max(cooling_hist)),
        final_db_c=float(room_t_hist[-1]),
        final_rh_pct=float(room_rh_hist[-1]),
        final_et_c=float(et_hist[-1]),
        switching_count=switches,
        actuator_label=(
            "Valve position (%)"
            if inputs.actuator == ACTUATOR_VALVE
            else "Supply-air setpoint (degC)"
        ),
    )


def controller_comparison(inputs: SimulationInputs) -> pd.DataFrame:
    """Simulate PID and threshold control with otherwise identical conditions."""
    rows = []
    for controller in CONTROLLERS:
        trial = SimulationInputs(
            **{
                **inputs.__dict__,
                "controller": controller,
            }
        )
        result = simulate_control(trial)
        rows.append(
            {
                "Controller": controller,
                "Comfort last half (%)": result.comfort_last_half_pct,
                "Humidity in band (%)": result.humidity_pct,
                "Delivered cooling (kWh)": result.delivered_cooling_kwh,
                "Estimated electricity (kWh)": result.estimated_electricity_kwh,
                "Switch changes": result.switching_count,
                "Final room temp (degC)": result.final_db_c,
                "Final RH (%)": result.final_rh_pct,
            }
        )
    return pd.DataFrame(rows)


def clock_ticks(start_hour: float, duration_h: float) -> tuple[list[float], list[str]]:
    """Sensible hourly clock ticks for Plotly charts."""
    end_hour = start_hour + duration_h
    tick_values: list[float] = []
    tick_labels: list[str] = []
    hour = math.floor(start_hour)
    while hour <= end_hour + 1e-9:
        if hour >= start_hour - 1e-9:
            tick_values.append(hour)
            tick_labels.append(f"{int(hour) % 24:02d}:00")
        hour += 1
    return tick_values, tick_labels
