"""One realistic design day for the quick-design recommendation.

The reduced-order model carries the same physics as Module 1 through a full
day: outdoor dry bulb follows a design-day sine, solar gain follows the main
window orientation, occupancy and internal gains follow the space schedule, and
the selected system modulates against a capacity limit.  The room has thermal
and moisture inertia, so morning pull-down, afternoon peaks and night setback
all appear in the result.

It is deliberately a teaching model: one zone, one air node, a fixed coil SHR
and a simple ambient/part-load COP correction.  It is not an energy-compliance
simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd

from .psychrometrics import (
    H_FG_0,
    humidity_ratio_from_rh,
    relative_humidity_from_ratio,
    saturation_humidity_ratio,
)
from .quick_design import QuickDesign
from .thermal_loads import ACTIVITY_PROFILES

SETBACK_C = 28.0
COMFORT_ET_MIN = 23.0
COMFORT_ET_MAX = 26.0
COMFORT_RH_MIN = 30.0
COMFORT_RH_MAX = 70.0

_STEP_S = 600.0
_STEPS_PER_HOUR = 6


def _day(values: list[float]) -> tuple[float, ...]:
    if len(values) != 24:
        raise ValueError("A daily schedule needs exactly 24 hourly values.")
    return tuple(float(value) for value in values)


SCHEDULES: dict[str, dict[str, tuple[float, ...]]] = {
    "office": {
        "occupancy": _day([0] * 7 + [0.2, 0.9, 1, 1, 1, 0.8, 0.7, 1, 1, 1, 0.6, 0.2] + [0] * 5),
        "available": _day([0] * 7 + [1] * 12 + [0] * 5),
        "lighting": _day([0.05] * 7 + [1] * 12 + [0.05] * 5),
        "equipment": _day([0.15] * 7 + [0.5] + [1] * 11 + [0.15] * 5),
    },
    "classroom": {
        "occupancy": _day([0] * 7 + [0.3, 1, 1, 1, 1, 1, 0.8, 0.5, 0.2] + [0] * 8),
        "available": _day([0] * 7 + [1] * 9 + [0] * 8),
        "lighting": _day([0.05] * 7 + [1] * 9 + [0.05] * 8),
        "equipment": _day([0.1] * 7 + [0.4] + [1] * 6 + [0.3, 0.1] + [0.1] * 8),
    },
    "retail": {
        "occupancy": _day([0] * 9 + [0.4] + [1] * 12 + [0.5] + [0] * 1),
        "available": _day([0] * 9 + [1] * 15),
        "lighting": _day([0.05] * 9 + [1] * 14 + [0.05]),
        "equipment": _day([0.2] * 9 + [1] * 14 + [0.2]),
    },
    "restaurant": {
        "occupancy": _day([0] * 10 + [0.3, 0.7, 0.7, 0.7, 0.7, 0.4] + [1] * 6 + [0.6] + [0]),
        "available": _day([0] * 10 + [1] * 14),
        "lighting": _day([0.05] * 10 + [1] * 14),
        "equipment": _day([0.2] * 10 + [1] * 14),
    },
    "residential": {
        "occupancy": _day([0.8] * 7 + [0.5] + [0.3] * 4 + [0.4] * 5 + [1] * 7),
        "available": _day([1, 1, 1] + [0] * 8 + [1] * 13),
        "lighting": _day([0.3] * 7 + [0.4] * 11 + [1] * 6),
        "equipment": _day([0.2] * 7 + [0.5] * 11 + [1] * 6),
    },
    "assembly": {
        "occupancy": _day([0, 0, 0, 0, 0.4, 0.9, 0.5, 0.15, 0.15, 0.15, 0.15, 0.15,
                           0.8, 0.5, 0.2, 0.2, 0.2, 0.7, 0.5, 0.3, 0.9, 0.6, 0.2, 0]),
        "available": _day([0, 0, 0, 0] + [1] * 19 + [0]),
        "lighting": _day([0.05] * 4 + [1] * 19 + [0.05]),
        "equipment": _day([0.1] * 4 + [0.7] * 19 + [0.1]),
    },
    "clinic": {
        "occupancy": _day([0] * 7 + [0.3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.2] + [0] * 5),
        "available": _day([0] * 7 + [1] * 12 + [0] * 5),
        "lighting": _day([0.05] * 7 + [1] * 12 + [0.05] * 5),
        "equipment": _day([0.2] * 7 + [1] * 12 + [0.2] * 5),
    },
}

SOLAR_SHAPES: dict[str, tuple[float, ...]] = {
    "east": _day([0] * 6 + [0.08, 0.30, 0.62, 0.85, 0.95, 0.90, 0.76, 0.55, 0.30, 0.12, 0.03, 0] + [0] * 6),
    "south": _day([0] * 6 + [0.05, 0.18, 0.42, 0.66, 0.85, 0.96, 1.00, 0.95, 0.82, 0.62, 0.38, 0.16] + [0.04] + [0] * 5),
    "west": _day([0] * 6 + [0, 0.03, 0.08, 0.15, 0.25, 0.40, 0.58, 0.75, 0.90, 0.97, 0.90, 0.72] + [0.50, 0.28, 0.10, 0.02, 0, 0]),
    "north": _day([0] * 6 + [0.05, 0.12, 0.20, 0.26, 0.30, 0.32, 0.33, 0.32, 0.28, 0.22, 0.16, 0.09] + [0.03] + [0] * 5),
    "roof": _day([0] * 5 + [0.05, 0.15, 0.30, 0.48, 0.65, 0.80, 0.90, 0.97, 1.00, 0.97, 0.90, 0.78] + [0.62, 0.45, 0.28, 0.14, 0.05, 0] + [0]),
}


@dataclass(frozen=True)
class DayResult:
    design: QuickDesign
    time_h: np.ndarray
    outdoor_db_c: np.ndarray
    outdoor_rh_pct: np.ndarray
    room_db_c: np.ndarray
    setpoint_c: np.ndarray
    room_rh_pct: np.ndarray
    room_et_c: np.ndarray
    occupancy: np.ndarray
    available: np.ndarray
    cooling_sensible_kw: np.ndarray
    cooling_latent_kw: np.ndarray
    cooling_total_kw: np.ndarray
    capacity_kw: np.ndarray
    electric_kw: np.ndarray
    envelope_kw: np.ndarray
    solar_kw: np.ndarray
    internal_kw: np.ndarray
    ventilation_kw: np.ndarray
    comfort_ok: np.ndarray
    occupied: np.ndarray
    peak_hour: float
    peak_cooling_kw: float
    peak_delivered_kw: float
    peak_electric_kw: float
    cooling_energy_kwh: float
    electric_energy_kwh: float
    occupied_comfort_pct: float
    unmet_hours: float
    max_rh_pct: float
    min_rh_pct: float
    day_cop: float
    headroom_pct: float
    system_on_hours: float

    def at_hour(self, hour: float) -> dict[str, float | bool]:
        index = int(round(min(23.999, max(0.0, hour)) * _STEPS_PER_HOUR))
        return {
            "outdoor_c": float(self.outdoor_db_c[index]),
            "room_c": float(self.room_db_c[index]),
            "setpoint_c": float(self.setpoint_c[index]),
            "rh_pct": float(self.room_rh_pct[index]),
            "cooling_kw": float(self.cooling_total_kw[index]),
            "electric_kw": float(self.electric_kw[index]),
            "part_load_pct": 100.0 * float(self.cooling_total_kw[index]) / max(1e-9, float(self.capacity_kw[index])),
            "comfort": bool(self.comfort_ok[index]),
            "occupied": bool(self.occupied[index]),
            "system_on": bool(self.available[index] > 0.5),
        }

    def hourly_frame(self) -> pd.DataFrame:
        indices = [min(len(self.time_h) - 1, int(hour * _STEPS_PER_HOUR)) for hour in range(24)]
        rows = []
        for hour, index in enumerate(indices):
            rows.append(
                {
                    "Hour": f"{hour:02d}:00",
                    "Outdoor DB (degC)": float(self.outdoor_db_c[index]),
                    "Room DB (degC)": float(self.room_db_c[index]),
                    "Setpoint (degC)": float(self.setpoint_c[index]),
                    "RH (%)": float(self.room_rh_pct[index]),
                    "Cooling (kW)": float(self.cooling_total_kw[index]),
                    "Capacity (kW)": float(self.capacity_kw[index]),
                    "Electric demand (kW)": float(self.electric_kw[index]),
                    "Occupied": bool(self.occupied[index]),
                    "Comfortable": bool(self.comfort_ok[index]),
                }
            )
        return pd.DataFrame(rows)


def _schedule_at(values: tuple[float, ...] | np.ndarray, hours: np.ndarray) -> np.ndarray:
    """Sample a 24-value schedule with linear interpolation, including 24:00."""
    positions = np.arange(24, dtype=float)
    extended = np.concatenate([np.asarray(values, dtype=float), np.asarray(values, dtype=float)[:1]])
    return np.interp(hours, np.append(positions, 24.0), extended)


def _solar_at(shape: str, hours: np.ndarray) -> np.ndarray:
    return _schedule_at(SOLAR_SHAPES[shape], hours)


def simulate_design_day(design: QuickDesign, *, capacity_kw: float | None = None) -> DayResult:
    """Run a 24-hour design day at ten-minute resolution."""
    load = design.load
    space = design.space
    schedule = SCHEDULES[space.schedule]
    capacity = float(capacity_kw if capacity_kw is not None else design.recommendation.capacity_kw)
    if capacity <= 0.0:
        raise ValueError("The selected system capacity must be positive.")

    n_steps = 24 * _STEPS_PER_HOUR
    time_h = np.linspace(0.0, 24.0, n_steps + 1)
    hours = np.minimum(time_h, 23.999)

    occupancy = _schedule_at(schedule["occupancy"], hours)
    available = _schedule_at(schedule["available"], hours)
    lighting = _schedule_at(schedule["lighting"], hours)
    equipment = _schedule_at(schedule["equipment"], hours)
    available_flag = (available > 0.5).astype(float)
    # Start the plant two hours before the space is needed, then reset the
    # setpoint through a short first-order ramp.  This is how a real building
    # avoids a brutal morning pull-down.
    precool = _schedule_at(schedule["available"], np.minimum(hours + 2.0, 23.999))
    active_flag = np.maximum(available_flag, (precool > 0.5).astype(float))
    setpoint_target = np.where(active_flag > 0.5, design.inputs.indoor_db_c, SETBACK_C)
    setpoint = np.empty_like(setpoint_target)
    setpoint[0] = setpoint_target[0]
    for index in range(1, len(setpoint)):
        setpoint[index] = setpoint[index - 1] + (
            setpoint_target[index] - setpoint[index - 1]
        ) * min(1.0, _STEP_S / 3600.0)

    city = design.city
    mean_c = city.db_c - city.daily_swing_k / 2.0
    amplitude = city.daily_swing_k / 2.0
    outdoor_db = mean_c + amplitude * np.cos(2.0 * math.pi * (time_h - 15.0) / 24.0)
    outdoor_state = load.outdoor_state
    outdoor_w = outdoor_state.humidity_ratio
    v_out = outdoor_state.specific_volume_m3_kg

    solar_shape = _solar_at(design.orientation.shape, hours)
    roof_shape = _solar_at("roof", hours)

    wall_solar = design.orientation.wall_solar_w_m2
    roof_solar = 950.0
    wall_u = load.inputs.wall_u_w_m2k
    roof_u = load.inputs.roof_u_w_m2k
    window_u = load.inputs.window_u_w_m2k
    wall_area = load.net_wall_area_m2
    roof_area = load.floor_area_m2
    window_area = load.inputs.window_area_m2
    film = load.inputs.outdoor_film_w_m2k
    shgc = load.inputs.window_shgc
    shading = load.inputs.shading_factor

    profile = load.inputs.activity_key
    activity = ACTIVITY_PROFILES[profile]
    people_sensible_peak = load.inputs.occupants * activity["sensible_w"] / 1000.0
    people_latent_peak = load.inputs.occupants * activity["latent_w"] / 1000.0
    lighting_peak = load.inputs.lighting_w_m2 * load.floor_area_m2 / 1000.0
    equipment_peak = load.inputs.equipment_w / 1000.0

    m_oa = load.ventilation_mass_kg_s
    m_inf = load.infiltration_mass_kg_s
    m_air = m_oa + m_inf
    cp = 1.021

    shr = max(0.55, min(0.95, load.design_shr))
    cap_sensible = capacity * shr
    moisture_capacity = max(80.0, load.volume_m3 * 1.15 * 2.5)

    room_t = (
        design.inputs.indoor_db_c + 0.2
        if active_flag[0] > 0.5
        else SETBACK_C + 0.3
    )
    room_w = humidity_ratio_from_rh(room_t, design.inputs.indoor_rh_pct, load.inputs.pressure_kpa)

    arrays = {
        name: np.zeros(n_steps + 1)
        for name in (
            "outdoor_db", "outdoor_rh", "room_db", "setpoint", "room_rh", "room_et",
            "q_sens", "q_lat", "q_total", "electric", "envelope", "solar",
            "internal", "ventilation", "comfort", "occupied", "available", "capacity",
            "required",
        )
    }
    integral = 0.0
    valve = 0.0

    f = load.inputs
    for step in range(n_steps + 1):
        hour = hours[step]
        t_out = float(outdoor_db[step])
        t_set = float(setpoint[step])
        occ = float(occupancy[step])
        is_available = active_flag[step] > 0.5

        env = (
            wall_u * wall_area * (t_out - room_t + f.wall_absorptivity * wall_solar * solar_shape[step] / film)
            + roof_u * roof_area * (t_out - room_t + f.roof_absorptivity * roof_solar * roof_shape[step] / film)
            + window_u * window_area * (t_out - room_t)
        ) / 1000.0
        solar = shgc * shading * window_area * wall_solar * solar_shape[step] / 1000.0
        internal = (
            people_sensible_peak * occ
            + lighting_peak * lighting[step]
            + equipment_peak * equipment[step]
        )
        ventilation = m_air * cp * (t_out - room_t)
        latent_gain = (
            m_air * H_FG_0 * (outdoor_w - room_w)
            + people_latent_peak * occ
        )

        gains = env + solar + internal + ventilation

        # A real plant trims a load-compensated feed-forward command rather than
        # driving the room with pure proportional gain.  With ten-minute steps a
        # high-gain P-only loop alternates between full cooling and off, which is
        # both unrealistic and ugly on the chart.
        if is_available:
            error = room_t - t_set
            feed_forward = max(0.0, min(1.0, gains / max(1e-9, cap_sensible)))
            raw = feed_forward + 0.8 * error + integral
            if 0.0 < raw < 1.0 or (raw >= 1.0 and error < 0.0) or (raw <= 0.0 and error > 0.0):
                integral += 0.00030 * error * _STEP_S
                integral = max(-0.25, min(0.25, integral))
                raw = feed_forward + 0.8 * error + integral
            u = max(0.0, min(1.0, raw))
        else:
            u = 0.0
            integral = 0.0

        # Coil and valve respond over a few minutes; the first-order lag also
        # keeps the delivered capacity continuous between timesteps.
        valve += (u - valve) * (1.0 - math.exp(-_STEP_S / 300.0))
        if not is_available:
            valve = 0.0
        q_sens = valve * cap_sensible
        if q_sens < 1e-3:
            q_sens = 0.0

        if q_sens > 0.05:
            latent_capacity = q_sens * (1.0 - shr) / shr
            q_lat = min(max(0.0, latent_gain), latent_capacity)
        else:
            q_lat = 0.0
        q_total = q_sens + q_lat

        d_t = (gains - q_sens) * _STEP_S / (space.capacitance_kj_m2k * load.floor_area_m2)
        room_t += d_t
        room_t = max(10.0, min(60.0, room_t))

        d_w = (latent_gain - q_lat) * _STEP_S / H_FG_0 / moisture_capacity
        room_w = max(0.0, room_w + d_w)
        w_sat = saturation_humidity_ratio(room_t, f.pressure_kpa)
        room_w = min(room_w, 0.995 * w_sat)
        rh = relative_humidity_from_ratio(room_t, room_w, f.pressure_kpa)
        rh = max(1.0, min(100.0, rh))

        cop_ambient = design.recommendation.cop_rated * (
            1.0 - 0.010 * max(0.0, t_out - 35.0) + 0.004 * max(0.0, 35.0 - t_out)
        )
        part_load = q_sens / max(1e-9, cap_sensible) if is_available else 0.0
        cop_eff = max(1.8, cop_ambient * (0.88 + 0.12 * part_load))
        fan_kw = (
            design.recommendation.fan_kw_per_1000_m3h * design.recommendation.airflow_m3h / 1000.0
            if q_sens > 0.05
            else 0.0
        )
        electric = (q_total / cop_eff if q_total > 0.0 else 0.0) + fan_kw

        et = room_t + 0.04 * (rh - 50.0)
        comfortable = (
            COMFORT_ET_MIN <= et <= COMFORT_ET_MAX
            and COMFORT_RH_MIN <= rh <= COMFORT_RH_MAX
        )

        arrays["outdoor_db"][step] = t_out
        arrays["outdoor_rh"][step] = relative_humidity_from_ratio(
            t_out, outdoor_w, f.pressure_kpa
        )
        arrays["room_db"][step] = room_t
        arrays["setpoint"][step] = t_set
        arrays["room_rh"][step] = rh
        arrays["room_et"][step] = et
        arrays["q_sens"][step] = q_sens
        arrays["q_lat"][step] = q_lat
        arrays["q_total"][step] = q_total
        arrays["electric"][step] = electric
        arrays["envelope"][step] = env
        arrays["solar"][step] = solar
        arrays["internal"][step] = internal
        arrays["ventilation"][step] = ventilation
        arrays["comfort"][step] = 1.0 if comfortable else 0.0
        arrays["occupied"][step] = 1.0 if occ >= 0.15 else 0.0
        arrays["available"][step] = active_flag[step]
        arrays["capacity"][step] = capacity
        arrays["required"][step] = max(0.0, gains) if is_available else 0.0

    q_total = arrays["q_total"]
    required = arrays["required"]
    peak_index = int(np.argmax(required))
    peak_kw = float(required[peak_index])
    delivered_peak = float(np.max(q_total))
    occupied = arrays["occupied"] > 0.5
    evaluated = occupied & (arrays["available"] > 0.5)
    evaluated_count = int(np.count_nonzero(evaluated))
    comfort_pct = (
        100.0 * float(np.count_nonzero(arrays["comfort"][evaluated])) / evaluated_count
        if evaluated_count
        else 100.0
    )
    unmet = float(
        np.count_nonzero(evaluated & (arrays["room_db"] > arrays["setpoint"] + 0.5))
    ) * _STEP_S / 3600.0
    cooling_kwh = float(np.sum(q_total[1:]) * _STEP_S / 3600.0)
    electric_kwh = float(np.sum(arrays["electric"][1:]) * _STEP_S / 3600.0)
    # Day COP is cooling energy divided by the electricity that produced it,
    # including the fan share; it is a whole-day indicator, not a rated COP.
    cop_day = cooling_kwh / max(1e-9, electric_kwh)
    headroom = 100.0 * (1.0 - peak_kw / capacity) if capacity > 0.0 else 0.0

    return DayResult(
        design=design,
        time_h=time_h,
        outdoor_db_c=arrays["outdoor_db"],
        outdoor_rh_pct=arrays["outdoor_rh"],
        room_db_c=arrays["room_db"],
        setpoint_c=arrays["setpoint"],
        room_rh_pct=arrays["room_rh"],
        room_et_c=arrays["room_et"],
        occupancy=occupancy,
        available=arrays["available"],
        cooling_sensible_kw=arrays["q_sens"],
        cooling_latent_kw=arrays["q_lat"],
        cooling_total_kw=q_total,
        capacity_kw=arrays["capacity"],
        electric_kw=arrays["electric"],
        envelope_kw=arrays["envelope"],
        solar_kw=arrays["solar"],
        internal_kw=arrays["internal"],
        ventilation_kw=arrays["ventilation"],
        comfort_ok=arrays["comfort"] > 0.5,
        occupied=occupied,
        peak_hour=float(time_h[peak_index]),
        peak_cooling_kw=peak_kw,
        peak_delivered_kw=delivered_peak,
        peak_electric_kw=float(np.max(arrays["electric"])),
        cooling_energy_kwh=cooling_kwh,
        electric_energy_kwh=electric_kwh,
        occupied_comfort_pct=comfort_pct,
        unmet_hours=unmet,
        max_rh_pct=float(np.max(arrays["room_rh"])),
        min_rh_pct=float(np.min(arrays["room_rh"])),
        day_cop=cop_day,
        headroom_pct=headroom,
        system_on_hours=float(np.sum(active_flag[1:]) * _STEP_S / 3600.0),
    )
