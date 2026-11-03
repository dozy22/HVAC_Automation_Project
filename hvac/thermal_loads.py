"""Peak cooling-load calculation based on ASHRAE-style steady design methods.

Scope: sensible and latent room gains, plus the outdoor-air ventilation load.
This is an educational design estimator, not a replacement for a full
hourly/radiant-time-series load program.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

import pandas as pd

from .psychrometrics import P_ATM_STD_KPA, H_FG_0, PsychrometricState, psychrometric_state

TR_KW = 3.5168525  # kW per ton of refrigeration

ACTIVITY_PROFILES: dict[str, dict[str, float]] = {
    "Seated, quiet": {"total_w": 105.0, "sensible_w": 60.0, "latent_w": 45.0},
    "Office work": {"total_w": 130.0, "sensible_w": 75.0, "latent_w": 55.0},
    "Standing / light work": {"total_w": 160.0, "sensible_w": 85.0, "latent_w": 75.0},
    "Light bench work": {"total_w": 235.0, "sensible_w": 130.0, "latent_w": 105.0},
    "Moderate activity": {"total_w": 295.0, "sensible_w": 170.0, "latent_w": 125.0},
    "Heavy work": {"total_w": 440.0, "sensible_w": 250.0, "latent_w": 190.0},
}

WALL_OPTIONS: dict[str, dict[str, float]] = {
    "Brick wall, 200 mm, uninsulated": {"u": 1.70, "absorptivity": 0.65},
    "Brick + 50 mm insulation": {"u": 0.55, "absorptivity": 0.65},
    "Concrete + 50 mm insulation": {"u": 0.48, "absorptivity": 0.60},
    "Insulated sandwich panel": {"u": 0.30, "absorptivity": 0.45},
    "Glazed curtain wall": {"u": 2.40, "absorptivity": 0.30},
}

ROOF_OPTIONS: dict[str, dict[str, float]] = {
    "Concrete roof, 150 mm, uninsulated": {"u": 1.75, "absorptivity": 0.75},
    "Concrete + 50 mm insulation": {"u": 0.55, "absorptivity": 0.75},
    "Concrete + 75 mm insulation": {"u": 0.35, "absorptivity": 0.75},
    "Metal deck + insulation": {"u": 0.40, "absorptivity": 0.55},
}

GLAZING_OPTIONS: dict[str, dict[str, float]] = {
    "Single clear glass": {"u": 5.80, "shgc": 0.86},
    "Double clear glass": {"u": 2.80, "shgc": 0.72},
    "Double low-e glass": {"u": 1.60, "shgc": 0.40},
    "Triple low-e glass": {"u": 0.80, "shgc": 0.28},
}

WEATHER_PRESETS: dict[str, dict[str, float]] = {
    "Hot dry example": {"db_c": 45.0, "wb_c": 24.0},
    "Hot humid example": {"db_c": 38.0, "wb_c": 28.0},
    "Mild example": {"db_c": 32.0, "wb_c": 22.0},
    "Custom": {},
}

WALL_SOLAR_OPTIONS: dict[str, float] = {
    "West facade (afternoon peak)": 600.0,
    "South facade": 420.0,
    "East facade (morning peak)": 480.0,
    "North facade": 130.0,
    "Custom / user value": 600.0,
}


@dataclass(frozen=True)
class LoadInputs:
    """All inputs needed for the peak cooling-load estimate."""

    project_name: str = "HVAC design studio"
    length_m: float = 12.0
    width_m: float = 8.0
    height_m: float = 3.2
    exposed_wall_fraction: float = 0.80

    wall_u_w_m2k: float = 0.55
    wall_absorptivity: float = 0.65
    roof_u_w_m2k: float = 0.35
    roof_absorptivity: float = 0.75
    window_u_w_m2k: float = 1.60
    window_shgc: float = 0.40
    window_area_m2: float = 18.0
    shading_factor: float = 0.85

    wall_solar_w_m2: float = 600.0
    roof_solar_w_m2: float = 950.0
    outdoor_film_w_m2k: float = 20.0

    outdoor_db_c: float = 45.0
    outdoor_wb_c: float = 24.0
    indoor_db_c: float = 24.0
    indoor_rh_pct: float = 50.0
    pressure_kpa: float = P_ATM_STD_KPA

    occupants: int = 20
    activity_key: str = "Office work"
    lighting_w_m2: float = 8.0
    equipment_w: float = 1500.0

    infiltration_ach: float = 0.50
    ventilation_l_s_person: float = 10.0


@dataclass(frozen=True)
class LoadComponent:
    name: str
    scope: str
    category: str
    sensible_kw: float
    latent_kw: float
    basis: str = ""

    @property
    def total_kw(self) -> float:
        return self.sensible_kw + self.latent_kw


@dataclass(frozen=True)
class LoadResult:
    inputs: LoadInputs
    components: tuple[LoadComponent, ...]
    room_sensible_kw: float
    room_latent_kw: float
    room_total_kw: float
    room_rshf: float
    ventilation_sensible_kw: float
    ventilation_latent_kw: float
    ventilation_total_kw: float
    design_sensible_kw: float
    design_latent_kw: float
    design_total_kw: float
    design_shr: float
    design_tr: float
    floor_area_m2: float
    volume_m3: float
    net_wall_area_m2: float
    gross_wall_area_m2: float
    outdoor_state: PsychrometricState
    indoor_state: PsychrometricState
    ventilation_m3_s: float
    infiltration_m3_s: float
    ventilation_mass_kg_s: float
    infiltration_mass_kg_s: float
    notes: tuple[str, ...] = field(default_factory=tuple)

    def component_frame(self, include_ventilation: bool = True) -> pd.DataFrame:
        rows = []
        for component in self.components:
            if not include_ventilation and component.scope != "Room":
                continue
            rows.append(
                {
                    "Scope": component.scope,
                    "Category": component.category,
                    "Item": component.name,
                    "Sensible (kW)": component.sensible_kw,
                    "Latent (kW)": component.latent_kw,
                    "Total (kW)": component.total_kw,
                    "Basis": component.basis,
                }
            )
        return pd.DataFrame(rows)

    def summary_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Metric": [
                    "Room sensible heat (RSH)",
                    "Room latent heat (RLH)",
                    "Room total heat",
                    "Room sensible heat factor (RSHF)",
                    "Outdoor ventilation sensible",
                    "Outdoor ventilation latent",
                    "Design sensible heat (incl. OA)",
                    "Design latent heat (incl. OA)",
                    "Design cooling load",
                    "Design load in tons of refrigeration",
                ],
                "Value": [
                    self.room_sensible_kw,
                    self.room_latent_kw,
                    self.room_total_kw,
                    self.room_rshf * 100.0,
                    self.ventilation_sensible_kw,
                    self.ventilation_latent_kw,
                    self.design_sensible_kw,
                    self.design_latent_kw,
                    self.design_total_kw,
                    self.design_tr,
                ],
                "Unit": ["kW", "kW", "kW", "%", "kW", "kW", "kW", "kW", "kW", "TR"],
            }
        )


def default_load_inputs() -> LoadInputs:
    """A complete, presentation-ready example design case."""
    return LoadInputs()


def _validate(inputs: LoadInputs) -> None:
    positives = {
        "Room length": inputs.length_m,
        "Room width": inputs.width_m,
        "Room height": inputs.height_m,
        "Wall U-value": inputs.wall_u_w_m2k,
        "Roof U-value": inputs.roof_u_w_m2k,
        "Window U-value": inputs.window_u_w_m2k,
        "Outdoor film coefficient": inputs.outdoor_film_w_m2k,
        "Outdoor dry-bulb temperature": inputs.outdoor_db_c + 100.0,
        "Indoor dry-bulb temperature": inputs.indoor_db_c + 100.0,
    }
    for name, value in positives.items():
        if not math.isfinite(float(value)) or float(value) <= 0.0:
            raise ValueError(f"{name} must be positive.")
    if inputs.occupants < 0:
        raise ValueError("Occupant count cannot be negative.")
    if inputs.lighting_w_m2 < 0.0 or inputs.equipment_w < 0.0:
        raise ValueError("Internal gains cannot be negative.")
    if inputs.infiltration_ach < 0.0 or inputs.ventilation_l_s_person < 0.0:
        raise ValueError("Airflow inputs cannot be negative.")
    if not 0.0 <= inputs.exposed_wall_fraction <= 1.0:
        raise ValueError("Exposed wall fraction must be between 0 and 1.")
    if not 0.0 <= inputs.shading_factor <= 1.0:
        raise ValueError("Shading factor must be between 0 and 1.")
    if not 0.0 < inputs.window_shgc <= 1.0:
        raise ValueError("SHGC must be greater than 0 and no more than 1.")
    if not 0.0 <= inputs.wall_absorptivity <= 1.0:
        raise ValueError("Wall absorptivity must be between 0 and 1.")
    if not 0.0 <= inputs.roof_absorptivity <= 1.0:
        raise ValueError("Roof absorptivity must be between 0 and 1.")
    if not 0.0 <= inputs.indoor_rh_pct <= 100.0:
        raise ValueError("Indoor relative humidity must be between 0 and 100 percent.")
    if inputs.outdoor_wb_c >= inputs.outdoor_db_c:
        raise ValueError("Outdoor wet-bulb temperature must be below outdoor dry-bulb.")
    if not 5.0 <= inputs.indoor_db_c <= 35.0:
        raise ValueError("Indoor setpoint must be between 5 and 35 degC.")
    if inputs.window_area_m2 < 0.0:
        raise ValueError("Window area cannot be negative.")
    if inputs.activity_key not in ACTIVITY_PROFILES:
        raise ValueError("Unknown occupant activity profile.")


def calculate_thermal_load(inputs: LoadInputs) -> LoadResult:
    """Compute room, ventilation and total design cooling loads."""
    _validate(inputs)

    area = inputs.length_m * inputs.width_m
    volume = area * inputs.height_m
    perimeter = 2.0 * (inputs.length_m + inputs.width_m)
    gross_wall = perimeter * inputs.height_m * inputs.exposed_wall_fraction
    if inputs.window_area_m2 > gross_wall + 1e-6:
        raise ValueError("Window area exceeds the exposed wall area for these dimensions.")
    net_wall = max(0.0, gross_wall - inputs.window_area_m2)

    outdoor = psychrometric_state(
        inputs.outdoor_db_c,
        inputs.pressure_kpa,
        wet_bulb_c=inputs.outdoor_wb_c,
    )
    indoor = psychrometric_state(
        inputs.indoor_db_c,
        inputs.pressure_kpa,
        relative_humidity_pct=inputs.indoor_rh_pct,
    )

    # Sol-air temperatures make the opaque-envelope calculation explicitly
    # dependent on solar exposure and surface absorptivity.
    t_sol_wall = (
        inputs.outdoor_db_c
        + inputs.wall_absorptivity * inputs.wall_solar_w_m2 / inputs.outdoor_film_w_m2k
    )
    t_sol_roof = (
        inputs.outdoor_db_c
        + inputs.roof_absorptivity * inputs.roof_solar_w_m2 / inputs.outdoor_film_w_m2k
    )
    q_wall = inputs.wall_u_w_m2k * net_wall * (t_sol_wall - inputs.indoor_db_c) / 1000.0
    q_roof = (
        inputs.roof_u_w_m2k
        * area
        * (t_sol_roof - inputs.indoor_db_c)
        / 1000.0
    )
    q_window_conduction = (
        inputs.window_u_w_m2k
        * inputs.window_area_m2
        * (inputs.outdoor_db_c - inputs.indoor_db_c)
        / 1000.0
    )
    q_window_solar = (
        inputs.window_shgc
        * inputs.window_area_m2
        * inputs.wall_solar_w_m2
        * inputs.shading_factor
        / 1000.0
    )

    profile = ACTIVITY_PROFILES[inputs.activity_key]
    q_people_sensible = inputs.occupants * profile["sensible_w"] / 1000.0
    q_people_latent = inputs.occupants * profile["latent_w"] / 1000.0
    q_lighting = inputs.lighting_w_m2 * area / 1000.0
    q_equipment = inputs.equipment_w / 1000.0

    infiltration_flow_m3_s = volume * inputs.infiltration_ach / 3600.0
    # Air crossing the envelope carries outdoor thermodynamic properties.
    infiltration_mass = infiltration_flow_m3_s / outdoor.specific_volume_m3_kg
    infiltration_total = infiltration_mass * (
        outdoor.enthalpy_kj_kg - indoor.enthalpy_kj_kg
    )
    infiltration_latent = (
        infiltration_mass
        * H_FG_0
        * (outdoor.humidity_ratio - indoor.humidity_ratio)
    )
    infiltration_sensible = infiltration_total - infiltration_latent

    ventilation_flow_m3_s = (
        inputs.occupants * inputs.ventilation_l_s_person / 1000.0
    )
    ventilation_mass = (
        ventilation_flow_m3_s / outdoor.specific_volume_m3_kg
        if ventilation_flow_m3_s > 0.0
        else 0.0
    )
    ventilation_total = ventilation_mass * (
        outdoor.enthalpy_kj_kg - indoor.enthalpy_kj_kg
    )
    ventilation_latent = (
        ventilation_mass
        * H_FG_0
        * (outdoor.humidity_ratio - indoor.humidity_ratio)
    )
    ventilation_sensible = ventilation_total - ventilation_latent

    components = [
        LoadComponent(
            "Wall conduction",
            "Room",
            "Envelope",
            q_wall,
            0.0,
            f"Sol-air {t_sol_wall:.1f} degC; net wall {net_wall:.1f} m2",
        ),
        LoadComponent(
            "Roof conduction",
            "Room",
            "Envelope",
            q_roof,
            0.0,
            f"Sol-air {t_sol_roof:.1f} degC; roof {area:.1f} m2",
        ),
        LoadComponent(
            "Window conduction",
            "Room",
            "Envelope",
            q_window_conduction,
            0.0,
            f"U={inputs.window_u_w_m2k:.2f} W/m2K",
        ),
        LoadComponent(
            "Window solar transmission",
            "Room",
            "Solar",
            q_window_solar,
            0.0,
            f"SHGC={inputs.window_shgc:.2f}; shading={inputs.shading_factor:.2f}",
        ),
        LoadComponent(
            "Occupants, sensible",
            "Room",
            "Internal",
            q_people_sensible,
            0.0,
            f"{inputs.occupants} people; {profile['sensible_w']:.0f} W/person",
        ),
        LoadComponent(
            "Occupants, latent",
            "Room",
            "Internal",
            0.0,
            q_people_latent,
            f"{inputs.occupants} people; {profile['latent_w']:.0f} W/person",
        ),
        LoadComponent(
            "Lighting",
            "Room",
            "Internal",
            q_lighting,
            0.0,
            f"{inputs.lighting_w_m2:.1f} W/m2 over {area:.1f} m2",
        ),
        LoadComponent(
            "Equipment",
            "Room",
            "Internal",
            q_equipment,
            0.0,
            "Connected equipment heat gain",
        ),
        LoadComponent(
            "Infiltration, sensible",
            "Room",
            "Infiltration",
            infiltration_sensible,
            0.0,
            f"{inputs.infiltration_ach:.2f} ACH",
        ),
        LoadComponent(
            "Infiltration, latent",
            "Room",
            "Infiltration",
            0.0,
            infiltration_latent,
            f"Humidity ratio difference {1000 * (outdoor.humidity_ratio - indoor.humidity_ratio):+.2f} g/kg",
        ),
        LoadComponent(
            "Outdoor ventilation, sensible",
            "Outdoor air",
            "Ventilation",
            ventilation_sensible,
            0.0,
            f"{ventilation_flow_m3_s * 3600:.0f} m3/h",
        ),
        LoadComponent(
            "Outdoor ventilation, latent",
            "Outdoor air",
            "Ventilation",
            0.0,
            ventilation_latent,
            f"{inputs.ventilation_l_s_person:.1f} L/s per person",
        ),
    ]

    room_components = [c for c in components if c.scope == "Room"]
    room_sensible = sum(c.sensible_kw for c in room_components)
    room_latent = sum(c.latent_kw for c in room_components)
    room_total = room_sensible + room_latent
    room_rshf = room_sensible / room_total if room_total > 1e-9 else 0.0
    design_sensible = room_sensible + ventilation_sensible
    design_latent = room_latent + ventilation_latent
    design_total = design_sensible + design_latent
    design_shr = design_sensible / design_total if abs(design_total) > 1e-9 else 0.0

    if design_total <= 0.0:
        raise ValueError("This design case produces no cooling load. Check the design temperatures.")

    notes = [
        "Peak-load estimate uses a steady sol-air temperature for opaque surfaces.",
        "RSHF uses room gains only; the separate outdoor-air ventilation load is added for the design coil load.",
        "Fan power, duct gain and envelope thermal lag are not included.",
    ]
    if inputs.window_area_m2 / gross_wall > 0.5 if gross_wall > 0 else False:
        notes.append("Window-to-wall ratio is high; check solar gain and daylight design.")
    if 1000.0 * outdoor.humidity_ratio < 1000.0 * indoor.humidity_ratio:
        notes.append(
            "Outdoor air is drier than the room, so the outdoor latent component is negative."
        )

    return LoadResult(
        inputs=inputs,
        components=tuple(components),
        room_sensible_kw=room_sensible,
        room_latent_kw=room_latent,
        room_total_kw=room_total,
        room_rshf=room_rshf,
        ventilation_sensible_kw=ventilation_sensible,
        ventilation_latent_kw=ventilation_latent,
        ventilation_total_kw=ventilation_sensible + ventilation_latent,
        design_sensible_kw=design_sensible,
        design_latent_kw=design_latent,
        design_total_kw=design_total,
        design_shr=design_shr,
        design_tr=design_total / TR_KW,
        floor_area_m2=area,
        volume_m3=volume,
        net_wall_area_m2=net_wall,
        gross_wall_area_m2=gross_wall,
        outdoor_state=outdoor,
        indoor_state=indoor,
        ventilation_m3_s=ventilation_flow_m3_s,
        infiltration_m3_s=infiltration_flow_m3_s,
        ventilation_mass_kg_s=ventilation_mass,
        infiltration_mass_kg_s=infiltration_mass,
        notes=tuple(notes),
    )


def load_result_payload(result: LoadResult) -> dict[str, Any]:
    """Compact hand-off dictionary for other modules / diagnostics."""
    return {
        "room_sensible_kw": result.room_sensible_kw,
        "room_latent_kw": result.room_latent_kw,
        "room_rshf": result.room_rshf,
        "design_total_kw": result.design_total_kw,
        "design_tr": result.design_tr,
        "ventilation_m3_s": result.ventilation_m3_s,
        "outdoor_db_c": result.inputs.outdoor_db_c,
        "outdoor_wb_c": result.inputs.outdoor_wb_c,
        "indoor_db_c": result.inputs.indoor_db_c,
        "indoor_rh_pct": result.inputs.indoor_rh_pct,
    }
